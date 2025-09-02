from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# ----------------------------
# User Role & Permission Models
# ----------------------------

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('owner', 'Owner'),
        ('logistics', 'Logistics'),
        ('warehouse', 'Warehouse'),
        ('sales', 'Sales'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_user_roles')
    
    class Meta:
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def role_permissions(self):
        """Get permissions for this role"""
        permissions = {
            'admin': {
                'can_manage_users': True,
                'can_manage_access_control': True,
                'can_create_purchase_order': True,
                'can_edit_purchase_order': True,
                'can_view_purchase_order': True,
                'can_receive_purchase_order': True,
                'can_view_purchase_order_amounts': True,
                'can_create_stock': True,
                'can_edit_stock': True,
                'can_view_stock': True,
                'can_transfer_stock': True,
                'can_commit_stock': True,
                'can_fulfill_commitment': True,
                'can_issue_stock': True,
                'can_receive_stock': True,
                'can_view_warehouse_receiving': True,
            },
            'owner': {
                'can_manage_users': False,
                'can_manage_access_control': False,
                'can_create_purchase_order': True,
                'can_edit_purchase_order': True,
                'can_view_purchase_order': True,
                'can_receive_purchase_order': True,
                'can_view_purchase_order_amounts': True,
                'can_create_stock': True,
                'can_edit_stock': True,
                'can_view_stock': True,
                'can_transfer_stock': True,
                'can_commit_stock': True,
                'can_fulfill_commitment': True,
                'can_issue_stock': True,
                'can_receive_stock': True,
                'can_view_warehouse_receiving': True,
            },
            'logistics': {
                'can_manage_users': False,
                'can_manage_access_control': False,
                'can_create_purchase_order': True,
                'can_edit_purchase_order': True,
                'can_view_purchase_order': True,
                'can_receive_purchase_order': False,
                'can_view_purchase_order_amounts': True,
                'can_create_stock': False,
                'can_edit_stock': False,
                'can_view_stock': True,
                'can_transfer_stock': True,  # Can request transfer
                'can_commit_stock': True,
                'can_fulfill_commitment': False,
                'can_issue_stock': True,
                'can_receive_stock': True,
                'can_view_warehouse_receiving': False,
            },
            'warehouse': {
                'can_manage_users': False,
                'can_manage_access_control': False,
                'can_create_purchase_order': False,
                'can_edit_purchase_order': False,
                'can_view_purchase_order': True,
                'can_receive_purchase_order': True,
                'can_view_purchase_order_amounts': False,  # Cannot see amounts
                'can_create_stock': True,
                'can_edit_stock': True,
                'can_view_stock': True,
                'can_transfer_stock': True,
                'can_commit_stock': True,
                'can_fulfill_commitment': False,
                'can_issue_stock': True,
                'can_receive_stock': True,
                'can_view_warehouse_receiving': True,
            },
            'sales': {
                'can_manage_users': False,
                'can_manage_access_control': False,
                'can_create_purchase_order': False,
                'can_edit_purchase_order': False,
                'can_view_purchase_order': False,
                'can_receive_purchase_order': False,
                'can_view_purchase_order_amounts': False,
                'can_create_stock': False,
                'can_edit_stock': False,
                'can_view_stock': True,
                'can_transfer_stock': True,  # For customer collections
                'can_commit_stock': True,
                'can_fulfill_commitment': True,
                'can_issue_stock': False,
                'can_receive_stock': False,
                'can_view_warehouse_receiving': False,
            },
        }
        return permissions.get(self.role, permissions['sales'])
    
    def has_permission(self, permission):
        """Check if user has a specific permission"""
        return self.role_permissions.get(permission, False)

# ----------------------------
# Category & Stock Models
# ----------------------------

class Category(models.Model):
    group = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return self.group

class Stock(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('demo_unit', 'Demo Unit'),
        ('bstock', 'B-Stock'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    receive_quantity = models.IntegerField(default=0, blank=True, null=True)
    received_by = models.CharField(max_length=50, blank=True, null=True)
    issue_quantity = models.IntegerField(default=0, blank=True, null=True)
    issued_by = models.CharField(max_length=50, blank=True, null=True)
    committed_quantity = models.IntegerField(default=0, blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    location = models.ForeignKey('Store', on_delete=models.SET_NULL, null=True, blank=True, help_text="Store location where this item is kept")
    aisle = models.CharField(max_length=50, blank=True, null=True, help_text="Specific aisle or section within the store")
    note = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    re_order = models.IntegerField(default=0, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(default=timezone.now)
    export_to_csv = models.BooleanField(default=False)
    image = models.ImageField(upload_to='stock/images/', null=True, blank=True)
    source_purchase_order = models.ForeignKey('PurchaseOrder', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def total_stock(self):
        """Total stock quantity (current inventory)"""
        return self.quantity or 0
    
    @property
    def committed_stock(self):
        """Total committed stock (reserved for customers with deposits)"""
        return self.committed_quantity or 0
    
    @property
    def reserved_quantity(self):
        """Total reserved stock (active reservations)"""
        from django.utils import timezone
        return self.reservations.filter(
            status='active',
            expires_at__gt=timezone.now()
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def available_for_sale(self):
        """Available stock for sale (total - committed - reserved)"""
        return self.total_stock - self.committed_stock - self.reserved_quantity
    
    @property
    def is_low_stock(self):
        """Check if stock is below reorder level"""
        return self.available_for_sale <= (self.re_order or 0)
    
    @property
    def total_across_locations(self):
        """Total stock across all locations"""
        return self.locations.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    def get_location_quantity(self, store):
        """Get quantity at a specific location"""
        try:
            location = self.locations.get(store=store)
            return location.quantity
        except StockLocation.DoesNotExist:
            return 0
    
    def add_to_location(self, store, quantity, aisle=None):
        """Add quantity to a specific location"""
        location, created = self.locations.get_or_create(
            store=store,
            defaults={'quantity': 0, 'aisle': aisle}
        )
        location.quantity += quantity
        if aisle:
            location.aisle = aisle
        location.save()
        return location
    
    def remove_from_location(self, store, quantity):
        """Remove quantity from a specific location"""
        try:
            location = self.locations.get(store=store)
            if location.quantity >= quantity:
                location.quantity -= quantity
                location.save()
                return True
            return False
        except StockLocation.DoesNotExist:
            return False
    
    def __str__(self):
        return f"{self.item_name} ({self.quantity}) - {self.last_updated}"

class StockHistory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True)
    receive_quantity = models.IntegerField(default=0, blank=True, null=True)
    received_by = models.CharField(max_length=50, blank=True, null=True)
    issue_quantity = models.IntegerField(default=0, blank=True, null=True)
    issued_by = models.CharField(max_length=50, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    re_order = models.IntegerField(default=0, blank=True, null=True)
    last_updated = models.DateTimeField(null=True)
    timestamp = models.DateTimeField(null=True)

class CommittedStock(models.Model):
    """Track individual stock commitments with deposit and order details"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='commitments')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    customer_order_number = models.CharField(max_length=100, help_text="Customer's order reference number")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=50, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    committed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    committed_at = models.DateTimeField(auto_now_add=True)
    is_fulfilled = models.BooleanField(default=False)
    fulfilled_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-committed_at']
    
    def __str__(self):
        status = "Fulfilled" if self.is_fulfilled else "Active"
        return f"{self.stock.item_name} - {self.quantity}pcs - {self.customer_order_number} ({status})"
    
    def save(self, *args, **kwargs):
        # Update the stock's committed_quantity when saving
        super().save(*args, **kwargs)
        self.stock.committed_quantity = self.stock.commitments.filter(is_fulfilled=False).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        self.stock.save(update_fields=['committed_quantity'])


class StockReservation(models.Model):
    """Track temporary stock reservations without deposits"""
    RESERVATION_TYPE_CHOICES = [
        ('quote', 'Quote/Estimate'),
        ('hold', 'Customer Hold'),
        ('inspection', 'Customer Inspection'),
        ('transfer_prep', 'Transfer Preparation'),
        ('maintenance', 'Maintenance/Repair'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='reservations')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    reservation_type = models.CharField(max_length=20, choices=RESERVATION_TYPE_CHOICES, default='hold')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Customer/Contact info (optional)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=50, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Quote number, order reference, etc.")
    
    # Reservation details
    reason = models.TextField(help_text="Reason for reservation")
    notes = models.TextField(blank=True, null=True)
    
    # Timing
    reserved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reservations')
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this reservation expires")
    fulfilled_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    # Tracking
    fulfilled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fulfilled_reservations')
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_reservations')
    
    class Meta:
        ordering = ['-reserved_at']
        verbose_name = 'Stock Reservation'
        verbose_name_plural = 'Stock Reservations'
    
    def __str__(self):
        return f"{self.stock.item_name} - {self.quantity}pcs ({self.get_status_display()}) - {self.customer_name or 'No Customer'}"
    
    def is_active(self):
        """Check if reservation is currently active"""
        from django.utils import timezone
        return self.status == 'active' and self.expires_at > timezone.now()
    
    def is_expired(self):
        """Check if reservation has expired"""
        from django.utils import timezone
        return self.expires_at <= timezone.now() and self.status == 'active'
    
    def can_be_fulfilled(self):
        """Check if reservation can be converted to commitment/sale"""
        return self.status == 'active'
    
    def can_be_cancelled(self):
        """Check if reservation can be cancelled"""
        return self.status in ['active', 'expired']
    
    def expire(self):
        """Mark reservation as expired"""
        if self.status == 'active':
            from django.utils import timezone
            self.status = 'expired'
            self.save()
            return True
        return False
    
    def fulfill(self, user):
        """Mark reservation as fulfilled"""
        if self.can_be_fulfilled():
            from django.utils import timezone
            self.status = 'fulfilled'
            self.fulfilled_at = timezone.now()
            self.fulfilled_by = user
            self.save()
            return True
        return False
    
    def cancel(self, user):
        """Cancel the reservation"""
        if self.can_be_cancelled():
            from django.utils import timezone
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.cancelled_by = user
            self.save()
            return True
        return False
    
    @property
    def days_until_expiry(self):
        """Get days until expiry"""
        from django.utils import timezone
        if self.status != 'active':
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

class StockLocation(models.Model):
    """Track stock quantities at different locations for the same item"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='locations')
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    aisle = models.CharField(max_length=50, blank=True, null=True, help_text="Specific aisle or section within the store")
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('stock', 'store')
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.stock.item_name} at {self.store.name}: {self.quantity} units"
    
    @property
    def is_low_stock(self):
        """Check if this location's stock is below reorder level"""
        return self.quantity <= (self.stock.re_order or 0)

class StockTransfer(models.Model):
    """Track stock transfers between different store locations"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('awaiting_collection', 'Awaiting Customer Collection'),
        ('collected', 'Customer Collected'),
        ('cancelled', 'Cancelled'),
    ]
    
    TRANSFER_TYPE_CHOICES = [
        ('restock', 'Restock'),
        ('customer_collection', 'Customer Collection'),
        ('general', 'General Transfer'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transfers')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    from_location = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_location = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='incoming_transfers')
    from_aisle = models.CharField(max_length=50, blank=True, null=True)
    to_aisle = models.CharField(max_length=50, blank=True, null=True)
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE_CHOICES, default='general')
    transfer_reason = models.CharField(max_length=255, help_text="Reason for transfer (e.g., customer collection, restock)")
    customer_name = models.CharField(max_length=100, blank=True, null=True, help_text="Customer name (for collection transfers)")
    customer_phone = models.CharField(max_length=50, blank=True, null=True, help_text="Customer contact")
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_transfers')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transfers')
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_transfers')
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collected_transfers')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transfer {self.stock.item_name} ({self.quantity}pcs) from {self.from_location} to {self.to_location}"
    
    def can_be_approved(self):
        return self.status == 'pending'
    
    def can_be_completed(self):
        return self.status in ['pending', 'in_transit']
    
    def can_be_collected(self):
        return self.status == 'awaiting_collection'
    
    def approve(self, user):
        if self.can_be_approved():
            self.status = 'in_transit'
            self.approved_by = user
            self.approved_at = timezone.now()
            self.save()
    
    def complete(self, user):
        if self.can_be_completed():
            # Handle different transfer types
            if self.transfer_type == 'restock':
                # For restock: move quantity from origin to destination
                self.stock.remove_from_location(self.from_location, self.quantity)
                self.stock.add_to_location(self.to_location, self.quantity, self.to_aisle)
                self.status = 'completed'
            elif self.transfer_type == 'customer_collection':
                # For customer collection: quantity already reduced, just update location and wait
                self.stock.add_to_location(self.to_location, self.quantity, self.to_aisle)
                self.status = 'awaiting_collection'
            else:
                # General transfer: move quantity
                self.stock.add_to_location(self.to_location, self.quantity, self.to_aisle)
                self.status = 'completed'
            
            self.completed_by = user
            self.completed_at = timezone.now()
            self.save()
    
    def mark_collected(self, user):
        """Mark customer collection transfer as collected and reduce stock"""
        if self.can_be_collected():
            # Remove the quantity from the destination location (customer has collected)
            self.stock.remove_from_location(self.to_location, self.quantity)
            
            self.status = 'collected'
            self.collected_by = user
            self.collected_at = timezone.now()
            self.save()
    
    @property
    def is_pending_collection(self):
        return self.status == 'awaiting_collection'

# ----------------------------
# Location & Person Models
# ----------------------------

class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class Contacts(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Contact for {self.person.name if self.person else 'Unknown'}"

# ----------------------------
# Scrum Models
# ----------------------------

class ScrumTitles(models.Model):
    lists = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return str(self.lists)

class Scrums(models.Model):
    task = models.CharField(max_length=100, blank=True, null=True)
    task_description = models.CharField(max_length=100, blank=True, null=True)
    task_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.task

# ----------------------------
# Product & Inventory Models
# ----------------------------

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    default_price_inc = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

# ----------------------------
# Manufacturer, DeliveryPerson, Store
# ----------------------------

class Manufacturer(models.Model):
    company_name = models.CharField(max_length=200)
    company_email = models.EmailField()
    additional_email = models.EmailField(blank=True, null=True)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    company_telephone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class DeliveryPerson(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}, {self.phone_number}"

class Store(models.Model):
    STORE_CHOICES = [
        ('audio_junction_newcastle', 'Audio Junction Store - Newcastle'),
        ('digital_cinema_auburn', 'Digital Cinema Store - Auburn'),
        ('instyle_dural', 'Instyle Store - Dural'),
        ('silverwater_warehouse', 'Silverwater Warehouse'),
        ('auburn_warehouse', 'Auburn Warehouse'),
    ]
    
    name = models.CharField(max_length=200, choices=STORE_CHOICES)
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True, help_text="Store contact email")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_name_display()}"

# ----------------------------
# Purchase Order Models
# ----------------------------

class PurchaseOrder(models.Model):
    DELIVERY_CHOICES = [
        ('dropship', 'Dropship'),
        ('store', 'Store'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('sent', 'Sent to Manufacturer'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    reference_number = models.CharField(max_length=50, unique=True, editable=False)
    note_for_manufacturer = models.TextField(blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.CASCADE)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='store')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            from datetime import datetime
            year = datetime.now().year
            last_po = PurchaseOrder.objects.filter(
                reference_number__startswith=f'PO-{year}-'
            ).order_by('-id').first()
            new_number = 1 if not last_po else int(last_po.reference_number.split('-')[-1]) + 1
            self.reference_number = f'PO-{year}-{new_number:03d}'
        super().save(*args, **kwargs)

    @property
    def overall_receiving_status(self):
        if not self.items.exists():
            return 'no_items'
        statuses = [item.receiving_status for item in self.items.all()]
        if all(status == 'not_received' for status in statuses):
            return 'not_received'
        elif all(status == 'fully_received' for status in statuses):
            return 'fully_received'
        else:
            return 'partially_received'

    @property
    def subtotal_exc(self):
        return sum(item.line_total_exc for item in self.items.all())

    @property
    def total_discount_amount(self):
        return sum(item.discount_amount for item in self.items.all())

    @property
    def subtotal_after_discount(self):
        return self.subtotal_exc - self.total_discount_amount

    @property
    def gst_amount(self):
        return self.subtotal_after_discount * Decimal("0.10")

    @property
    def grand_total(self):
        return self.subtotal_after_discount + self.gst_amount

    def __str__(self):
        return f"{self.reference_number} - {self.manufacturer.company_name}"

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    product = models.CharField(max_length=255)
    associated_order_number = models.CharField(max_length=100, blank=True, null=True)
    price_inc = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True, null=True
    )
    received_quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def price_exc(self):
        return self.price_inc * Decimal("0.90")

    @property
    def line_total_inc(self):
        return self.price_inc * self.quantity

    @property
    def line_total_exc(self):
        return self.price_exc * self.quantity

    @property
    def discount_amount(self):
        if not self.discount_percent:
            return Decimal("0.00")
        return (self.line_total_exc * self.discount_percent) / Decimal("100")

    @property
    def subtotal_exc(self):
        return self.line_total_exc - self.discount_amount

    @property
    def total_received_quantity(self):
        return sum(record.quantity_received for record in self.receiving_records.all())

    @property
    def remaining_quantity(self):
        return self.quantity - self.total_received_quantity

    @property
    def is_fully_received(self):
        return self.total_received_quantity >= self.quantity

    @property
    def receiving_status(self):
        total_received = self.total_received_quantity
        if total_received == 0:
            return 'not_received'
        elif total_received < self.quantity:
            return 'partially_received'
        else:
            return 'fully_received'

    def __str__(self):
        return f"{self.product} - {self.purchase_order.reference_number}"

class PurchaseOrderHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('submitted', 'Submitted'),
        ('sent', 'Sent to Manufacturer'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='history', on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.purchase_order.reference_number} - {self.action}"

class PurchaseOrderReceiving(models.Model):
    purchase_order_item = models.ForeignKey(PurchaseOrderItem, related_name='receiving_records', on_delete=models.CASCADE)
    quantity_received = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    delivery_reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(User, on_delete=models.CASCADE)
    received_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        from django.core.exceptions import ValidationError
        existing_received = self.purchase_order_item.receiving_records.exclude(pk=self.pk).aggregate(
            total=models.Sum('quantity_received')
        )['total'] or 0
        total_after_this = existing_received + self.quantity_received
        if total_after_this > self.purchase_order_item.quantity:
            raise ValidationError(
                f'Cannot receive {self.quantity_received} items. Only {self.purchase_order_item.remaining_quantity} items remaining to receive.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        po = self.purchase_order_item.purchase_order
        if po.overall_receiving_status == 'fully_received' and po.status != 'completed':
            po.status = 'completed'
            po.save()
            PurchaseOrderHistory.objects.create(
                purchase_order=po,
                action='completed',
                notes='All items received - Purchase order completed automatically',
                created_by=self.received_by
            )

    def __str__(self):
        return f"{self.purchase_order_item.product} - Received {self.quantity_received} on {self.received_at.strftime('%Y-%m-%d')}"
