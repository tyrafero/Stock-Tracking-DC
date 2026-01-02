from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from stock.models import PurchaseOrder, PurchaseOrderItem, PurchaseOrderHistory, Stock, StockLocation, Store
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
        try:
            purchase_order = self.get_object()

            if purchase_order.status not in ['sent', 'confirmed', 'partially_received']:
                return Response(
                    {
                        'error': f'Can only receive items from sent or confirmed purchase orders. Current status: {purchase_order.status}. Please send the PO first.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            items_data = request.data.get('items', [])
            delivery_date = request.data.get('delivery_date')
            notes = request.data.get('notes', '')
            receiving_store_id = request.data.get('receiving_store_id')
            aisle = request.data.get('aisle', '')

            # Validate receiving store
            if not receiving_store_id:
                return Response(
                    {'error': 'Receiving store is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                receiving_store = Store.objects.get(id=receiving_store_id)
            except Store.DoesNotExist:
                return Response(
                    {'error': f'Store with id {receiving_store_id} does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process received items
            for item_data in items_data:
                item_id = item_data.get('id')
                received_quantity = item_data.get('received_quantity', 0)

                if received_quantity > 0:
                    try:
                        item = PurchaseOrderItem.objects.get(id=item_id, purchase_order=purchase_order)

                        # Check if receiving would exceed ordered quantity
                        new_received_quantity = item.received_quantity + received_quantity
                        if new_received_quantity > item.quantity:
                            return Response(
                                {'error': f'Cannot receive {received_quantity} of {item.product}. Only {item.quantity - item.received_quantity} remaining to receive.'},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        item.received_quantity = new_received_quantity
                        item.save()

                        # Update stock at receiving location
                        # Find or create stock entry for this product
                        stock, created = Stock.objects.get_or_create(
                            item_name=item.product,
                            defaults={
                                'sku': f'AUTO-{item.product[:20].upper().replace(" ", "-")}',
                                'quantity': 0,
                            }
                        )

                        # Find or create stock location for this store
                        stock_location, location_created = StockLocation.objects.get_or_create(
                            stock=stock,
                            store=receiving_store,
                            defaults={'quantity': 0, 'aisle': aisle}
                        )

                        # Update quantities and aisle
                        stock_location.quantity += received_quantity
                        if aisle:
                            stock_location.aisle = aisle
                        stock_location.save()

                        # Update overall stock quantity
                        stock.quantity += received_quantity
                        stock.save()

                    except PurchaseOrderItem.DoesNotExist:
                        continue

            # Refresh purchase order to get updated item quantities
            purchase_order.refresh_from_db()

            # Update purchase order status based on receiving status
            if purchase_order.overall_receiving_status == 'fully_received':
                purchase_order.status = 'completed'
            elif purchase_order.overall_receiving_status == 'partially_received':
                purchase_order.status = 'partially_received'

            purchase_order.save()

            # Create receiving history record
            history_note = f'Received items at {receiving_store.name}'
            if notes:
                history_note += f'. Notes: {notes}'

            PurchaseOrderHistory.objects.create(
                purchase_order=purchase_order,
                action='updated',
                notes=history_note,
                created_by=request.user
            )

            return Response({
                'message': 'Items received successfully',
                'purchase_order': self.get_serializer(purchase_order).data
            })
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR in receive endpoint: {str(e)}")
            print(error_trace)
            return Response(
                {'error': f'Error receiving items: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

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

    @action(detail=True, methods=['post'], url_path='create-invoice')
    def create_invoice(self, request, pk=None):
        """Create an invoice for a purchase order"""
        from stock.models import Invoice, PurchaseOrderHistory
        from decimal import Decimal
        from datetime import datetime
        from ..serializers.stock import InvoiceSerializer

        purchase_order = self.get_object()

        # Extract data from request
        invoice_number = request.data.get('invoice_number')
        invoice_date = request.data.get('invoice_date')
        due_date = request.data.get('due_date')
        invoice_amount_exc = request.data.get('invoice_amount_exc')
        gst_amount = request.data.get('gst_amount')
        invoice_total = request.data.get('invoice_total')
        notes = request.data.get('notes', '')
        invoice_file = request.FILES.get('invoice_file')

        # Validate required fields
        if not all([invoice_number, invoice_date, due_date, invoice_amount_exc, gst_amount, invoice_total]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert to Decimal for numeric fields
            invoice_amount_exc = Decimal(str(invoice_amount_exc))
            gst_amount = Decimal(str(gst_amount))
            invoice_total = Decimal(str(invoice_total))

            # Convert date strings to date objects
            invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

            # Create invoice
            invoice = Invoice.objects.create(
                purchase_order=purchase_order,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                due_date=due_date,
                invoice_amount_exc=invoice_amount_exc,
                gst_amount=gst_amount,
                invoice_total=invoice_total,
                notes=notes,
                invoice_file=invoice_file,
                created_by=request.user
            )

            # Create history entry
            history_note = f'Invoice {invoice_number} added. Total: ${invoice_total}'
            if notes:
                history_note += f'. Notes: {notes}'

            PurchaseOrderHistory.objects.create(
                purchase_order=purchase_order,
                action='invoice_added',
                notes=history_note,
                created_by=request.user
            )

            # Return invoice data
            return Response(
                InvoiceSerializer(invoice, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR in create_invoice: {str(e)}")
            print(error_trace)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model"""
    permission_classes = [IsAuthenticated]
    filterset_fields = ['purchase_order', 'status']
    search_fields = ['invoice_number']
    ordering_fields = ['invoice_date', 'due_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        from stock.models import Invoice
        return Invoice.objects.select_related(
            'purchase_order', 'created_by'
        ).prefetch_related('payments')

    def get_serializer_class(self):
        from ..serializers.stock import InvoiceSerializer
        return InvoiceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='record-payment')
    def record_payment(self, request, pk=None):
        """Record a payment for this invoice"""
        from stock.models import Payment, PurchaseOrderHistory
        from decimal import Decimal
        from datetime import datetime
        from ..serializers.stock import PaymentSerializer

        invoice = self.get_object()

        # Extract data from request
        payment_reference = request.data.get('payment_reference')
        payment_date = request.data.get('payment_date')
        payment_amount = request.data.get('payment_amount')
        payment_method = request.data.get('payment_method')
        bank_details = request.data.get('bank_details', '')
        notes = request.data.get('notes', '')
        receipt_file = request.FILES.get('receipt_file')

        # Validate required fields
        if not all([payment_reference, payment_date, payment_amount, payment_method]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert to Decimal for payment amount
            payment_amount = Decimal(str(payment_amount))

            # Convert date string to date object
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()

            # Create payment
            payment = Payment.objects.create(
                invoice=invoice,
                payment_reference=payment_reference,
                payment_date=payment_date,
                payment_amount=payment_amount,
                payment_method=payment_method,
                bank_details=bank_details,
                notes=notes,
                receipt_file=receipt_file,
                created_by=request.user
            )

            # Create history entry
            history_note = f'Payment recorded: {payment_reference} - ${payment_amount}'
            if notes:
                history_note += f'. Notes: {notes}'

            PurchaseOrderHistory.objects.create(
                purchase_order=invoice.purchase_order,
                action='payment_recorded',
                notes=history_note,
                created_by=request.user
            )

            # Return payment data
            return Response(
                PaymentSerializer(payment, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR in record_payment: {str(e)}")
            print(error_trace)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model"""
    permission_classes = [IsAuthenticated]
    filterset_fields = ['invoice', 'payment_status', 'payment_method']
    search_fields = ['payment_reference']
    ordering_fields = ['payment_date', 'created_at']
    ordering = ['-payment_date']

    def get_queryset(self):
        from stock.models import Payment
        return Payment.objects.select_related('invoice', 'created_by')

    def get_serializer_class(self):
        from ..serializers.stock import PaymentSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
