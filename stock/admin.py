from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Stock, Category, Country, State, City, Person, Contacts, Product, PurchaseOrder, PurchaseOrderItem, Manufacturer, DeliveryPerson, Store, PurchaseOrderHistory
from .form import StockCreateForm  # Note: 'form' should be 'forms' in the import

# Optional: Customize User admin if needed
class PurchaseOrderInline(admin.TabularInline):
    model = PurchaseOrder
    extra = 0
    fields = ('reference_number', 'manufacturer', 'status', 'created_at')
    readonly_fields = ('reference_number', 'manufacturer', 'status', 'created_at')

class StockInline(admin.TabularInline):
    model = Stock
    extra = 0
    fields = ('item_name', 'quantity', 'category', 'last_updated')
    readonly_fields = ('item_name', 'quantity', 'category', 'last_updated')

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    inlines = [PurchaseOrderInline, StockInline]

# Uncomment the following if you need to customize User admin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

# Stock Admin
class StockCreateAdmin(admin.ModelAdmin):
    list_display = ['category', 'item_name', 'quantity']
    form = StockCreateForm
    list_filter = ['category']
    search_fields = ['category', 'item_name']

# PurchaseOrder Admin
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

# Other PO System Models
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_price_inc', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_email', 'company_telephone')
    search_fields = ('company_name', 'company_email')

@admin.register(DeliveryPerson)
class DeliveryPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'is_active')
    list_filter = ('is_active',)

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active')
    list_filter = ('is_active',)

# Existing Model Registrations
admin.site.register(Stock, StockCreateAdmin)
admin.site.register(Category)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Person)
admin.site.register(Contacts)