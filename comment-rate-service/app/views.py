import os
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer


ALLOW_COMMENT_WITHOUT_ORDER_CHECK = os.getenv('ALLOW_COMMENT_WITHOUT_ORDER_CHECK', '0') == '1'

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def create(self, request, *args, **kwargs):
        """Create a comment/rating - verify customer purchased the book"""
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            book_id = serializer.validated_data['book_id']
            
            # Verify customer has purchased this book
            try:
                order_resp = requests.post(
                    'http://order-service:8000/api/orders/verify_purchase/',
                    data={'customer_id': customer_id, 'book_id': book_id},
                    timeout=8,
                )
                if order_resp.status_code == 200:
                    purchase_data = order_resp.json()
                    if not purchase_data.get('purchased'):
                        return Response(
                            {'error': 'You must purchase this book before rating'},
                            status=status.HTTP_403_FORBIDDEN
                        )
                elif not ALLOW_COMMENT_WITHOUT_ORDER_CHECK:
                    return Response(
                        {'error': 'Could not verify purchase. Please try again later.'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )
            except requests.exceptions.RequestException:
                if not ALLOW_COMMENT_WITHOUT_ORDER_CHECK:
                    return Response(
                        {'error': 'Order service unavailable, cannot verify purchase.'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )
            
            comment = serializer.save()
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_book(self, request):
        """Get all comments/reviews for a specific book"""
        book_id = request.query_params.get('book_id')
        if not book_id:
            return Response({'error': 'book_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        comments = Comment.objects.filter(book_id=book_id).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        
        # Calculate average rating
        stats = Comment.objects.filter(book_id=book_id).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        return Response({
            'book_id': book_id,
            'average_rating': stats['avg_rating'] or 0,
            'total_reviews': stats['total_reviews'] or 0,
            'comments': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """Get all comments submitted by a customer"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        comments = Comment.objects.filter(customer_id=customer_id).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        
        return Response({
            'customer_id': customer_id,
            'count': comments.count(),
            'comments': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def book_rating_stats(self, request):
        """Get rating statistics for a book"""
        book_id = request.query_params.get('book_id')
        if not book_id:
            return Response({'error': 'book_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        comments = Comment.objects.filter(book_id=book_id)
        
        # Calculate distribution
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for comment in comments:
            rating_dist[comment.rating] += 1
        
        stats = comments.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        return Response({
            'book_id': book_id,
            'average_rating': round(stats['avg_rating'] or 0, 2),
            'total_reviews': stats['total_reviews'] or 0,
            'rating_distribution': rating_dist,
            'percentage_by_rating': {
                rating: round((count / (stats['total_reviews'] or 1)) * 100, 1)
                for rating, count in rating_dist.items()
            }
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def filter_by_rating(self, request):
        """Get comments filtered by rating"""
        book_id = request.query_params.get('book_id')
        rating = request.query_params.get('rating')
        
        if not book_id or not rating:
            return Response({'error': 'book_id and rating parameters are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return Response({'error': 'rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'rating must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
        
        comments = Comment.objects.filter(book_id=book_id, rating=rating).order_by('-helpful_count')
        serializer = CommentSerializer(comments, many=True)
        
        return Response({
            'book_id': book_id,
            'rating': rating,
            'count': comments.count(),
            'comments': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def mark_helpful(self, request, pk=None):
        """Mark a comment as helpful"""
        comment = self.get_object()
        comment.helpful_count += 1
        comment.save()
        
        return Response({
            'message': 'Comment marked as helpful',
            'comment': CommentSerializer(comment).data
        }, status=status.HTTP_200_OK)
