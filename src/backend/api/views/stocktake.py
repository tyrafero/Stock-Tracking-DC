from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from stock.models import StockAudit, StockAuditItem
from ..serializers.stock import StockAuditSerializer, StockAuditListSerializer, StockAuditItemSerializer
from ..permissions import StockPermissions


class StockAuditViewSet(viewsets.ModelViewSet):
    """ViewSet for StockAudit model"""
    serializer_class = StockAuditSerializer
    permission_classes = [IsAuthenticated, StockPermissions]
    filterset_fields = ['status', 'audit_type']
    search_fields = ['audit_reference', 'title', 'description']
    ordering_fields = ['created_at', 'planned_start_date', 'planned_end_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use lightweight serializer to avoid loading all audit items"""
        # Always use list serializer since we fetch items separately via /items/ endpoint
        return StockAuditListSerializer

    def get_queryset(self):
        """Optimize queryset - never prefetch audit_items (fetched separately via /items/)"""
        return StockAudit.objects.select_related(
            'created_by', 'approved_by'
        ).prefetch_related(
            'assigned_auditors', 'audit_locations', 'audit_categories'
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start stock audit"""
        audit = self.get_object()

        if not audit.can_start():
            return Response(
                {'error': 'Audit cannot be started'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if audit.start_audit(request.user):
            return Response({
                'message': 'Stock audit started successfully',
                'audit': self.get_serializer(audit).data
            })
        else:
            return Response(
                {'error': 'Failed to start audit'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete stock audit"""
        audit = self.get_object()

        if not audit.can_complete():
            return Response(
                {'error': 'Audit cannot be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if audit.complete_audit(request.user):
            return Response({
                'message': 'Stock audit completed successfully',
                'audit': self.get_serializer(audit).data
            })
        else:
            return Response(
                {'error': 'Failed to complete audit'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve stock audit"""
        audit = self.get_object()

        if audit.status != 'completed':
            return Response(
                {'error': 'Only completed audits can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if audit.approve_audit(request.user):
            return Response({
                'message': 'Stock audit approved successfully',
                'audit': self.get_serializer(audit).data
            })
        else:
            return Response(
                {'error': 'Failed to approve audit'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel stock audit"""
        audit = self.get_object()

        if audit.status in ['completed', 'approved']:
            return Response(
                {'error': 'Cannot cancel completed or approved audits'},
                status=status.HTTP_400_BAD_REQUEST
            )

        audit.status = 'cancelled'
        audit.save()

        return Response({
            'message': 'Stock audit cancelled successfully',
            'audit': self.get_serializer(audit).data
        })

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get paginated audit items for a stocktake"""
        audit = self.get_object()

        # Get query parameters for pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))

        # Get all items for this audit
        items = StockAuditItem.objects.filter(audit=audit).select_related(
            'stock', 'counted_by'
        ).order_by('id')

        # Calculate pagination
        total_items = items.count()
        total_pages = (total_items + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        # Get paginated items
        paginated_items = items[start_idx:end_idx]

        return Response({
            'results': StockAuditItemSerializer(paginated_items, many=True).data,
            'count': total_items,
            'current_page': page,
            'total_pages': total_pages,
            'page_size': page_size,
        })

    @action(detail=True, methods=['post'])
    def count_item(self, request, pk=None):
        """Count a specific item in the audit"""
        audit = self.get_object()

        if audit.status != 'in_progress':
            return Response(
                {'error': 'Can only count items in active audits'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item_id = request.data.get('item_id')
        counted_quantity = request.data.get('counted_quantity')
        notes = request.data.get('notes', '')

        if item_id is None or counted_quantity is None:
            return Response(
                {'error': 'item_id and counted_quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            audit_item = StockAuditItem.objects.get(
                id=item_id,
                audit=audit
            )
        except StockAuditItem.DoesNotExist:
            return Response(
                {'error': 'Audit item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update the audit item
        from django.utils import timezone
        audit_item.physical_count = counted_quantity
        audit_item.variance_notes = notes
        audit_item.counted_by = request.user
        audit_item.count_date = timezone.now()
        audit_item.save()

        # Update audit statistics (total_items_counted, items_with_variances, etc.)
        audit.update_statistics()
        audit.save()

        return Response({
            'message': 'Item counted successfully',
            'audit_item': StockAuditItemSerializer(audit_item).data
        })