from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from stock.models import PurchaseOrder, PurchaseOrderItem
from ..serializers.stock import PurchaseOrderSerializer, PurchaseOrderItemSerializer
from ..permissions import PurchaseOrderPermissions


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for PurchaseOrder model"""
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, PurchaseOrderPermissions]
    filterset_fields = ['status', 'manufacturer']
    search_fields = ['reference_number', 'manufacturer__name', 'manufacturer__email']
    ordering_fields = ['created_at', 'updated_at', 'reference_number']
    ordering = ['-created_at']

    def get_queryset(self):
        return PurchaseOrder.objects.select_related(
            'created_by', 'manufacturer', 'delivery_person', 'store', 'creating_store'
        ).prefetch_related('items')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send purchase order to supplier"""
        purchase_order = self.get_object()

        if purchase_order.status != 'draft':
            return Response(
                {'error': 'Only draft purchase orders can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )

        purchase_order.status = 'sent'
        purchase_order.sent_by = request.user
        from django.utils import timezone
        purchase_order.sent_at = timezone.now()
        purchase_order.save()

        return Response({
            'message': 'Purchase order sent successfully',
            'purchase_order': self.get_serializer(purchase_order).data
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve purchase order"""
        purchase_order = self.get_object()

        if purchase_order.status != 'sent':
            return Response(
                {'error': 'Only sent purchase orders can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        purchase_order.status = 'confirmed'
        purchase_order.approved_by = request.user
        from django.utils import timezone
        purchase_order.approved_at = timezone.now()
        purchase_order.save()

        return Response({
            'message': 'Purchase order approved successfully',
            'purchase_order': self.get_serializer(purchase_order).data
        })

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Receive purchase order items"""
        purchase_order = self.get_object()

        if purchase_order.status not in ['confirmed', 'partially_received']:
            return Response(
                {'error': 'Can only receive items from confirmed purchase orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        items_data = request.data.get('items', [])
        delivery_date = request.data.get('delivery_date')
        notes = request.data.get('notes', '')

        for item_data in items_data:
            item_id = item_data.get('id')
            received_quantity = item_data.get('received_quantity', 0)

            if received_quantity > 0:
                try:
                    item = PurchaseOrderItem.objects.get(id=item_id, purchase_order=purchase_order)
                    item.received_quantity += received_quantity
                    item.save()
                except PurchaseOrderItem.DoesNotExist:
                    continue

        # Update purchase order status
        if purchase_order.is_fully_received:
            purchase_order.status = 'received'
            purchase_order.received_by = request.user
            from django.utils import timezone
            purchase_order.received_at = timezone.now()
        else:
            purchase_order.status = 'partially_received'

        if delivery_date:
            purchase_order.delivery_date = delivery_date

        purchase_order.save()

        return Response({
            'message': 'Items received successfully',
            'purchase_order': self.get_serializer(purchase_order).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel purchase order"""
        purchase_order = self.get_object()

        if purchase_order.status in ['received', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel received or already cancelled purchase orders'},
                status=status.HTTP_400_BAD_REQUEST
            )

        purchase_order.status = 'cancelled'
        purchase_order.save()

        return Response({
            'message': 'Purchase order cancelled successfully',
            'purchase_order': self.get_serializer(purchase_order).data
        })