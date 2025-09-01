from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Stock, Category, Country, State, City, Person, Contacts, Product, 
    PurchaseOrder, PurchaseOrderItem, Manufacturer, DeliveryPerson, Store, 
    PurchaseOrderHistory, CommittedStock, StockTransfer, StockLocation, UserRole
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
    list_display = ('name', 'location', 'is_active')
    list_filter = ('is_active',)

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
