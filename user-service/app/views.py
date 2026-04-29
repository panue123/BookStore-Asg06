import requests
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse

from .models import Address, Job, UserAccount, UserRole
from .serializers import AddressSerializer, JobSerializer, UserAccountSerializer


ROLE_PERMISSIONS = {
    UserRole.MANAGER: [
        'users:create', 'users:read', 'users:update', 'users:delete',
        'staff:manage', 'customer:manage', 'reports:view',
    ],
    UserRole.STAFF: [
        'orders:process', 'shipping:process', 'support:assist',
    ],
    UserRole.CUSTOMER: [
        'products:view', 'orders:purchase', 'cart:manage', 'orders:manage_own',
    ],
}


def _role_from_headers(request):
    role = request.headers.get('X-User-Role') or request.META.get('HTTP_X_USER_ROLE') or ''
    return role.strip().lower()


def health(request):
    return JsonResponse({'service': 'user-service', 'status': 'healthy'})


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data.get('role', UserRole.CUSTOMER)
        created = serializer.save(role=role)

        # Create cart for new customers to preserve legacy behavior.
        if created.role == UserRole.CUSTOMER and not created.cart_id:
            try:
                cart_resp = requests.post(
                    'http://cart-service:8000/api/carts/',
                    data={'customer_id': created.id},
                    timeout=5,
                )
                if cart_resp.status_code == 201:
                    created.cart_id = cart_resp.json().get('id')
                    created.save(update_fields=['cart_id'])
            except requests.exceptions.RequestException:
                pass

        return Response({
            'message': 'User created successfully',
            'data': self.get_serializer(created).data,
            'id': created.id,
            'user_id': created.id,
            'customer_id': created.id,
            'cart_id': created.cart_id,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def roles(self, request):
        return Response({
            'roles': [
                {'role': role, 'permissions': perms}
                for role, perms in ROLE_PERMISSIONS.items()
            ]
        })

    @action(detail=False, methods=['post'], url_path='rbac/check')
    def rbac_check(self, request):
        role = (request.data.get('role') or _role_from_headers(request) or '').lower()
        permission = request.data.get('permission', '').strip()
        if not role or not permission:
            return Response({'error': 'role and permission are required'}, status=400)
        allowed = permission in ROLE_PERMISSIONS.get(role, [])
        return Response({'role': role, 'permission': permission, 'allowed': allowed})


class CustomerViewSet(UserAccountViewSet):
    def get_queryset(self):
        return UserAccount.objects.filter(role=UserRole.CUSTOMER)

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        payload['role'] = UserRole.CUSTOMER
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        created = serializer.save(role=UserRole.CUSTOMER)
        return Response({'message': 'User created successfully', 'data': self.get_serializer(created).data, 'id': created.id, 'customer_id': created.id, 'cart_id': created.cart_id}, status=status.HTTP_201_CREATED)


class StaffViewSet(UserAccountViewSet):
    def get_queryset(self):
        return UserAccount.objects.filter(role=UserRole.STAFF)

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        payload['role'] = UserRole.STAFF
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        created = serializer.save(role=UserRole.STAFF)
        return Response({'message': 'User created successfully', 'data': self.get_serializer(created).data, 'id': created.id}, status=status.HTTP_201_CREATED)


class ManagerViewSet(UserAccountViewSet):
    def get_queryset(self):
        return UserAccount.objects.filter(role=UserRole.MANAGER)

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        payload['role'] = UserRole.MANAGER
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        created = serializer.save(role=UserRole.MANAGER)
        return Response({'message': 'User created successfully', 'data': self.get_serializer(created).data, 'id': created.id}, status=status.HTTP_201_CREATED)
