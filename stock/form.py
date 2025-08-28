from django import forms
from django.forms import inlineformset_factory
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML, Submit, Row, Column
from registration.forms import RegistrationForm


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity', 'image']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact phone number'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('category', css_class='form-group col-md-6'),
                Column('item_name', css_class='form-group col-md-6'),
            ),
            Row(
                Column('quantity', css_class='form-group col-md-6'),
                Column('phone_number', css_class='form-group col-md-6'),
            ),
            Row(
                Column('note', css_class='form-group col-md-12'),
            ),
            Row(Column('image', css_class='form-group col-md-12')),
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
        fields = ['category', 'item_name', 'quantity', 'phone_number', 'image', 'note']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Update note'}),
        }


class IssueForm(forms.ModelForm):
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


class ReceiveForm(forms.ModelForm):
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


class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['re_order']
        widgets = {
            're_order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


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
        fields = ['note_for_manufacturer', 'manufacturer', 'delivery_person', 'delivery_type', 'store']
        widgets = {
            'note_for_manufacturer': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter notes for manufacturer...'}),
            'manufacturer': forms.Select(attrs={'class': 'form-control', 'id': 'id_manufacturer'}),
            'delivery_person': forms.Select(attrs={'class': 'form-control'}),
            'delivery_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_delivery_type'}),
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
                HTML('<h5 class="mb-3">Delivery Information</h5>'),
                Row(
                    Column('delivery_type', css_class='form-group col-md-6 mb-3'),
                    Column('store', css_class='form-group col-md-6 mb-3'),
                ),
                css_class='card card-inner mb-4'
            ),
        )
        self.fields['store'].required = False


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'associated_order_number', 'price_inc', 'quantity', 'discount_percent']
        widgets = {
            'product': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
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
        fields = ['company_name', 'company_email', 'additional_email', 'street_address', 'city', 'country', 'region', 'postal_code', 'company_telephone']
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
        fields = ['name', 'location', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('location', css_class='form-group col-md-6 mb-3'),
            ),
            Row(Column('address', css_class='form-group col-md-12 mb-3')),
            Row(Column('is_active', css_class='form-group col-md-12 mb-3')),
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