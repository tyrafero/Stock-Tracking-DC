from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from stock.models import StockAudit, StockAuditItem
from ..serializers.stock import StockAuditSerializer, StockAuditItemSerializer
from ..permissions import StockPermissions


class StockAuditViewSet(viewsets.ModelViewSet):
    """ViewSet for StockAudit model"""
    serializer_class = StockAuditSerializer
    permission_classes = [IsAuthenticated, StockPermissions]
    filterset_fields = ['status', 'audit_type']
    search_fields = ['audit_reference', 'title', 'description']
    ordering_fields = ['created_at', 'planned_start_date', 'planned_end_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return StockAudit.objects.select_related(
            'created_by', 'approved_by'
        ).prefetch_related(
            'assigned_auditors', 'audit_locations', 'audit_categories', 'audit_items'
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
                stock_audit=audit
            )
        except StockAuditItem.DoesNotExist:
            return Response(
                {'error': 'Audit item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update the audit item
        from django.utils import timezone
        audit_item.counted_quantity = counted_quantity
        audit_item.notes = notes
        audit_item.counted_by = request.user
        audit_item.counted_at = timezone.now()
        audit_item.save()

        return Response({
            'message': 'Item counted successfully',
            'audit_item': StockAuditItemSerializer(audit_item).data
        })