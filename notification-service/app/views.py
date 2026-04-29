from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Notification, NotificationStatus
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save(status=NotificationStatus.QUEUED)
        return Response({'queued': True, 'data': self.get_serializer(notification).data}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        notif = self.get_object()
        notif.status = NotificationStatus.SENT
        notif.processed_at = timezone.now()
        notif.save(update_fields=['status', 'processed_at'])
        return Response({'sent': True, 'id': notif.id})


@api_view(['GET'])
def health(request):
    return Response({'service': 'notification-service', 'status': 'healthy'})
