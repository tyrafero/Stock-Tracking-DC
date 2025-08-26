from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Stock, Category, Country, State, City, Person, Contacts, Product, 
    PurchaseOrder, PurchaseOrderItem, Manufacturer, DeliveryPerson, Store, 
    PurchaseOrderHistory
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

# Stock Admin
class StockAdmin(admin.ModelAdmin):
    list_display = ['category', 'item_name', 'quantity']
    form = StockCreateForm
    list_filter = ['category']
    search_fields = ['category', 'item_name']

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
