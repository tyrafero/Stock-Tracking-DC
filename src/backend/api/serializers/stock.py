from rest_framework import serializers
from django.contrib.auth.models import User
from stock.models import (
    Stock, Category, StockHistory, CommittedStock, StockReservation,
    StockLocation, Store, StockTransfer, UserRole
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""

    class Meta:
        model = Category
        fields = ['id', 'group']


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for Store model"""
    initials = serializers.ReadOnlyField()

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'designation', 'location', 'address', 'email',
            'order_email', 'logo_url', 'website_url', 'facebook_url',
            'instagram_url', 'abn', 'is_active', 'initials'
        ]


class StockLocationSerializer(serializers.ModelSerializer):
    """Serializer for StockLocation model"""
    store = StoreSerializer(read_only=True)
    store_id = serializers.IntegerField(write_only=True)
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = StockLocation
        fields = [
            'id', 'store', 'store_id', 'quantity', 'aisle',
            'last_updated', 'created_at', 'is_low_stock'
        ]


class StockSerializer(serializers.ModelSerializer):
    """Serializer for Stock model"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    location = StoreSerializer(read_only=True)
    location_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    locations = StockLocationSerializer(many=True, read_only=True)

    # Computed properties
    total_stock = serializers.ReadOnlyField()
    committed_stock = serializers.ReadOnlyField()
    reserved_quantity = serializers.ReadOnlyField()
    available_for_sale = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    total_across_locations = serializers.ReadOnlyField()

    # Condition display
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)

    class Meta:
        model = Stock
        fields = [
            'id', 'category', 'category_id', 'item_name', 'sku', 'quantity',
            'receive_quantity', 'received_by', 'issue_quantity', 'issued_by',
            'committed_quantity', 'condition', 'condition_display', 'location',
            'location_id', 'aisle', 'note', 'phone_number', 'created_by',
            're_order', 'last_updated', 'timestamp', 'date', 'export_to_csv',
            'image_url', 'source_purchase_order', 'opening_stock', 'stock_on_hand',
            'warehouse_name', 'locations', 'total_stock', 'committed_stock',
            'reserved_quantity', 'available_for_sale', 'is_low_stock',
            'total_across_locations'
        ]
        read_only_fields = [
            'last_updated', 'timestamp', 'total_stock', 'committed_stock',
            'reserved_quantity', 'available_for_sale', 'is_low_stock',
            'total_across_locations'
        ]

    def validate_quantity(self, value):
        """Validate stock quantity"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_sku(self, value):
        """Validate SKU uniqueness"""
        if value:
            # Check if SKU already exists (excluding current instance during updates)
            queryset = Stock.objects.filter(sku=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError("A stock item with this SKU already exists.")
        return value


class StockHistorySerializer(serializers.ModelSerializer):
    """Serializer for StockHistory model"""
    category = CategorySerializer(read_only=True)

    class Meta:
        model = StockHistory
        fields = [
            'id', 'category', 'item_name', 'quantity', 'receive_quantity',
            'received_by', 'issue_quantity', 'issued_by', 'note', 'phone_number',
            'created_by', 're_order', 'last_updated', 'timestamp'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']


class CommittedStockSerializer(serializers.ModelSerializer):
    """Serializer for CommittedStock model"""
    stock = StockSerializer(read_only=True)
    stock_id = serializers.IntegerField(write_only=True)
    committed_by = UserSerializer(read_only=True)

    class Meta:
        model = CommittedStock
        fields = [
            'id', 'stock', 'stock_id', 'quantity', 'customer_order_number',
            'deposit_amount', 'customer_name', 'customer_phone', 'customer_email',
            'notes', 'committed_by', 'committed_at', 'is_fulfilled', 'fulfilled_at'
        ]
        read_only_fields = ['committed_at', 'fulfilled_at']

    def validate_quantity(self, value):
        """Validate committed quantity"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate(self, data):
        """Validate that stock has enough available quantity"""
        stock_id = data.get('stock_id')
        quantity = data.get('quantity', 0)

        if stock_id and quantity:
            try:
                stock = Stock.objects.get(id=stock_id)
                if stock.available_for_sale < quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock available. Available: {stock.available_for_sale}, Requested: {quantity}"
                    )
            except Stock.DoesNotExist:
                raise serializers.ValidationError("Stock item not found.")

        return data


class StockReservationSerializer(serializers.ModelSerializer):
    """Serializer for StockReservation model"""
    stock = StockSerializer(read_only=True)
    stock_id = serializers.IntegerField(write_only=True)
    reserved_by = UserSerializer(read_only=True)
    fulfilled_by = UserSerializer(read_only=True)
    cancelled_by = UserSerializer(read_only=True)

    # Display fields
    reservation_type_display = serializers.CharField(source='get_reservation_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Computed properties
    is_active = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    can_be_fulfilled = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()

    class Meta:
        model = StockReservation
        fields = [
            'id', 'stock', 'stock_id', 'quantity', 'reservation_type',
            'reservation_type_display', 'status', 'status_display',
            'customer_name', 'customer_phone', 'customer_email',
            'reference_number', 'reason', 'notes', 'reserved_by',
            'reserved_at', 'expires_at', 'fulfilled_at', 'cancelled_at',
            'fulfilled_by', 'cancelled_by', 'is_active', 'is_expired',
            'can_be_fulfilled', 'can_be_cancelled', 'days_until_expiry'
        ]
        read_only_fields = [
            'reserved_at', 'fulfilled_at', 'cancelled_at', 'status',
            'is_active', 'is_expired', 'can_be_fulfilled', 'can_be_cancelled',
            'days_until_expiry'
        ]

    def validate_quantity(self, value):
        """Validate reservation quantity"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_expires_at(self, value):
        """Validate expiry date"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future.")
        return value


class StockTransferSerializer(serializers.ModelSerializer):
    """Serializer for StockTransfer model"""
    stock = StockSerializer(read_only=True)
    stock_id = serializers.IntegerField(write_only=True)
    from_location = StoreSerializer(read_only=True)
    from_location_id = serializers.IntegerField(write_only=True)
    to_location = StoreSerializer(read_only=True)
    to_location_id = serializers.IntegerField(write_only=True)
    created_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    completed_by = UserSerializer(read_only=True)
    collected_by = UserSerializer(read_only=True)

    # Display fields
    transfer_type_display = serializers.CharField(source='get_transfer_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Computed properties
    can_be_approved = serializers.ReadOnlyField()
    can_be_completed = serializers.ReadOnlyField()
    can_be_collected = serializers.ReadOnlyField()
    is_pending_collection = serializers.ReadOnlyField()

    class Meta:
        model = StockTransfer
        fields = [
            'id', 'stock', 'stock_id', 'quantity', 'from_location',
            'from_location_id', 'to_location', 'to_location_id', 'from_aisle',
            'to_aisle', 'transfer_type', 'transfer_type_display', 'transfer_reason',
            'customer_name', 'customer_phone', 'notes', 'status', 'status_display',
            'created_by', 'approved_by', 'completed_by', 'collected_by',
            'created_at', 'approved_at', 'completed_at', 'collected_at',
            'can_be_approved', 'can_be_completed', 'can_be_collected',
            'is_pending_collection'
        ]
        read_only_fields = [
            'status', 'created_at', 'approved_at', 'completed_at', 'collected_at',
            'can_be_approved', 'can_be_completed', 'can_be_collected',
            'is_pending_collection'
        ]

    def validate_quantity(self, value):
        """Validate transfer quantity"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate(self, data):
        """Validate transfer data"""
        from_location_id = data.get('from_location_id')
        to_location_id = data.get('to_location_id')
        stock_id = data.get('stock_id')
        quantity = data.get('quantity', 0)

        # Check that from and to locations are different
        if from_location_id == to_location_id:
            raise serializers.ValidationError("From and to locations must be different.")

        # Check stock availability at from location
        if stock_id and from_location_id and quantity:
            try:
                stock = Stock.objects.get(id=stock_id)
                from_quantity = stock.get_location_quantity(Store.objects.get(id=from_location_id))
                if from_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock at source location. Available: {from_quantity}, Requested: {quantity}"
                    )
            except (Stock.DoesNotExist, Store.DoesNotExist):
                raise serializers.ValidationError("Stock item or location not found.")

        return data


class StockIssueSerializer(serializers.Serializer):
    """Serializer for stock issue operations"""
    quantity = serializers.IntegerField(min_value=1)
    issued_by = serializers.CharField(max_length=50, required=False)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)
    location_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_quantity(self, value):
        """Validate issue quantity against available stock"""
        stock = self.context['stock']
        if value > stock.available_for_sale:
            raise serializers.ValidationError(
                f"Cannot issue {value} units. Only {stock.available_for_sale} available for sale."
            )
        return value


class StockReceiveSerializer(serializers.Serializer):
    """Serializer for stock receive operations"""
    quantity = serializers.IntegerField(min_value=1)
    received_by = serializers.CharField(max_length=50, required=False)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)
    location_id = serializers.IntegerField(required=False, allow_null=True)
    aisle = serializers.CharField(max_length=50, required=False, allow_blank=True)