from django import forms
from django.forms import inlineformset_factory
from .models import *


# fields = '__all__' to display all


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity', 'image', 'date']

    # def clean_category(self):
    #     category = self.cleaned_data.get('category')
    #     if not category:
    #         raise forms.ValidationError('This Field should not be empty')
    #     for something in Stock.objects.all():
    #         if something.category == category:
    #             raise forms.ValidationError(category + " Already Exists")
    #     return category
    #
    # def clean_item(self):
    #     item = self.cleaned_data.get('item_name')
    #     if not item:
    #         raise forms.ValidationError('This Field should not be empty')
    #     for something in Stock.objects.all():
    #         if something.category == item:
    #             raise forms.ValidationError(item + " Already Exists")
    #     return item


class StockHistorySearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)

    class Meta:
        model = StockHistory
        fields = ['category', 'item_name', 'start_date', 'end_date']


class StockSearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)

    class Meta:
        model = Stock
        fields = ['category', 'item_name']


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity', 'image']


class IssueForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['issue_quantity', 'issued_to']


class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['receive_quantity']


class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['re_order']


class DependentDropdownForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    state = forms.ModelChoiceField(queryset=State.objects.none())  # Add this line
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


class AddScrumListForm(forms.ModelForm):
    class Meta:

        model = ScrumTitles
        fields = ['lists']


class AddScrumTaskForm(forms.ModelForm):
    class Meta:
        model = Scrums
        fields = ['task', 'task_description', 'task_date']


class ContactsForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = '__all__'


from django import forms
from .models import Stock, Category, PurchaseOrder, PurchaseOrderItem, Manufacturer, DeliveryPerson, Store, Product
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML, Submit, Row, Column

class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity', 'receive_quantity', 'received_by', 'issue_quantity', 'issued_by', 'issued_to', 'phone_number', 're_order', 'image']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'receive_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'received_by': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'issued_by': forms.TextInput(attrs={'class': 'form-control'}),
            'issued_to': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            're_order': forms.NumberInput(attrs={'class': 'form-control'}),
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
                Column('quantity', css_class='form-group col-md-4'),
                Column('receive_quantity', css_class='form-group col-md-4'),
                Column('re_order', css_class='form-group col-md-4'),
            ),
            Row(
                Column('received_by', css_class='form-group col-md-4'),
                Column('issued_by', css_class='form-group col-md-4'),
                Column('issued_to', css_class='form-group col-md-4'),
            ),
            Row(Column('phone_number', css_class='form-group col-md-6')),
            Row(Column('image', css_class='form-group col-md-6')),
            Submit('submit', 'Save Stock', css_class='btn btn-primary')
        )

# Other forms (from previous response)
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
                HTML('<h5 class="mb-3">📋 PO Information</h5>'),
                Row(Column('note_for_manufacturer', css_class='form-group col-md-12 mb-3')),
                css_class='card card-inner mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">👤 Responsible Person</h5>'),
                Row(Column('delivery_person', css_class='form-group col-md-12 mb-3')),
                css_class='card card-inner mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">🏭 Manufacturer Information</h5>'),
                Row(Column('manufacturer', css_class='form-group col-md-12 mb-3')),
                HTML('<div id="manufacturer-details" class="mt-3"></div>'),
                css_class='card card-inner mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">🚚 Delivery Information</h5>'),
                Row(
                    Column('delivery_type', css_class='form-group col-md-6 mb-3'),
                    Column('store', css_class='form-group col-md-6 mb-3'),
                ),
                css_class='card card-inner mb-4'
            ),
            Submit('submit', 'Save Purchase Order', css_class='btn btn-primary')
        )
        self.fields['store'].required = False

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'associated_order_number', 'price_inc', 'quantity', 'discount_percent', 'received_quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'associated_order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Order #'}),
            'price_inc': forms.NumberInput(attrs={'class': 'form-control price-inc', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity', 'min': '1', 'placeholder': '1'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control discount-percent', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '0.00'}),
            'received_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
        }

    def __init__(self, *args, **kwargs):
        edit_mode = kwargs.pop('edit_mode', False)
        super().__init__(*args, **kwargs)
        self.fields['product'] = forms.CharField(widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Product Name'
        }))

        for field_name, field in self.fields.items():
            field.required = field_name in ['product', 'price_inc', 'quantity']

        # Only set price_inc if instance.product is a Product object
        product_instance = getattr(self.instance, 'product', None)
        if isinstance(product_instance, Product):
            self.fields['price_inc'].initial = product_instance.default_price_inc

        # received_quantity readonly in Add mode
        if not edit_mode:
            self.fields['received_quantity'].initial = 0
            self.fields['received_quantity'].widget.attrs['readonly'] = True
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=0,
    can_delete=True,
    min_num=0,
    validate_min=True,
)

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

from registration.forms import RegistrationForm
from django import forms

class CustomRegistrationForm(RegistrationForm):
    allowed_domains = ['digitalcinema.com.au','gmail.com']  # all emails ending with this domain
    allowed_specific_emails = ['atish.digitalcinema@gmail.com', ]  # individual allowed emails

    def clean_email(self):
        email = self.cleaned_data.get('email')
        domain = email.split('@')[-1]

        if domain in self.allowed_domains or email.lower() in [e.lower() for e in self.allowed_specific_emails]:
            return email

        raise forms.ValidationError(
            "Registration is only allowed with @dc.com.au emails or certain approved Gmail accounts."
        )
