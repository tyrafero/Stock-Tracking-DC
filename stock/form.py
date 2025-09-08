from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML, Submit, Row, Column
from registration.forms import RegistrationForm
from django.utils import timezone
from datetime import timedelta


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'sku', 'condition', 'quantity', 'location', 'aisle', 'image_url']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SKU (e.g., SKU-001)'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'aisle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aisle or section (e.g., A1, B2)'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact phone number'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter image URL'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all active stores are available in location dropdown
        self.fields['location'].queryset = Store.objects.filter(is_active=True)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('category', css_class='form-group col-md-6'),
                Column('item_name', css_class='form-group col-md-6'),
            ),
            Row(
                Column('sku', css_class='form-group col-md-6'),
                Column('condition', css_class='form-group col-md-6'),
            ),
            Row(
                Column('quantity', css_class='form-group col-md-6'),
                Column('location', css_class='form-group col-md-6'),
            ),
            Row(
                Column('aisle', css_class='form-group col-md-6'),
                Column('note', css_class='form-group col-md-6'),
            ),
            Row(Column('image_url', css_class='form-group col-md-12')),
            Submit('submit', 'Save Stock', css_class='btn btn-primary')
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set default values for background fields
        instance.received_by = "System"
        instance.issued_by = "System"
        # If note is empty, set default
        if not instance.note:
            instance.note = "Fresh Stock"
        if commit:
            instance.save()
        return instance


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'sku', 'condition', 'quantity', 'location', 'aisle', 'image_url', 'note']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SKU (e.g., SKU-001)'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'aisle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aisle or section (e.g., A1, B2)'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter image URL'}),
            'note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Update note'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all active stores are available in location dropdown
        self.fields['location'].queryset = Store.objects.filter(is_active=True)


class IssueForm(forms.ModelForm):
    issue_location = forms.ModelChoiceField(
        queryset=Store.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the location to issue items from"
    )
    note = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issue note (optional)'})
    )
    
    class Meta:
        model = Stock
        fields = ['issue_quantity', 'note']
        widgets = {
            'issue_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        stock = kwargs.pop('stock', None)
        super().__init__(*args, **kwargs)
        self.stock = stock
        
        if stock:
            # Only show locations that have stock available
            stock_locations = stock.locations.filter(quantity__gt=0)
            self.fields['issue_location'].queryset = Store.objects.filter(
                id__in=stock_locations.values_list('store_id', flat=True)
            )


class ReceiveForm(forms.ModelForm):
    receive_location = forms.ModelChoiceField(
        queryset=Store.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the location where items are being received"
    )
    receive_aisle = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aisle or section (e.g., A1, B2)'}),
        help_text="Specific aisle or section within the location"
    )
    note = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Receive note (optional)'})
    )
    
    class Meta:
        model = Stock
        fields = ['receive_quantity', 'note']
        widgets = {
            'receive_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        stock = kwargs.pop('stock', None)
        super().__init__(*args, **kwargs)
        self.stock = stock
        
        if stock:
            # Default to the first location with existing stock, or first active store
            existing_locations = stock.locations.filter(quantity__gt=0)
            if existing_locations.exists():
                self.fields['receive_location'].initial = existing_locations.first().store
            else:
                self.fields['receive_location'].initial = Store.objects.filter(is_active=True).first()

class CommitStockForm(forms.ModelForm):
    class Meta:
        model = CommittedStock
        fields = ['quantity', 'customer_order_number', 'deposit_amount', 'customer_name', 
                 'customer_phone', 'customer_email', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'customer_order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer order reference'}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer name'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (optional)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('quantity', css_class='form-group col-md-6'),
                Column('customer_order_number', css_class='form-group col-md-6'),
            ),
            Row(
                Column('deposit_amount', css_class='form-group col-md-6'),
                Column('customer_name', css_class='form-group col-md-6'),
            ),
            Row(
                Column('customer_phone', css_class='form-group col-md-6'),
                Column('customer_email', css_class='form-group col-md-6'),
            ),
            Row(
                Column('notes', css_class='form-group col-md-12'),
            ),
            Submit('submit', 'Commit Stock', css_class='btn btn-success')
        )


class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['re_order']
        widgets = {
            're_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

class StockTransferForm(forms.ModelForm):
    from_location = forms.ModelChoiceField(
        queryset=Store.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_from_location'}),
        help_text="Select the source location to transfer from"
    )

    class Meta:
        model = StockTransfer
        fields = ['from_location', 'quantity', 'to_location', 'to_aisle', 'transfer_type', 'transfer_reason', 'customer_name', 'customer_phone', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'to_location': forms.Select(attrs={'class': 'form-control'}),
            'to_aisle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination aisle (e.g., A1, B2)'}),
            'transfer_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_transfer_type'}),
            'transfer_reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Customer collection, Restock'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer name (for collection transfers)'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer phone number'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional transfer notes'}),
        }

    def __init__(self, *args, **kwargs):
        stock = kwargs.pop('stock', None)
        super().__init__(*args, **kwargs)
        self.stock = stock
        
        # Set up location choices based on stock locations
        if stock:
            # Get locations where this stock exists
            stock_locations = stock.locations.filter(quantity__gt=0)
            self.fields['from_location'].queryset = Store.objects.filter(
                id__in=stock_locations.values_list('store_id', flat=True)
            )
            
            # Show all active stores as destination choices
            self.fields['to_location'].queryset = Store.objects.filter(is_active=True)
            
            total_stock = stock.total_across_locations
            self.fields['quantity'].widget.attrs['max'] = str(total_stock)
            self.fields['quantity'].help_text = f"Total available: {total_stock}"
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('from_location', css_class='form-group col-md-6'),
                Column('quantity', css_class='form-group col-md-6'),
            ),
            Row(
                Column('to_location', css_class='form-group col-md-6'),
                Column('to_aisle', css_class='form-group col-md-6'),
            ),
            Row(
                Column('transfer_type', css_class='form-group col-md-12'),
            ),
            Row(
                Column('transfer_reason', css_class='form-group col-md-12'),
            ),
            HTML('<div id="customer_fields" style="display: none;">'),
            Row(
                Column('customer_name', css_class='form-group col-md-6'),
                Column('customer_phone', css_class='form-group col-md-6'),
            ),
            HTML('</div>'),
            Row(
                Column('notes', css_class='form-group col-md-12'),
            ),
            Submit('submit', 'Transfer Stock', css_class='btn btn-warning')
        )

    def clean(self):
        cleaned_data = super().clean()
        transfer_type = cleaned_data.get('transfer_type')
        customer_name = cleaned_data.get('customer_name')
        
        # If transfer type is customer collection, customer name is required
        if transfer_type == 'customer_collection' and not customer_name:
            raise forms.ValidationError('Customer name is required for customer collection transfers.')
        
        return cleaned_data

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if self.stock and quantity > self.stock.quantity:
            raise forms.ValidationError(f'Cannot transfer more than {self.stock.quantity} items available.')
        return quantity


class StockSearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)

    class Meta:
        model = Stock
        fields = ['category', 'item_name']


class StockHistorySearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)

    class Meta:
        model = StockHistory
        fields = ['category', 'item_name', 'start_date', 'end_date']


# Purchase Order Forms (unchanged from your original)
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['note_for_manufacturer', 'manufacturer', 'delivery_person', 'delivery_type', 'creating_store', 'store']
        widgets = {
            'note_for_manufacturer': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter notes for manufacturer...'}),
            'manufacturer': forms.Select(attrs={'class': 'form-control', 'id': 'id_manufacturer'}),
            'delivery_person': forms.Select(attrs={'class': 'form-control'}),
            'delivery_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_delivery_type'}),
            'creating_store': forms.Select(attrs={'class': 'form-control', 'id': 'id_creating_store'}),
            'store': forms.Select(attrs={'class': 'form-control', 'id': 'id_store'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                HTML('<h5 class="mb-3">PO Information</h5>'),
                Row(Column('note_for_manufacturer', css_class='form-group col-md-12 mb-3')),
                css_class='card card-inner mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">Responsible Person</h5>'),
                Row(Column('delivery_person', css_class='form-group col-md-12 mb-3')),
                css_class='card card-inner mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">Manufacturer Information</h5>'),
                Row(Column('manufacturer', css_class='form-group col-md-12 mb-3')),
                HTML('<div id="manufacturer-details" class="mt-3"></div>'),
                css_class='card card-inner mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">Store Information</h5>'),
                Row(
                    Column('creating_store', css_class='form-group col-md-6 mb-3'),
                    Column('delivery_type', css_class='form-group col-md-6 mb-3'),
                ),
                Row(
                    Column('store', css_class='form-group col-md-12 mb-3'),
                ),
                css_class='card card-inner mb-4'
            ),
        )
        # Configure creating store field
        self.fields['creating_store'].required = True
        self.fields['creating_store'].label = 'Creating Store'
        self.fields['creating_store'].help_text = 'Store that is creating this purchase order'
        self.fields['creating_store'].queryset = Store.objects.filter(is_active=True, designation='store').order_by('name')
        
        # Make delivery location required and rename label
        self.fields['store'].required = True
        self.fields['store'].label = 'Delivery Location'
        self.fields['store'].help_text = 'Where items will be delivered and added to inventory (can be any store or warehouse)'
        self.fields['store'].queryset = Store.objects.filter(is_active=True).order_by('designation', 'name')


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'associated_order_number', 'price_inc', 'quantity', 'discount_percent']
        widgets = {
            'product': forms.TextInput(attrs={'class': 'form-control product-input', 'placeholder': 'Product name'}),
            'associated_order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Order #'}),
            'price_inc': forms.NumberInput(attrs={'class': 'form-control price-inc', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity', 'min': '1', 'placeholder': '1'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control discount-percent', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '0.00', 'value': '0'}),
        }

    def __init__(self, *args, **kwargs):
        edit_mode = kwargs.pop('edit_mode', False)  # Handle edit_mode parameter
        super().__init__(*args, **kwargs)
        # Make discount_percent default to 0 if empty
        self.fields['discount_percent'].initial = 0
        # Set required fields
        for field_name, field in self.fields.items():
            field.required = field_name in ['product', 'price_inc', 'quantity']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        price_inc = cleaned_data.get('price_inc')
        quantity = cleaned_data.get('quantity')
        
        # If any field has data, then all required fields must have data
        has_data = any([product, price_inc, quantity])
        
        if has_data:
            if not product:
                self.add_error('product', 'Product name is required.')
            if not price_inc:
                self.add_error('price_inc', 'Price is required.')
            if not quantity:
                self.add_error('quantity', 'Quantity is required.')
        
        # Set default discount_percent if not provided
        if not cleaned_data.get('discount_percent'):
            cleaned_data['discount_percent'] = 0
        
        return cleaned_data


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)



class BulkReceivingForm(forms.Form):
    """Form for receiving multiple items at once"""
    def __init__(self, *args, purchase_order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.purchase_order = purchase_order
        
        if purchase_order:
            # Create fields for each item that hasn't been fully received
            for item in purchase_order.items.all():
                remaining = item.remaining_quantity
                if remaining > 0:
                    field_name = f'item_{item.pk}_quantity'
                    self.fields[field_name] = forms.IntegerField(
                        required=False,
                        min_value=0,
                        max_value=remaining,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'placeholder': f'Max: {remaining}',
                            'min': '0',
                            'max': str(remaining)
                        }),
                        label=f'{item.product} (Remaining: {remaining})',
                        help_text=f'Enter quantity received (max: {remaining})'
                    )
            
            # Common fields for all items
            self.fields['delivery_reference'] = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Delivery note, invoice #, tracking #'
                }),
                label='Delivery Reference',
                help_text='Common reference for all items in this delivery'
            )
            
            self.fields['notes'] = forms.CharField(
                required=False,
                widget=forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Notes about this delivery...'
                }),
                label='Delivery Notes',
                help_text='Common notes for all items in this delivery'
            )

    def clean(self):
        cleaned_data = super().clean()
        
        # Check if at least one item quantity is provided
        has_quantities = False
        for field_name, value in cleaned_data.items():
            if field_name.startswith('item_') and field_name.endswith('_quantity') and value and value > 0:
                has_quantities = True
                break
        
        if not has_quantities:
            raise forms.ValidationError('Please enter at least one quantity to receive.')
        
        return cleaned_data

    def get_receiving_data(self):
        """Extract receiving data for processing"""
        data = []
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('item_') and field_name.endswith('_quantity') and value and value > 0:
                item_pk = field_name.replace('item_', '').replace('_quantity', '')
                data.append({
                    'item_pk': int(item_pk),
                    'quantity': value,
                    'delivery_reference': self.cleaned_data.get('delivery_reference', ''),
                    'notes': self.cleaned_data.get('notes', '')
                })
        return data

class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['company_name', 'company_email', 'additional_email', 'street_address', 'city', 'country', 'region', 'postal_code', 'company_telephone', 'abn']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'additional_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'street_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'company_telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'abn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12 345 678 901'}),
        }
        labels = {
            'city': 'Suburb',
            'region': 'State',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('company_name', css_class='form-group col-md-6 mb-3'),
                Column('company_telephone', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('company_email', css_class='form-group col-md-6 mb-3'),
                Column('additional_email', css_class='form-group col-md-6 mb-3'),
            ),
            Row(Column('street_address', css_class='form-group col-md-12 mb-3')),
            Row(
                Column('city', css_class='form-group col-md-4 mb-3'),
                Column('region', css_class='form-group col-md-4 mb-3'),
                Column('postal_code', css_class='form-group col-md-4 mb-3'),
            ),
            Row(Column('country', css_class='form-group col-md-12 mb-3')),
            Submit('submit', 'Save Manufacturer', css_class='btn btn-primary')
        )


class DeliveryPersonForm(forms.ModelForm):
    class Meta:
        model = DeliveryPerson
        fields = ['name', 'phone_number', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
            ),
            Row(Column('is_active', css_class='form-group col-md-12 mb-3')),
            Submit('submit', 'Save Delivery Person', css_class='btn btn-primary')
        )


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'designation', 'location', 'email', 'order_email', 'address', 'logo_url', 'website_url', 'facebook_url', 'instagram_url', 'abn', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter store or warehouse name'}),
            'designation': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'sales@example.com'}),
            'order_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'orders@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'logo_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/logo.png'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.example.com'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.facebook.com/yourpage'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.instagram.com/yourprofile'}),
            'abn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12 345 678 901'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'  # Required for file uploads
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('designation', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('location', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('logo', css_class='form-group col-md-6 mb-3'),
                Column('is_active', css_class='form-group col-md-6 mb-3'),
            ),
            Row(Column('address', css_class='form-group col-md-12 mb-3')),
            Submit('submit', 'Save Store', css_class='btn btn-primary')
        )


class PurchaseOrderSearchForm(forms.Form):
    reference_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by PO Reference Number'})
    )
    manufacturer = forms.ModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + PurchaseOrder.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('reference_number', css_class='form-group col-md-4'),
                Column('manufacturer', css_class='form-group col-md-4'),
                Column('status', css_class='form-group col-md-4'),
            ),
            Submit('search', 'Search', css_class='btn btn-primary')
        )


# Contact and other forms (simplified)
class ContactsForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = '__all__'


class AddScrumListForm(forms.ModelForm):
    class Meta:
        model = ScrumTitles
        fields = ['lists']


class AddScrumTaskForm(forms.ModelForm):
    class Meta:
        model = Scrums
        fields = ['task', 'task_description', 'task_date']


class DependentDropdownForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    state = forms.ModelChoiceField(queryset=State.objects.none())
    city = forms.ModelChoiceField(queryset=City.objects.none())
    
    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].queryset = State.objects.none()
        if 'country' in self.data:
            try:
                country_idm = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_idm).order_by('name')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['state'].queryset = self.instance.country.state_set.order_by('name')

        self.fields['city'].queryset = City.objects.none()
        if 'state' in self.data:
            try:
                state_idm = int(self.data.get('state'))
                self.fields['city'].queryset = City.objects.filter(state_id=state_idm).order_by('name')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.state.city_set.order_by('name')


class CustomRegistrationForm(RegistrationForm):
    allowed_domains = ['digitalcinema.com.au','gmail.com']
    allowed_specific_emails = ['atish.digitalcinema@gmail.com']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        domain = email.split('@')[-1]

        if domain in self.allowed_domains or email.lower() in [e.lower() for e in self.allowed_specific_emails]:
            return email

        raise forms.ValidationError(
            "Registration is only allowed with @digitalcinema.com.au emails or approved Gmail accounts."
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['group']
        widgets = {
            'group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name (e.g., Electronics, Accessories)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('group', css_class='form-group col-md-12 mb-3'),
            ),
            Submit('submit', 'Save Category', css_class='btn btn-primary')
        )

    def clean_group(self):
        group = self.cleaned_data.get('group')
        if group:
            group = group.strip()
            # Check if category already exists (case-insensitive)
            existing = Category.objects.filter(group__iexact=group)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(f'Category "{group}" already exists.')
        
        return group


# ----------------------------
# Access Control Forms
# ----------------------------

class UserRoleForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        required=False,
        help_text="Leave blank to keep current password when editing"
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = UserRole
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        if self.user_instance:
            self.fields['username'].initial = self.user_instance.username
            self.fields['first_name'].initial = self.user_instance.first_name
            self.fields['last_name'].initial = self.user_instance.last_name
            self.fields['email'].initial = self.user_instance.email
            self.fields['is_active'].initial = self.user_instance.is_active
            self.fields['password'].required = False
            self.fields['password'].help_text = "Leave blank to keep current password"
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = "Enter a password for the new user"
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('role', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-8 mb-3'),
                Column('is_active', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('password', css_class='form-group col-md-12 mb-3'),
            ),
            Submit('submit', 'Save User', css_class='btn btn-primary')
        )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            existing_user = User.objects.filter(username=username)
            if self.user_instance:
                existing_user = existing_user.exclude(pk=self.user_instance.pk)
            
            if existing_user.exists():
                raise forms.ValidationError('A user with this username already exists.')
        
        return username
    
    def save(self, commit=True, created_by=None):
        role = super().save(commit=False)
        
        # Handle User creation/update
        if self.user_instance:
            user = self.user_instance
        else:
            user = User()
        
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_active = self.cleaned_data['is_active']
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            role.user = user
            if created_by:
                role.created_by = created_by
            role.save()
        
        return role

class UserSearchForm(forms.Form):
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by username'})
    )
    role = forms.ChoiceField(
        required=False,
        choices=[('', 'All Roles')] + UserRole.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.ChoiceField(
        required=False,
        choices=[('', 'All Users'), ('true', 'Active'), ('false', 'Inactive')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-4'),
                Column('role', css_class='form-group col-md-4'),
                Column('is_active', css_class='form-group col-md-4'),
            ),
            Submit('search', 'Search', css_class='btn btn-primary')
        )

class ReceivePOItemsForm(forms.Form):
    purchase_order = forms.ModelChoiceField(
        queryset=PurchaseOrder.objects.none(),  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select a Purchase Order"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show POs that have items to receive
        self.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(
            status__in=['submitted', 'sent', 'confirmed'],
            items__received_quantity__lt=models.F('items__quantity')
        ).select_related('manufacturer').distinct()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('purchase_order', css_class='form-group col-md-12 mb-3'),
            ),
            Submit('select_po', 'Load Items to Receive', css_class='btn btn-primary')
        )

class ReceiveItemForm(forms.Form):
    def __init__(self, items, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for item in items:
            remaining_qty = item.quantity - item.received_quantity
            if remaining_qty > 0:
                # Quantity to receive field
                self.fields[f'receive_qty_{item.id}'] = forms.IntegerField(
                    min_value=0,
                    max_value=remaining_qty,
                    initial=remaining_qty,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'placeholder': f'Max: {remaining_qty}'
                    }),
                    label=f'Receive ({item.product})',
                    required=False
                )
                
                # Location field
                self.fields[f'location_{item.id}'] = forms.ModelChoiceField(
                    queryset=Store.objects.filter(is_active=True),
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    label='Location',
                    required=False
                )
                
                # Condition field
                self.fields[f'condition_{item.id}'] = forms.ChoiceField(
                    choices=Stock.CONDITION_CHOICES,
                    initial='new',
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    label='Condition',
                    required=False
                )
                
                # Aisle field
                self.fields[f'aisle_{item.id}'] = forms.CharField(
                    max_length=50,
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'e.g., A1, B2'
                    }),
                    label='Aisle'
                )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h5>Items to Receive</h5>'),
            Submit('receive_items', 'Receive Selected Items', css_class='btn btn-success')
        )


class StockReservationForm(forms.ModelForm):
    """Form for creating stock reservations"""
    
    duration_days = forms.IntegerField(
        initial=7,
        min_value=1,
        max_value=90,
        help_text="Number of days to hold this reservation",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = StockReservation
        fields = [
            'quantity', 'reservation_type', 'customer_name', 
            'customer_phone', 'customer_email', 'reference_number',
            'reason', 'notes'
        ]
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'reservation_type': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer name (optional)'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address (optional)'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quote #, Order #, etc. (optional)'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for reservation'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes (optional)'}),
        }
    
    def __init__(self, stock=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stock = stock
        
        if stock:
            # Set max quantity based on available stock
            available = stock.available_for_sale
            self.fields['quantity'].widget.attrs['max'] = available
            self.fields['quantity'].help_text = f"Maximum available: {available} units"
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-0'),
                Column('reservation_type', css_class='form-group col-md-4 mb-0'),
                Column('duration_days', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('customer_name', css_class='form-group col-md-6 mb-0'),
                Column('customer_phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('customer_email', css_class='form-group col-md-6 mb-0'),
                Column('reference_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'reason',
            'notes',
            Submit('create_reservation', 'Create Reservation', css_class='btn btn-warning')
        )
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if self.stock and quantity:
            available = self.stock.available_for_sale
            if quantity > available:
                raise forms.ValidationError(f'Only {available} units available for reservation.')
        return quantity
    
    def save(self, commit=True, reserved_by=None):
        reservation = super().save(commit=False)
        if reserved_by:
            reservation.reserved_by = reserved_by
        if self.stock:
            reservation.stock = self.stock
        
        # Calculate expiry date
        duration = self.cleaned_data.get('duration_days', 7)
        reservation.expires_at = timezone.now() + timedelta(days=duration)
        
        if commit:
            reservation.save()
        return reservation


class StockReservationUpdateForm(forms.ModelForm):
    """Form for updating existing stock reservations"""
    
    extend_days = forms.IntegerField(
        initial=0,
        min_value=0,
        max_value=30,
        required=False,
        help_text="Extend reservation by additional days",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = StockReservation
        fields = [
            'customer_name', 'customer_phone', 'customer_email', 
            'reference_number', 'reason', 'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('customer_name', css_class='form-group col-md-6 mb-0'),
                Column('customer_phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('customer_email', css_class='form-group col-md-6 mb-0'),
                Column('reference_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'reason',
            'notes',
            'extend_days',
            Submit('update_reservation', 'Update Reservation', css_class='btn btn-primary')
        )
    
    def save(self, commit=True):
        reservation = super().save(commit=False)
        
        # Extend expiry if requested
        extend_days = self.cleaned_data.get('extend_days', 0)
        if extend_days > 0:
            reservation.expires_at = reservation.expires_at + timedelta(days=extend_days)
        
        if commit:
            reservation.save()
        return reservation


# ----------------------------
# Stock Audit Forms
# ----------------------------

class StockAuditForm(forms.ModelForm):
    class Meta:
        model = StockAudit
        fields = ['audit_reference', 'title', 'description', 'audit_type', 'planned_start_date', 
                 'planned_end_date', 'audit_locations', 'audit_categories', 'assigned_auditors']
        widgets = {
            'audit_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AUD-2024-001'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quarterly Stock Audit'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description of audit scope and purpose'}),
            'audit_type': forms.Select(attrs={'class': 'form-control'}),
            'planned_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'audit_locations': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'audit_categories': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'assigned_auditors': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Generate default audit reference if creating new audit
        if not self.instance.pk:
            from django.utils import timezone
            import uuid
            year = timezone.now().year
            ref = f"AUD-{year}-{str(uuid.uuid4())[:8].upper()}"
            self.fields['audit_reference'].initial = ref

    def clean_planned_end_date(self):
        start_date = self.cleaned_data.get('planned_start_date')
        end_date = self.cleaned_data.get('planned_end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date must be after start date.")
        
        return end_date


class StockAuditItemForm(forms.ModelForm):
    class Meta:
        model = StockAuditItem
        fields = ['physical_count', 'variance_reason', 'variance_notes', 'audit_location', 'audit_aisle']
        widgets = {
            'physical_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'variance_reason': forms.Select(attrs={'class': 'form-control'}),
            'variance_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes about variance'}),
            'audit_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Physical location during count'}),
            'audit_aisle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aisle/section'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If this is an existing audit item, show current system quantities as reference
        if self.instance and self.instance.pk:
            system_qty = self.instance.system_quantity
            self.fields['physical_count'].help_text = f"System quantity: {system_qty}"

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Calculate variance when saving
        if instance.physical_count is not None:
            instance.variance_quantity = instance.physical_count - instance.system_quantity
            
        if commit:
            instance.save()
        return instance


class AuditItemBulkCountForm(forms.Form):
    """Form for bulk counting multiple items in an audit"""
    audit_items = forms.ModelMultipleChoiceField(
        queryset=StockAuditItem.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        audit = kwargs.pop('audit', None)
        super().__init__(*args, **kwargs)
        
        if audit:
            # Only show items that haven't been counted yet
            uncounted_items = audit.audit_items.filter(physical_count__isnull=True)
            self.fields['audit_items'].queryset = uncounted_items
            
            # Dynamically create fields for each audit item
            for item in uncounted_items:
                if item.stock and item.stock.item_name:  # Ensure item and stock exist
                    field_name = f'count_{item.id}'
                    self.fields[field_name] = forms.IntegerField(
                        required=False,
                        min_value=0,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control', 
                            'placeholder': f'Count for {item.stock.item_name}'
                        }),
                        label=f'{item.stock.item_name} (System: {item.system_quantity})'
                    )
    
    def save(self, audit, counted_by):
        """Save the bulk counts to audit items"""
        from django.utils import timezone
        updated_items = []
        
        for field_name, value in self.cleaned_data.items():
            if field_name and field_name.startswith('count_') and value is not None:
                item_id_str = field_name.replace('count_', '')
                if item_id_str.isdigit():  # Ensure we have a valid numeric ID
                    try:
                        audit_item = audit.audit_items.get(id=int(item_id_str))
                        audit_item.physical_count = value
                        audit_item.variance_quantity = value - audit_item.system_quantity
                        audit_item.counted_by = counted_by
                        audit_item.count_date = timezone.now()
                        audit_item.save()
                        updated_items.append(audit_item)
                    except (StockAuditItem.DoesNotExist, ValueError):
                        continue
        
        return updated_items
