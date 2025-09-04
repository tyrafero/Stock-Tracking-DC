from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Stock, Category, Country, State, City, Person, Contacts, Product, 
    PurchaseOrder, PurchaseOrderItem, Manufacturer, DeliveryPerson, Store, 
    PurchaseOrderHistory, CommittedStock, StockTransfer, StockLocation, UserRole,
    StockReservation, StockAudit, StockAuditItem
)
from .form import StockCreateForm  # Make sure this is the correct import path

# Inline admin for PurchaseOrder
class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ('product', 'quantity', 'price_inc', 'discount_percent', 'subtotal_exc')

class PurchaseOrderHistoryInline(admin.TabularInline):
    model = PurchaseOrderHistory
    extra = 0
    fields = ('action', 'notes', 'created_by', 'created_at')
    readonly_fields = ('action', 'notes', 'created_by', 'created_at')

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'manufacturer', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'manufacturer')
    search_fields = ('reference_number',)
    inlines = [PurchaseOrderItemInline, PurchaseOrderHistoryInline]

# CommittedStock Inline for Stock Admin
class CommittedStockInline(admin.TabularInline):
    model = CommittedStock
    extra = 0
    fields = ('quantity', 'customer_order_number', 'deposit_amount', 'customer_name', 'is_fulfilled')
    readonly_fields = ('committed_at',)

# Stock Location Inline for Stock Admin
class StockLocationInline(admin.TabularInline):
    model = StockLocation
    extra = 0
    fields = ('store', 'quantity', 'aisle', 'last_updated')
    readonly_fields = ('last_updated',)

# Stock Transfer Inline for Stock Admin
class StockTransferInline(admin.TabularInline):
    model = StockTransfer
    extra = 0
    fields = ('quantity', 'from_location', 'to_location', 'status', 'created_by')
    readonly_fields = ('created_by', 'created_at')

# Stock Admin
class StockAdmin(admin.ModelAdmin):
    list_display = ['category', 'item_name', 'quantity', 'committed_quantity', 'condition', 'location', 'aisle']
    form = StockCreateForm
    list_filter = ['category', 'condition', 'location']
    search_fields = ['category', 'item_name', 'location__name', 'aisle']
    inlines = [StockLocationInline, CommittedStockInline, StockTransferInline]

# CommittedStock Admin
@admin.register(CommittedStock)
class CommittedStockAdmin(admin.ModelAdmin):
    list_display = ('stock', 'quantity', 'customer_name', 'customer_order_number', 'deposit_amount', 'is_fulfilled', 'committed_at')
    list_filter = ('is_fulfilled', 'committed_at')
    search_fields = ('customer_name', 'customer_order_number', 'stock__item_name')
    readonly_fields = ('committed_at', 'fulfilled_at')

admin.site.register(Stock, StockAdmin)
admin.site.register(Category)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Person)
admin.site.register(Contacts)

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_price_inc', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)

# Manufacturer Admin
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_email', 'company_telephone')
    search_fields = ('company_name', 'company_email')

# Delivery Person Admin
@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'is_active')
    list_filter = ('is_active',)

# Store Admin
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'location', 'is_active')
    list_filter = ('designation', 'is_active')
    fields = ('name', 'designation', 'location', 'address', 'email', 'logo', 'is_active')

# StockLocation Admin
@admin.register(StockLocation)
class StockLocationAdmin(admin.ModelAdmin):
    list_display = ('stock', 'store', 'quantity', 'aisle', 'last_updated')
    list_filter = ('store', 'last_updated')
    search_fields = ('stock__item_name', 'store__name')

# StockTransfer Admin
@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('stock', 'from_location', 'to_location', 'quantity', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'from_location', 'to_location', 'created_at')
    readonly_fields = ('created_at', 'approved_at', 'completed_at')
    search_fields = ('stock__item_name', 'transfer_reason')

# UserRole Admin
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username',)

# StockReservation Admin
@admin.register(StockReservation)
class StockReservationAdmin(admin.ModelAdmin):
    list_display = ('stock', 'quantity', 'customer_name', 'reservation_type', 'status', 'expires_at', 'reserved_by', 'reserved_at')
    list_filter = ('status', 'reservation_type', 'expires_at', 'reserved_at')
    search_fields = ('stock__item_name', 'customer_name', 'reference_number')
    readonly_fields = ('reserved_at', 'fulfilled_at', 'cancelled_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('stock', 'reserved_by', 'fulfilled_by', 'cancelled_by')

# Stock Audit Admin
class StockAuditItemInline(admin.TabularInline):
    model = StockAuditItem
    fields = ('stock', 'system_quantity', 'physical_count', 'variance_quantity', 'counted_by', 'variance_reason')
    readonly_fields = ('variance_quantity',)
    extra = 0

@admin.register(StockAudit)
class StockAuditAdmin(admin.ModelAdmin):
    list_display = ('audit_reference', 'title', 'audit_type', 'status', 'planned_start_date', 'completion_percentage', 'items_with_variances', 'created_by')
    list_filter = ('audit_type', 'status', 'planned_start_date', 'created_at')
    search_fields = ('audit_reference', 'title', 'description')
    readonly_fields = ('total_items_planned', 'total_items_counted', 'items_with_variances', 'total_variance_value', 'completion_percentage', 'created_at', 'updated_at')
    filter_horizontal = ('audit_locations', 'audit_categories', 'assigned_auditors')
    inlines = [StockAuditItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('audit_reference', 'title', 'description', 'audit_type', 'status')
        }),
        ('Scope', {
            'fields': ('audit_locations', 'audit_categories')
        }),
        ('Schedule', {
            'fields': ('planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Personnel', {
            'fields': ('created_by', 'assigned_auditors', 'approved_by')
        }),
        ('Results Summary', {
            'fields': ('total_items_planned', 'total_items_counted', 'items_with_variances', 'total_variance_value', 'completion_percentage'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'approved_by')

@admin.register(StockAuditItem)
class StockAuditItemAdmin(admin.ModelAdmin):
    list_display = ('audit', 'stock', 'system_quantity', 'physical_count', 'variance_quantity', 'variance_percentage', 'counted_by', 'adjustment_applied')
    list_filter = ('audit__status', 'variance_reason', 'adjustment_applied', 'count_date')
    search_fields = ('audit__audit_reference', 'stock__item_name')
    readonly_fields = ('variance_quantity', 'variance_percentage', 'count_date', 'adjustment_date')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('audit', 'stock')
        }),
        ('System Data', {
            'fields': ('system_quantity', 'committed_quantity', 'reserved_quantity')
        }),
        ('Physical Count', {
            'fields': ('physical_count', 'variance_quantity', 'variance_percentage', 'counted_by', 'count_date')
        }),
        ('Variance Analysis', {
            'fields': ('variance_reason', 'variance_notes'),
            'classes': ('collapse',)
        }),
        ('Adjustment', {
            'fields': ('adjustment_applied', 'adjustment_date'),
            'classes': ('collapse',)
        }),
        ('Location Info', {
            'fields': ('audit_location', 'audit_aisle'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('audit', 'stock', 'counted_by')
