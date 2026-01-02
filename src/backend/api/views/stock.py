from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Sum, F
from django.db import models

from stock.models import (
    Stock, Category, StockHistory, CommittedStock, StockReservation,
    StockLocation, Store, StockTransfer, Manufacturer, DeliveryPerson
)
from ..serializers.stock import (
    StockSerializer, CategorySerializer, StockHistorySerializer,
    CommittedStockSerializer, StockReservationSerializer, StockLocationSerializer,
    StockTransferSerializer, StoreSerializer, StockIssueSerializer,
    StockReceiveSerializer, ManufacturerSerializer, DeliveryPersonSerializer
)
from ..permissions import (
    StockPermissions, TransferPermissions, CommittedStockPermissions,
    ReservationPermissions, ViewOnlyPermission
)
from ..filters import (
    StockFilter, StockHistoryFilter, CommittedStockFilter, StockReservationFilter
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['group']
    ordering_fields = ['group', 'id']
    ordering = ['group']


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing stores/locations
    """
    queryset = Store.objects.filter(is_active=True)
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'location', 'designation']
    ordering_fields = ['name', 'designation', 'location']
    ordering = ['name']
    filterset_fields = ['designation', 'is_active']


class ManufacturerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing manufacturers/suppliers
    """
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name', 'company_email', 'city', 'country']
    ordering_fields = ['company_name', 'created_at', 'updated_at']
    ordering = ['company_name']


class DeliveryPersonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing delivery persons
    """
    queryset = DeliveryPerson.objects.filter(is_active=True)
    serializer_class = DeliveryPersonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone_number']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class StockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock items

    Provides standard CRUD operations plus custom actions:
    - issue: Issue stock (reduce quantity)
    - receive: Receive stock (increase quantity)
    - reserve: Create stock reservation
    - commit: Commit stock with deposit
    """
    queryset = Stock.objects.select_related('category', 'location').prefetch_related('locations')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated, StockPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StockFilter
    search_fields = ['item_name', 'sku', 'note', 'warehouse_name']
    ordering_fields = [
        'item_name', 'sku', 'quantity', 'last_updated', 'timestamp',
        'condition', 'location__name', 'category__group'
    ]
    ordering = ['-last_updated']

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        queryset = super().get_queryset()

        # Apply role-based filtering if needed
        if hasattr(user, 'role') and user.role.role == 'warehouse_boy':
            # Warehouse boys can only view stock, not modify
            pass

        return queryset

    def perform_create(self, serializer):
        """Set created_by field when creating stock and create stock location if specified"""
        stock = serializer.save(created_by=self.request.user.username)

        # Create stock location entry if location was specified
        if stock.location and stock.quantity and stock.quantity > 0:
            from stock.models import StockLocation
            StockLocation.objects.get_or_create(
                stock=stock,
                store=stock.location,
                defaults={
                    'quantity': stock.quantity,
                    'aisle': stock.aisle or ''
                }
            )

    def perform_update(self, serializer):
        """Track who last updated the stock"""
        serializer.save(created_by=self.request.user.username)

    @action(detail=True, methods=['post'], url_path='issue')
    def issue_stock(self, request, pk=None):
        """
        Issue stock (reduce quantity)

        POST /api/v1/stock/{id}/issue/
        Body: {
            "quantity": 5,
            "issued_by": "John Doe",
            "note": "Issued for customer order",
            "location_id": 1  # optional
        }
        """
        stock = self.get_object()
        serializer = StockIssueSerializer(data=request.data, context={'stock': stock})

        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            issued_by = serializer.validated_data.get('issued_by', request.user.username)
            note = serializer.validated_data.get('note', '')
            location_id = serializer.validated_data.get('location_id')

            # Issue from specific location if provided
            if location_id:
                try:
                    location = Store.objects.get(id=location_id)
                    if not stock.remove_from_location(location, quantity):
                        return Response({
                            'error': f'Not enough stock at {location.name}. Available: {stock.get_location_quantity(location)}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Store.DoesNotExist:
                    return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Issue from main stock quantity
                stock.quantity = max(0, (stock.quantity or 0) - quantity)

            # Update issue tracking fields
            stock.issue_quantity = (stock.issue_quantity or 0) + quantity
            stock.issued_by = issued_by
            stock.note = note
            stock.save()

            return Response({
                'message': f'Successfully issued {quantity} units',
                'new_quantity': stock.quantity,
                'available_for_sale': stock.available_for_sale
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='receive')
    def receive_stock(self, request, pk=None):
        """
        Receive stock (increase quantity)

        POST /api/v1/stock/{id}/receive/
        Body: {
            "quantity": 10,
            "received_by": "Jane Smith",
            "note": "Received from supplier",
            "location_id": 1,  # optional
            "aisle": "A1"      # optional
        }
        """
        stock = self.get_object()
        serializer = StockReceiveSerializer(data=request.data)

        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            received_by = serializer.validated_data.get('received_by', request.user.username)
            note = serializer.validated_data.get('note', '')
            location_id = serializer.validated_data.get('location_id')
            aisle = serializer.validated_data.get('aisle')

            # Receive to specific location if provided
            if location_id:
                try:
                    location = Store.objects.get(id=location_id)
                    stock.add_to_location(location, quantity, aisle)
                except Store.DoesNotExist:
                    return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Add to main stock quantity
                stock.quantity = (stock.quantity or 0) + quantity

            # Update receive tracking fields
            stock.receive_quantity = (stock.receive_quantity or 0) + quantity
            stock.received_by = received_by
            stock.note = note
            if aisle:
                stock.aisle = aisle
            stock.save()

            return Response({
                'message': f'Successfully received {quantity} units',
                'new_quantity': stock.quantity,
                'available_for_sale': stock.available_for_sale
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reserve')
    def reserve_stock(self, request, pk=None):
        """
        Create a stock reservation

        POST /api/v1/stock/{id}/reserve/
        """
        stock = self.get_object()
        serializer = StockReservationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                stock=stock,
                reserved_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='commit')
    def commit_stock(self, request, pk=None):
        """
        Commit stock with customer deposit

        POST /api/v1/stock/{id}/commit/
        """
        stock = self.get_object()
        serializer = CommittedStockSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                stock=stock,
                committed_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='history')
    def stock_history(self, request, pk=None):
        """
        Get stock movement history

        GET /api/v1/stock/{id}/history/
        """
        stock = self.get_object()
        history = StockHistory.objects.filter(item_name=stock.item_name).order_by('-timestamp')
        serializer = StockHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='locations')
    def stock_locations(self, request, pk=None):
        """
        Get stock quantities by location

        GET /api/v1/stock/{id}/locations/
        """
        stock = self.get_object()
        locations = stock.locations.all()
        serializer = StockLocationSerializer(locations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """
        Get stock items that are low on inventory

        GET /api/v1/stock/low-stock/
        """
        queryset = self.get_queryset().filter(
            Q(quantity__lte=models.F('re_order')) |
            Q(quantity__isnull=True) |
            Q(quantity=0)
        ).order_by('quantity', 'item_name')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-condition')
    def by_condition(self, request):
        """
        Get stock grouped by condition

        GET /api/v1/stock/by-condition/
        """
        from django.db.models import Count, Sum

        conditions = Stock.objects.values('condition').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        ).order_by('condition')

        return Response(conditions)


class StockHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing stock history
    """
    queryset = StockHistory.objects.all()
    serializer_class = StockHistorySerializer
    permission_classes = [IsAuthenticated, ViewOnlyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['item_name', 'note', 'received_by', 'issued_by', 'created_by']
    ordering_fields = ['timestamp', 'last_updated', 'item_name']
    ordering = ['-timestamp']
    filterset_fields = ['category', 'received_by', 'issued_by', 'created_by']


class CommittedStockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing committed stock
    """
    queryset = CommittedStock.objects.select_related('stock', 'committed_by')
    serializer_class = CommittedStockSerializer
    permission_classes = [IsAuthenticated, CommittedStockPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer_name', 'customer_order_number', 'stock__item_name']
    ordering_fields = ['committed_at', 'customer_name', 'deposit_amount']
    ordering = ['-committed_at']
    filterset_fields = ['is_fulfilled', 'stock', 'committed_by']

    def perform_create(self, serializer):
        """Set committed_by field when creating commitment"""
        serializer.save(committed_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='fulfill')
    def fulfill_commitment(self, request, pk=None):
        """
        Fulfill a stock commitment

        POST /api/v1/committed-stock/{id}/fulfill/
        """
        commitment = self.get_object()

        if commitment.is_fulfilled:
            return Response({'error': 'Commitment is already fulfilled'},
                          status=status.HTTP_400_BAD_REQUEST)

        commitment.is_fulfilled = True
        commitment.fulfilled_at = timezone.now()
        commitment.save()

        # Update stock committed quantity
        stock = commitment.stock
        stock.committed_quantity = stock.commitments.filter(is_fulfilled=False).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        stock.save(update_fields=['committed_quantity'])

        return Response({
            'message': 'Commitment fulfilled successfully',
            'commitment': CommittedStockSerializer(commitment).data
        })


class StockReservationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock reservations
    """
    queryset = StockReservation.objects.select_related('stock', 'reserved_by', 'fulfilled_by', 'cancelled_by')
    serializer_class = StockReservationSerializer
    permission_classes = [IsAuthenticated, ReservationPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer_name', 'reference_number', 'stock__item_name', 'reason']
    ordering_fields = ['reserved_at', 'expires_at', 'customer_name']
    ordering = ['-reserved_at']
    filterset_fields = ['status', 'reservation_type', 'stock', 'reserved_by']

    def perform_create(self, serializer):
        """Set reserved_by field when creating reservation"""
        serializer.save(reserved_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='fulfill')
    def fulfill_reservation(self, request, pk=None):
        """
        Fulfill a stock reservation

        POST /api/v1/reservations/{id}/fulfill/
        """
        reservation = self.get_object()

        if reservation.fulfill(request.user):
            return Response({
                'message': 'Reservation fulfilled successfully',
                'reservation': StockReservationSerializer(reservation).data
            })

        return Response({'error': 'Reservation cannot be fulfilled'},
                      status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_reservation(self, request, pk=None):
        """
        Cancel a stock reservation

        POST /api/v1/reservations/{id}/cancel/
        """
        reservation = self.get_object()

        if reservation.cancel(request.user):
            return Response({
                'message': 'Reservation cancelled successfully',
                'reservation': StockReservationSerializer(reservation).data
            })

        return Response({'error': 'Reservation cannot be cancelled'},
                      status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='active')
    def active_reservations(self, request):
        """
        Get active reservations

        GET /api/v1/reservations/active/
        """
        queryset = self.get_queryset().filter(
            status='active',
            expires_at__gt=timezone.now()
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='expired')
    def expired_reservations(self, request):
        """
        Get expired reservations

        GET /api/v1/reservations/expired/
        """
        queryset = self.get_queryset().filter(
            status='active',
            expires_at__lte=timezone.now()
        )

        # Auto-expire them
        for reservation in queryset:
            reservation.expire()

        # Refresh and serialize
        queryset = queryset.filter(status='expired')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StockTransferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock transfers
    """
    queryset = StockTransfer.objects.select_related(
        'stock', 'from_location', 'to_location', 'created_by', 'approved_by'
    )
    serializer_class = StockTransferSerializer
    permission_classes = [IsAuthenticated, TransferPermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['stock__item_name', 'transfer_reason', 'customer_name']
    ordering_fields = ['created_at', 'completed_at', 'transfer_type', 'status']
    ordering = ['-created_at']
    filterset_fields = ['status', 'transfer_type', 'from_location', 'to_location', 'created_by']

    def perform_create(self, serializer):
        """Set created_by field when creating transfer"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_transfer(self, request, pk=None):
        """
        Approve a stock transfer

        POST /api/v1/transfers/{id}/approve/
        """
        transfer = self.get_object()

        if transfer.can_be_approved():
            transfer.approve(request.user)
            return Response({
                'message': 'Transfer approved successfully',
                'transfer': StockTransferSerializer(transfer).data
            })

        return Response({'error': 'Transfer cannot be approved'},
                      status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_transfer(self, request, pk=None):
        """
        Complete a stock transfer

        POST /api/v1/transfers/{id}/complete/
        """
        transfer = self.get_object()

        if transfer.can_be_completed():
            transfer.complete(request.user)
            return Response({
                'message': 'Transfer completed successfully',
                'transfer': StockTransferSerializer(transfer).data
            })

        return Response({'error': 'Transfer cannot be completed'},
                      status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='collect')
    def mark_collected(self, request, pk=None):
        """
        Mark transfer as collected (for customer collections)

        POST /api/v1/transfers/{id}/collect/
        """
        transfer = self.get_object()

        if transfer.can_be_collected():
            transfer.mark_collected(request.user)
            return Response({
                'message': 'Transfer marked as collected',
                'transfer': StockTransferSerializer(transfer).data
            })

        return Response({'error': 'Transfer cannot be marked as collected'},
                      status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_transfers(self, request):
        """
        Get pending transfers

        GET /api/v1/transfers/pending/
        """
        queryset = self.get_queryset().filter(status='pending')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='awaiting-collection')
    def awaiting_collection(self, request):
        """
        Get transfers awaiting customer collection

        GET /api/v1/transfers/awaiting-collection/
        """
        queryset = self.get_queryset().filter(status='awaiting_collection')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class StockLocationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing stock locations and their aisles"""
    queryset = StockLocation.objects.select_related('stock', 'store')
    serializer_class = StockLocationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options']  # Only allow GET and PATCH

    def get_queryset(self):
        """Optionally filter by stock_id"""
        queryset = super().get_queryset()
        stock_id = self.request.query_params.get('stock_id')
        if stock_id:
            queryset = queryset.filter(stock_id=stock_id)
        return queryset
