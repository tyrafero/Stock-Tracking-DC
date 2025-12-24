import django_filters
from django.db.models import Q
from stock.models import Stock, Category, Store, StockHistory, CommittedStock, StockReservation


class StockFilter(django_filters.FilterSet):
    """
    Filter class for Stock model with advanced filtering options
    """
    # Text filters
    item_name = django_filters.CharFilter(field_name='item_name', lookup_expr='icontains')
    sku = django_filters.CharFilter(field_name='sku', lookup_expr='icontains')
    created_by = django_filters.CharFilter(field_name='created_by', lookup_expr='icontains')

    # Category filters
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    category_name = django_filters.CharFilter(field_name='category__group', lookup_expr='icontains')

    # Location filters
    location = django_filters.ModelChoiceFilter(queryset=Store.objects.all())
    location_name = django_filters.CharFilter(field_name='location__name', lookup_expr='icontains')
    warehouse_name = django_filters.CharFilter(field_name='warehouse_name', lookup_expr='icontains')

    # Quantity filters
    quantity_min = django_filters.NumberFilter(field_name='quantity', lookup_expr='gte')
    quantity_max = django_filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    quantity_exact = django_filters.NumberFilter(field_name='quantity', lookup_expr='exact')

    # Available stock filters
    available_min = django_filters.NumberFilter(method='filter_available_min')
    available_max = django_filters.NumberFilter(method='filter_available_max')

    # Condition filter
    condition = django_filters.ChoiceFilter(choices=Stock.CONDITION_CHOICES)

    # Boolean filters
    has_image = django_filters.BooleanFilter(method='filter_has_image')
    is_low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    has_committed_stock = django_filters.BooleanFilter(method='filter_committed_stock')
    has_reserved_stock = django_filters.BooleanFilter(method='filter_reserved_stock')

    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='last_updated', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='last_updated', lookup_expr='lte')

    # Special filters
    zero_quantity = django_filters.BooleanFilter(method='filter_zero_quantity')
    negative_quantity = django_filters.BooleanFilter(method='filter_negative_quantity')

    class Meta:
        model = Stock
        fields = {
            'quantity': ['exact', 'gte', 'lte', 'gt', 'lt'],
            'condition': ['exact'],
            'export_to_csv': ['exact'],
            're_order': ['exact', 'gte', 'lte'],
        }

    def filter_available_min(self, queryset, name, value):
        """Filter by minimum available quantity (total - committed - reserved)"""
        # This is a simplified version - in practice you might need raw SQL for complex calculations
        return queryset.filter(quantity__gte=value)

    def filter_available_max(self, queryset, name, value):
        """Filter by maximum available quantity"""
        return queryset.filter(quantity__lte=value)

    def filter_has_image(self, queryset, name, value):
        """Filter items that have or don't have images"""
        if value:
            return queryset.exclude(Q(image_url__isnull=True) | Q(image_url__exact=''))
        else:
            return queryset.filter(Q(image_url__isnull=True) | Q(image_url__exact=''))

    def filter_low_stock(self, queryset, name, value):
        """Filter items that are low on stock (quantity <= reorder level)"""
        if value:
            return queryset.filter(quantity__lte=django_filters.F('re_order'))
        else:
            return queryset.filter(quantity__gt=django_filters.F('re_order'))

    def filter_committed_stock(self, queryset, name, value):
        """Filter items that have or don't have committed stock"""
        if value:
            return queryset.filter(committed_quantity__gt=0)
        else:
            return queryset.filter(Q(committed_quantity__isnull=True) | Q(committed_quantity=0))

    def filter_reserved_stock(self, queryset, name, value):
        """Filter items that have active reservations"""
        from django.utils import timezone
        if value:
            return queryset.filter(
                reservations__status='active',
                reservations__expires_at__gt=timezone.now()
            ).distinct()
        else:
            # Items without active reservations
            active_reservation_ids = Stock.objects.filter(
                reservations__status='active',
                reservations__expires_at__gt=timezone.now()
            ).values_list('id', flat=True).distinct()
            return queryset.exclude(id__in=active_reservation_ids)

    def filter_zero_quantity(self, queryset, name, value):
        """Filter items with zero quantity"""
        if value:
            return queryset.filter(Q(quantity=0) | Q(quantity__isnull=True))
        else:
            return queryset.filter(quantity__gt=0)

    def filter_negative_quantity(self, queryset, name, value):
        """Filter items with negative quantity"""
        if value:
            return queryset.filter(quantity__lt=0)
        else:
            return queryset.filter(quantity__gte=0)


class StockHistoryFilter(django_filters.FilterSet):
    """
    Filter class for StockHistory model
    """
    item_name = django_filters.CharFilter(field_name='item_name', lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    received_by = django_filters.CharFilter(field_name='received_by', lookup_expr='icontains')
    issued_by = django_filters.CharFilter(field_name='issued_by', lookup_expr='icontains')
    created_by = django_filters.CharFilter(field_name='created_by', lookup_expr='icontains')
    note = django_filters.CharFilter(field_name='note', lookup_expr='icontains')

    # Date filters
    date_from = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    # Operation type filters
    received_only = django_filters.BooleanFilter(method='filter_received_only')
    issued_only = django_filters.BooleanFilter(method='filter_issued_only')

    class Meta:
        model = StockHistory
        fields = [
            'category', 'received_by', 'issued_by', 'created_by',
            'receive_quantity', 'issue_quantity'
        ]

    def filter_received_only(self, queryset, name, value):
        """Filter only stock received operations"""
        if value:
            return queryset.filter(receive_quantity__gt=0)
        return queryset

    def filter_issued_only(self, queryset, name, value):
        """Filter only stock issued operations"""
        if value:
            return queryset.filter(issue_quantity__gt=0)
        return queryset


class CommittedStockFilter(django_filters.FilterSet):
    """
    Filter class for CommittedStock model
    """
    customer_name = django_filters.CharFilter(field_name='customer_name', lookup_expr='icontains')
    customer_order_number = django_filters.CharFilter(field_name='customer_order_number', lookup_expr='icontains')
    stock_item = django_filters.CharFilter(field_name='stock__item_name', lookup_expr='icontains')
    stock_sku = django_filters.CharFilter(field_name='stock__sku', lookup_expr='icontains')
    is_fulfilled = django_filters.BooleanFilter()
    committed_by = django_filters.CharFilter(field_name='committed_by__username', lookup_expr='icontains')

    # Date filters
    committed_after = django_filters.DateTimeFilter(field_name='committed_at', lookup_expr='gte')
    committed_before = django_filters.DateTimeFilter(field_name='committed_at', lookup_expr='lte')

    # Amount filters
    deposit_min = django_filters.NumberFilter(field_name='deposit_amount', lookup_expr='gte')
    deposit_max = django_filters.NumberFilter(field_name='deposit_amount', lookup_expr='lte')

    class Meta:
        model = CommittedStock
        fields = [
            'stock', 'is_fulfilled', 'committed_by', 'quantity',
            'customer_name', 'customer_order_number'
        ]


class StockReservationFilter(django_filters.FilterSet):
    """
    Filter class for StockReservation model
    """
    customer_name = django_filters.CharFilter(field_name='customer_name', lookup_expr='icontains')
    reference_number = django_filters.CharFilter(field_name='reference_number', lookup_expr='icontains')
    stock_item = django_filters.CharFilter(field_name='stock__item_name', lookup_expr='icontains')
    stock_sku = django_filters.CharFilter(field_name='stock__sku', lookup_expr='icontains')
    reservation_type = django_filters.ChoiceFilter(choices=StockReservation.RESERVATION_TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=StockReservation.STATUS_CHOICES)
    reserved_by = django_filters.CharFilter(field_name='reserved_by__username', lookup_expr='icontains')

    # Date filters
    reserved_after = django_filters.DateTimeFilter(field_name='reserved_at', lookup_expr='gte')
    reserved_before = django_filters.DateTimeFilter(field_name='reserved_at', lookup_expr='lte')
    expires_after = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='gte')
    expires_before = django_filters.DateTimeFilter(field_name='expires_at', lookup_expr='lte')

    # Special filters
    active_only = django_filters.BooleanFilter(method='filter_active_only')
    expired_only = django_filters.BooleanFilter(method='filter_expired_only')
    expiring_soon = django_filters.NumberFilter(method='filter_expiring_soon')

    class Meta:
        model = StockReservation
        fields = [
            'stock', 'reservation_type', 'status', 'reserved_by',
            'customer_name', 'reference_number'
        ]

    def filter_active_only(self, queryset, name, value):
        """Filter only active reservations"""
        if value:
            from django.utils import timezone
            return queryset.filter(status='active', expires_at__gt=timezone.now())
        return queryset

    def filter_expired_only(self, queryset, name, value):
        """Filter only expired reservations"""
        if value:
            from django.utils import timezone
            return queryset.filter(status='active', expires_at__lte=timezone.now())
        return queryset

    def filter_expiring_soon(self, queryset, name, value):
        """Filter reservations expiring within X days"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            cutoff_date = timezone.now() + timedelta(days=value)
            return queryset.filter(
                status='active',
                expires_at__lte=cutoff_date,
                expires_at__gt=timezone.now()
            )
        return queryset