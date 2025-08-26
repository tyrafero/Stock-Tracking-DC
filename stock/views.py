import csv
import os
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from .form import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse

# Create your views here.


def new_register(request):
    form = UserCreationForm
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login/')
    context = {'form': form}
    return render(request, 'stock/register.html', context)


@login_required
def get_client_ip(request):
    labels = []
    label_item = []
    data = []
    issue_data = []
    receive_data = []
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    u = User(username=ip)
    result = User.objects.filter(Q(username__icontains=ip))
    
    if len(result) == 1:
        pass
    else:
        u.save()
        # Don't return here - continue to render the template
    
    queryset = Stock.objects.all()
    querys = Category.objects.all()
    for chart in queryset:
        label_item.append(chart.item_name)
        data.append(chart.quantity)
        issue_data.append(chart.issue_quantity)
        receive_data.append(chart.receive_quantity)
    for chart in querys:
        labels.append(str(chart.group))

    count = User.objects.all().count()
    body = Category.objects.values('stock').count()
    mind = Category.objects.values('stockhistory').count()
    soul = Category.objects.values('group').count()
    
    context = {
        'count': count,
        'body': body,
        'mind': mind,
        'soul': soul,
        'labels': labels,
        'data': data,
        'issue_data': issue_data,
        'receive_data': receive_data,
        'label_item': label_item
    }
    return render(request, 'stock/home.html', context)  # ✅ Always return HttpResponse


@login_required
def view_stock(request):
    title = "VIEW STOCKS"
    everything = Stock.objects.all()
    form = StockSearchForm(request.POST or None)

    context = {'everything': everything, 'form': form}
    if request.method == 'POST':
        category = form['category'].value()
        everything = Stock.objects.filter(item_name__icontains=form['item_name'].value())
        if category != '':
            everything = everything.filter(category_id=category)

        if form['export_to_CSV'].value() == True:
            resp = HttpResponse(content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename = "Invoice.csv"'
            writer = csv.writer(resp)
            writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
            instance = everything
            for stock in instance:
                writer.writerow([stock.category, stock.item_name, stock.quantity])
            return resp
        context = {'title': title, 'everything': everything, 'form': form}
    return render(request, 'stock/view_stock.html', context)


@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        # Search in Stock items
        stocks = Stock.objects.filter(
            Q(item_name__icontains=query) |
            Q(category__group__icontains=query)
        )
        results = stocks
    else:
        # If no search query, show all stocks
        results = Stock.objects.all()
    
    context = {
        'query': query,
        'results': results,
        'title': 'Search Results' if query else 'All Items'
    }
    
    return render(request, 'stock/search_results.html', context)


def live_search(request):
    """AJAX endpoint for live search suggestions"""
    if not request.user.is_authenticated:
        return JsonResponse({'suggestions': []})
        
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    if query and len(query) >= 2:  # Only search if query is at least 2 characters
        # Search in Stock items (limit to 10 results for performance)
        stocks = Stock.objects.filter(
            Q(item_name__icontains=query) |
            Q(category__group__icontains=query)
        ).select_related('category')[:10]
        
        suggestions = [{
            'id': stock.id,
            'item_name': stock.item_name,
            'category': stock.category.group if stock.category else 'No Category',
            'quantity': stock.quantity,
            'image_url': stock.image.url if stock.image else None,
            'low_stock': stock.quantity <= stock.re_order
        } for stock in stocks]
    
    return JsonResponse({'suggestions': suggestions})


@login_required
def scrum_list(request):
    title = 'Add List'
    add = ScrumTitles.objects.all()
    sub = Scrums.objects.all()
    if request.method == 'POST':
        form = AddScrumListForm(request.POST, prefix='banned')
        if form.is_valid():
            form.save()
    else:
        form = AddScrumListForm(prefix='banned')
    if request.method == 'POST' and not form:
        task_form = AddScrumTaskForm(request.POST, prefix='expected')
        form = AddScrumListForm(prefix='banned')
        if task_form.is_valid():
            task_form.save()
    else:
        task_form = AddScrumTaskForm(prefix='expected')
    context = {'add': add, 'form': form, 'task_form': task_form, 'sub': sub, 'title': title}
    return render(request, 'stock/scrumboard.html', context)





@login_required
def scrum_view(request):
    title = 'View'
    viewers = ScrumTitles.objects.all()
    context = {'title': title, 'view': viewers}
    return render(request, 'stock/scrumboard.html', context)


@login_required
def add_stock(request):
    title = 'Add Stock'
    if request.method == 'POST':
        print("\n=== ADD STOCK DEBUG ===")
        print("POST:", request.POST)
        print("FILES:", request.FILES)
        
        # Debug Django/Cloudinary configuration
        print("\n=== ENVIRONMENT DEBUG ===")
        from django.conf import settings
        import os
        print(f"DEBUG: {settings.DEBUG}")
        print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
        print(f"CLOUDINARY_CLOUD_NAME set: {'Yes' if os.getenv('CLOUDINARY_CLOUD_NAME') else 'No'}")
        print(f"CLOUDINARY_API_KEY set: {'Yes' if os.getenv('CLOUDINARY_API_KEY') else 'No'}")
        print(f"CLOUDINARY_API_SECRET set: {'Yes' if os.getenv('CLOUDINARY_API_SECRET') else 'No'}")
        
        # Test Cloudinary configuration
        try:
            import cloudinary
            config = cloudinary.config()
            print(f"Cloudinary cloud_name: {config.cloud_name}")
            print(f"Cloudinary configured: {'Yes' if config.cloud_name else 'No'}")
        except Exception as e:
            print(f"Cloudinary config error: {e}")
        
        form = StockCreateForm(request.POST, request.FILES)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_by = request.user.username
            
            # Set default note for new stock
            if not stock.note:
                stock.note = "Fresh Stock"
            
            stock.save()
            
            # Debug the saved image
            print("\n=== IMAGE DEBUG ===")
            print(f"Image field: {stock.image}")
            if stock.image:
                print(f"Image name: {stock.image.name}")
                print(f"Image URL: {stock.image.url}")
                print(f"Image storage: {type(stock.image.storage)}")
                # Test if we can get image info
                try:
                    print(f"Image size: {stock.image.size} bytes")
                except Exception as e:
                    print(f"Error getting image size: {e}")
            else:
                print("No image was saved!")
            
            # CREATE HISTORY RECORD
            StockHistory.objects.create(
                category=stock.category,
                item_name=stock.item_name,
                quantity=stock.quantity,
                issue_quantity=0,
                receive_quantity=stock.quantity,
                received_by=request.user.username,
                note="Fresh Stock",  # Single note field
                created_by=request.user.username,
                last_updated=timezone.now(),
                timestamp=timezone.now()
            )
            
            print("=== STOCK AND HISTORY CREATED ===")
            messages.success(request, f'Successfully added {stock.item_name} to stock!')
            return redirect('view_stock')
        else:
            print("=== FORM ERRORS ===")
            print(form.errors)
            messages.error(request, 'Failed to add stock. Please check the form.')
    else:
        form = StockCreateForm()
    
    # Include 'add' variable for template compatibility
    add = Stock.objects.all()
    context = {
        'add': add,
        'form': form,
        'title': title
    }
    return render(request, 'stock/add_stock.html', context)

from django.http import JsonResponse
import os
from django.conf import settings

def debug_info(request):
    """Debug view to check configuration - remove after testing"""
    try:
        import cloudinary
        config = cloudinary.config()
        cloudinary_info = {
            'configured': bool(config.cloud_name),
            'cloud_name': config.cloud_name or 'NOT SET'
        }
    except Exception as e:
        cloudinary_info = {'error': str(e)}
    
    debug_data = {
        'DEBUG': settings.DEBUG,
        'DEFAULT_FILE_STORAGE': getattr(settings, 'DEFAULT_FILE_STORAGE', 'Django default'),
        'environment_vars': {
            'CLOUDINARY_CLOUD_NAME': 'SET' if os.getenv('CLOUDINARY_CLOUD_NAME') else 'NOT SET',
            'CLOUDINARY_API_KEY': 'SET' if os.getenv('CLOUDINARY_API_KEY') else 'NOT SET',
            'CLOUDINARY_API_SECRET': 'SET' if os.getenv('CLOUDINARY_API_SECRET') else 'NOT SET',
        },
        'cloudinary': cloudinary_info
    }
    
    return JsonResponse(debug_data, indent=2)

@login_required
def update_stock(request, pk):
    title = 'Update Stock'
    update = Stock.objects.get(id=pk)
    old_quantity = update.quantity  # Store old quantity
    form = StockUpdateForm(instance=update)
    
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, request.FILES, instance=update)
        if form.is_valid():
            # Remove old image if exists
            if update.image and os.path.exists(update.image.path):
                os.remove(update.image.path)
            
            updated_stock = form.save()
            
            # CREATE HISTORY RECORD
            quantity_change = updated_stock.quantity - old_quantity
            
            # Determine note based on quantity change
            if quantity_change >= 0:
                note = "Stock Updated - Quantity Increased"
            else:
                note = "Stock Updated - Quantity Decreased"
            
            StockHistory.objects.create(
                category=updated_stock.category,
                item_name=updated_stock.item_name,
                quantity=updated_stock.quantity,
                issue_quantity=0 if quantity_change >= 0 else abs(quantity_change),
                receive_quantity=quantity_change if quantity_change >= 0 else 0,
                received_by=request.user.username if quantity_change >= 0 else None,
                issued_by=request.user.username if quantity_change < 0 else None,
                note=note,  # Single note field
                created_by=request.user.username,
                last_updated=timezone.now(),
                timestamp=timezone.now()
            )
            
            messages.success(request, 'Successfully Updated!')
            return redirect('/view_stock')
    
    context = {'form': form, 'update': update, 'title': title}
    return render(request, 'stock/add_stock.html', context)

@login_required
def issue_stock(request, pk):
    """Handle stock issuing with notes"""
    stock = Stock.objects.get(id=pk)
    
    if request.method == 'POST':
        form = IssueForm(request.POST, instance=stock)
        if form.is_valid():
            issue_quantity = form.cleaned_data['issue_quantity']
            note = form.cleaned_data.get('note', '')  # Get note from form
            
            if issue_quantity <= stock.quantity:
                # Update stock
                stock.quantity -= issue_quantity
                stock.issued_by = request.user.username
                stock.note = note  # Store in single note field
                stock.save()
                
                # Create history record
                StockHistory.objects.create(
                    category=stock.category,
                    item_name=stock.item_name,
                    quantity=stock.quantity,
                    issue_quantity=issue_quantity,
                    receive_quantity=0,
                    issued_by=request.user.username,
                    note=note,  # Single note field
                    created_by=request.user.username,
                    last_updated=timezone.now(),
                    timestamp=timezone.now()
                )
                
                messages.success(request, f'Successfully issued {issue_quantity} {stock.item_name}!')
                return redirect('view_stock')
            else:
                messages.error(request, 'Cannot issue more than available stock!')
    else:
        form = IssueForm(instance=stock)
    
    context = {'form': form, 'stock': stock}
    return render(request, 'stock/issue_stock.html', context)

@login_required
def receive_stock(request, pk):
    """Handle stock receiving with notes"""
    stock = Stock.objects.get(id=pk)
    
    if request.method == 'POST':
        form = ReceiveForm(request.POST, instance=stock)
        if form.is_valid():
            receive_quantity = form.cleaned_data['receive_quantity']
            note = form.cleaned_data.get('note', '')  # Get note from form
            
            # Update stock
            stock.quantity += receive_quantity
            stock.received_by = request.user.username
            stock.note = note  # Store in single note field
            stock.save()
            
            # Create history record
            StockHistory.objects.create(
                category=stock.category,
                item_name=stock.item_name,
                quantity=stock.quantity,
                issue_quantity=0,
                receive_quantity=receive_quantity,
                received_by=request.user.username,
                note=note,  # Single note field
                created_by=request.user.username,
                last_updated=timezone.now(),
                timestamp=timezone.now()
            )
            
            messages.success(request, f'Successfully received {receive_quantity} {stock.item_name}!')
            return redirect('view_stock')
    else:
        form = ReceiveForm(instance=stock)
    
    context = {'form': form, 'stock': stock}
    return render(request, 'stock/receive_stock.html', context)

@login_required
def delete_stock(request, pk):
    # Get stock item before deleting to create history record
    stock_item = Stock.objects.get(id=pk)
    
    # CREATE HISTORY RECORD FOR DELETION
    from django.utils import timezone
    StockHistory.objects.create(
        category=stock_item.category,
        item_name=f"DELETED: {stock_item.item_name}",
        quantity=0,
        issue_quantity=stock_item.quantity,  # All quantity is "issued" (removed)
        receive_quantity=0,
        issued_by=request.user.username,
        created_by=request.user.username,
        note=f"Stock deleted by {request.user.username}",
        last_updated=timezone.now(),
        timestamp=timezone.now()
    )
    
    # Delete the stock item
    stock_item.delete()
    messages.success(request, 'Your file has been deleted.')
    return redirect('/view_stock')


@login_required
def stock_detail(request, pk):
    detail = Stock.objects.get(id=pk)
    context = {
        'detail': detail
    }
    return render(request, 'stock/stock_detail.html', context)


@login_required
def issue_item(request, pk):
    issue = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=issue)
    if form.is_valid():
        value = form.save(commit=False)
        value.receive_quantity = 0
        value.quantity = value.quantity - value.issue_quantity
        value.issued_by = str(request.user)
        if value.quantity >= 0:
            value.save()
            
            # CREATE HISTORY RECORD
            from django.utils import timezone
            StockHistory.objects.create(
                category=value.category,
                item_name=value.item_name,
                quantity=value.quantity,
                issue_quantity=value.issue_quantity,
                receive_quantity=0,
                issued_by=value.issued_by,
                note=value.note,
                created_by=str(request.user),
                last_updated=timezone.now(),
                timestamp=timezone.now()
            )
            
            messages.success(request, "Issued Successfully, " + str(value.quantity) + " " + str(value.item_name) + "s now left in Store")
        else:
            messages.error(request, "Insufficient Stock")
        return redirect('/stock_detail/' + str(value.id))
    
    context = {
        "title": 'Issue ' + str(issue.item_name),
        "issue": issue,
        "form": form,
        "username": 'Issued by: ' + str(request.user),
    }
    return render(request, "stock/add_stock.html", context)


@login_required
def receive_item(request, pk):
    print(f"=== RECEIVE_ITEM DEBUG ===")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    print(f"PK received: {pk}")
    
    receive = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=receive)
    
    if request.method == "POST":
        print(f"POST data: {request.POST}")
        print(f"Button clicked: {'receive_submit' in request.POST}")
        print(f"Form is valid: {form.is_valid()}")
        
        # Check if the correct submit button was clicked
        if 'receive_submit' not in request.POST:
            print("ERROR: Wrong form was submitted!")
            return redirect('receive_item', pk=pk)
        
        if form.is_valid():
            value = form.save(commit=False)
            value.issue_quantity = 0
            value.quantity = value.quantity + value.receive_quantity
            value.received_by = str(request.user)
            value.edited_by = str(request.user)
            value.save()
            
            # CREATE HISTORY RECORD
            from django.utils import timezone  # Import moved here
            StockHistory.objects.create(
                category=value.category,
                item_name=value.item_name,
                quantity=value.quantity,
                issue_quantity=0,
                receive_quantity=value.receive_quantity,
                received_by=value.received_by,
                note=value.note,
                created_by=str(request.user),
                last_updated=timezone.now(),
                timestamp=timezone.now()
            )
            
            messages.success(
                request,
                f"Received Successfully, {value.quantity} {value.item_name}s now in Store"
            )
            return redirect('stock_detail', pk=value.id)
        else:
            print(f"Form errors: {form.errors}")
    
    context = {
        "title": f"Receive {receive.item_name}",
        "receive": receive,
        "form": form,
        "username": f"Received by: {request.user}",
    }
    print(f"Rendering template with context: {list(context.keys())}")
    return render(request, "stock/add_stock.html", context)


@login_required
def re_order(request, pk):
    order = Stock.objects.get(id=pk)
    form = ReorderLevelForm(request.POST or None, instance=order)
    if form.is_valid():
        value = form.save(commit=False)
        value.save()
        messages.success(request, 'Reorder level for ' + str(value.item_name) + ' is updated to ' + str(value.re_order))
        return redirect('/view_stock')
    context = {
        'value': order,
        'form': form
    }
    return render(request, 'stock/add_stock.html', context)


@login_required()
def view_history(request):
    print("=== VIEW HISTORY DEBUG START ===")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    
    try:
        title = "STOCK HISTORY"
        history = StockHistory.objects.all()
        print(f"Total StockHistory records: {history.count()}")
        
        # ✅ Add row_class to each record for coloring
        for record in history:
            if record.issue_quantity and record.issue_quantity > 0:
                record.row_class = "table-success"   # Green row when issued
            elif record.receive_quantity and record.receive_quantity > 0:
                record.row_class = "table-danger"    # Red row when received
            else:
                record.row_class = ""                # Default

        # Debug: show first 5 records with row_class
        for record in history[:5]:
            print(f"Record: {record.item_name}, Issue: {record.issue_quantity}, "
                  f"Receive: {record.receive_quantity}, RowClass: {record.row_class}")
        
        form = StockHistorySearchForm(request.POST or None)
        print(f"Form created successfully")
        
        context = {
            'title': title,
            'history': history,
            'form': form
        }
        
        if request.method == 'POST':
            print("Processing POST request...")
            print("POST data:", dict(request.POST))
            
            try:
                print("Form is_valid check...")
                if form.is_valid():
                    print("Form is valid!")
                    # Filtering logic can stay here if needed
                    context = {
                        'title': title,
                        'history': history,
                        'form': form
                    }
                else:
                    print("Form is invalid!")
                    print("Form errors:", form.errors)
            except Exception as e:
                print(f"Error in form validation: {e}")
                import traceback
                traceback.print_exc()
        
        print("About to render template...")
        return render(request, 'stock/view_history.html', context)
    
    except Exception as e:
        print(f"ERROR in view_history: {e}")
        import traceback
        traceback.print_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error: {e}")

    print("=== VIEW HISTORY DEBUG END ===")


@login_required
def dependent_forms(request):
    title = 'Dependent Forms'
    form = DependentDropdownForm()
    if request.method == 'POST':
        form = DependentDropdownForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, str(form['name'].value()) + ' Successfully Added!')
            return redirect('/depend_form_view')
    context = {'form': form, 'title': title}
    return render(request, 'stock/add_stock.html', context)


@login_required
def dependent_forms_update(request, pk):
    title = 'Update Form'
    dependent_update = Person.objects.get(id=pk)
    form = DependentDropdownForm(instance=dependent_update)
    if request.method == 'POST':
        form = DependentDropdownForm(request.POST, instance=dependent_update)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Updated!')
            return redirect('/depend_form_view')
    context = {
        'title': title,
        'dependent_update': dependent_update,
        'form': form
    }
    return render(request, 'stock/add_stock.html', context)


@login_required
def dependent_forms_view(request):
    title = 'Dependent Views'
    viewers = Person.objects.all()
    context = {'title': title, 'view': viewers}
    return render(request, 'stock/depend_form_view.html', context)


@login_required
def delete_dependant(request, pk):
    Person.objects.get(id=pk).delete()
    messages.success(request, 'Your file has been deleted.')
    return redirect('/depend_form_view')


def load_stats(request):
    country_idm = request.GET.get('country_id')
    states = State.objects.filter(country_id=country_idm)
    context = {'states': states}
    return render(request, 'stock/state_dropdown_list_options.html', context)


def load_cities(request):
    state_main_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_main_id)
    context = {'cities': cities}
    return render(request, 'stock/city_dropdown_list_options.html', context)


@login_required
def contact(request):
    title = 'Contacts'
    people = Contacts.objects.all()
    form = ContactsForm(request.POST or None)
    if request.method == 'POST':
        form = ContactsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Added')
            return redirect('/contacts')
    context = {'people': people, 'form': form, 'title': title}
    return render(request, 'stock/contacts.html', context)


# stock/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction

@login_required
def purchase_order_list(request):
    form = PurchaseOrderSearchForm(request.GET or None)
    purchase_orders = PurchaseOrder.objects.all().select_related('manufacturer', 'created_by')
    if form.is_valid():
        if ref := form.cleaned_data.get('reference_number'):
            purchase_orders = purchase_orders.filter(reference_number__icontains=ref)
        if manufacturer := form.cleaned_data.get('manufacturer'):
            purchase_orders = purchase_orders.filter(manufacturer=manufacturer)
        if status := form.cleaned_data.get('status'):
            purchase_orders = purchase_orders.filter(status=status)
    context = {
        'title': 'Purchase Orders',
        'purchase_orders': purchase_orders,
        'form': form,
    }
    return render(request, 'stock/purchase_order_list.html', context)

@login_required
def create_purchase_order(request):
    if request.method == 'POST':
        po_form = PurchaseOrderForm(request.POST)
        item_formset = PurchaseOrderItemFormSet(request.POST)
        if po_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():
                    purchase_order = po_form.save(commit=False)
                    purchase_order.created_by = request.user
                    purchase_order.save()
                    item_formset.instance = purchase_order
                    item_formset.save()
                    PurchaseOrderHistory.objects.create(
                        purchase_order=purchase_order,
                        action='created',
                        notes='Purchase order created',
                        created_by=request.user
                    )
                    if request.POST.get('action') == 'submit':
                        purchase_order.status = 'submitted'
                        purchase_order.submitted_at = timezone.now()
                        purchase_order.save()
                        PurchaseOrderHistory.objects.create(
                            purchase_order=purchase_order,
                            action='submitted',
                            notes='Purchase order submitted',
                            created_by=request.user
                        )
                    messages.success(request, f'Purchase Order {purchase_order.reference_number} created successfully!')
                    return redirect('purchase_order_detail', pk=purchase_order.pk)
            except Exception as e:
                messages.error(request, f'Error creating purchase order: {str(e)}')
        else:
            print(po_form.errors)
            print(item_formset.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        po_form = PurchaseOrderForm()
        item_formset = PurchaseOrderItemFormSet()
    context = {
        'title': 'Create Purchase Order',
        'po_form': po_form,
        'item_formset': item_formset,
    }
    return render(request, 'stock/create_purchase_order.html', context)

@login_required
def purchase_order_detail(request, pk):
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    context = {
        'title': f'Purchase Order - {purchase_order.reference_number}',
        'purchase_order': purchase_order,
        'items': purchase_order.items.all(),
    }
    return render(request, 'stock/purchase_order_detail.html', context)

@login_required
def update_purchase_order(request, pk):
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    if purchase_order.status not in ['draft', 'submitted']:
        messages.error(request, 'This purchase order cannot be modified.')
        return redirect('purchase_order_detail', pk=pk)
    if request.method == 'POST':
        po_form = PurchaseOrderForm(request.POST, instance=purchase_order)
        item_formset = PurchaseOrderItemFormSet(request.POST, instance=purchase_order)
        if po_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():
                    po_form.save()
                    item_formset.save()
                    PurchaseOrderHistory.objects.create(
                        purchase_order=purchase_order,
                        action='updated',
                        notes='Purchase order updated',
                        created_by=request.user
                    )
                    if request.POST.get('action') == 'submit':
                        purchase_order.status = 'submitted'
                        purchase_order.submitted_at = timezone.now()
                        purchase_order.save()
                        PurchaseOrderHistory.objects.create(
                            purchase_order=purchase_order,
                            action='submitted',
                            notes='Purchase order submitted',
                            created_by=request.user
                        )
                    messages.success(request, f'Purchase Order {purchase_order.reference_number} updated successfully!')
                    return redirect('purchase_order_detail', pk=purchase_order.pk)
            except Exception as e:
                messages.error(request, f'Error updating purchase order: {str(e)}')
        else:
            print(po_form.errors)
            print(item_formset.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        po_form = PurchaseOrderForm(instance=purchase_order)
        item_formset = PurchaseOrderItemFormSet(instance=purchase_order,
                                                form_kwargs={'edit_mode': True})  # Edit mode

    context = {
        'title': f'Update Purchase Order - {purchase_order.reference_number}',
        'po_form': po_form,
        'item_formset': item_formset,
        'purchase_order': purchase_order,
    }
    return render(request, 'stock/create_purchase_order.html', context)

@login_required
def submit_purchase_order(request, pk):
    if request.method == 'POST':
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
        if purchase_order.status == 'draft':
            purchase_order.status = 'submitted'
            purchase_order.submitted_at = timezone.now()
            purchase_order.save()
            PurchaseOrderHistory.objects.create(
                purchase_order=purchase_order,
                action='submitted',
                notes='Purchase order submitted',
                created_by=request.user
            )
            messages.success(request, f'Purchase Order {purchase_order.reference_number} submitted successfully!')
        else:
            messages.error(request, 'Purchase order cannot be submitted.')
    return redirect('purchase_order_detail', pk=pk)

@login_required
def send_purchase_order_email(request, pk):
    if request.method == 'POST':
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
        if purchase_order.status not in ['submitted', 'sent']:
            messages.error(request, 'Purchase order must be submitted before sending.')
            return redirect('purchase_order_detail', pk=pk)
        try:
            context = {
                'purchase_order': purchase_order,
                'items': purchase_order.items.all(),
                'company_name': getattr(settings, 'COMPANY_NAME', 'Your Company'),
            }
            email_subject = f'Purchase Order {purchase_order.reference_number}'
            email_body = render_to_string('stock/email/purchase_order_email.html', context)
            recipient_emails = [purchase_order.manufacturer.company_email]
            if purchase_order.manufacturer.additional_email:
                recipient_emails.append(purchase_order.manufacturer.additional_email)
            send_mail(
                subject=email_subject,
                message='',
                html_message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                fail_silently=False,
            )
            purchase_order.status = 'sent'
            purchase_order.sent_at = timezone.now()
            purchase_order.save()
            PurchaseOrderHistory.objects.create(
                purchase_order=purchase_order,
                action='sent',
                notes=f'Purchase order sent to {", ".join(recipient_emails)}',
                created_by=request.user
            )
            messages.success(request, f'Purchase Order {purchase_order.reference_number} sent successfully!')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
    return redirect('purchase_order_detail', pk=pk)

@login_required
def receive_purchase_order_items(request, pk):
    """Main receiving interface - shows all items and allows bulk receiving"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Check if PO is in a receivable state
    if purchase_order.status not in ['sent', 'confirmed', 'completed']:
        messages.error(request, 'This purchase order is not ready for receiving items.')
        return redirect('purchase_order_detail', pk=pk)
    
    if request.method == 'POST':
        form = BulkReceivingForm(request.POST, purchase_order=purchase_order)
        if form.is_valid():
            try:
                with transaction.atomic():
                    receiving_data = form.get_receiving_data()
                    created_records = []
                    
                    for item_data in receiving_data:
                        item = get_object_or_404(PurchaseOrderItem, pk=item_data['item_pk'])
                        
                        # Create receiving record
                        receiving_record = PurchaseOrderReceiving.objects.create(
                            purchase_order_item=item,
                            quantity_received=item_data['quantity'],
                            delivery_reference=item_data['delivery_reference'],
                            notes=item_data['notes'],
                            received_by=request.user
                        )
                        created_records.append(receiving_record)
                    
                    # Create history entry
                    total_items = sum(r.quantity_received for r in created_records)
                    products_received = ', '.join([f"{r.purchase_order_item.product} ({r.quantity_received})" 
                                                 for r in created_records])
                    
                    PurchaseOrderHistory.objects.create(
                        purchase_order=purchase_order,
                        action='updated',
                        notes=f'Items received: {products_received}',
                        created_by=request.user
                    )
                    
                    messages.success(
                        request, 
                        f'Successfully received {total_items} items across {len(created_records)} products!'
                    )
                    return redirect('receive_purchase_order_items', pk=pk)
                    
            except Exception as e:
                messages.error(request, f'Error receiving items: {str(e)}')
    else:
        form = BulkReceivingForm(purchase_order=purchase_order)
    
    # Get receiving records for display
    receiving_records = PurchaseOrderReceiving.objects.filter(
        purchase_order_item__purchase_order=purchase_order
    ).select_related('purchase_order_item', 'received_by').order_by('-received_at')
    
    context = {
        'title': f'Receive Items - {purchase_order.reference_number}',
        'purchase_order': purchase_order,
        'form': form,
        'receiving_records': receiving_records,
        'items_with_progress': _get_items_with_progress(purchase_order),
    }
    
    return render(request, 'stock/receive_purchase_order_items.html', context)




@login_required
def purchase_order_receiving_history(request, pk):
    """View complete receiving history for a purchase order"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    receiving_records = PurchaseOrderReceiving.objects.filter(
        purchase_order_item__purchase_order=purchase_order
    ).select_related('purchase_order_item', 'received_by').order_by('-received_at')
    
    # Calculate statistics
    total_items_received = sum(record.quantity_received for record in receiving_records)
    unique_products_affected = receiving_records.values('purchase_order_item').distinct().count()
    
    context = {
        'title': f'Receiving History - {purchase_order.reference_number}',
        'purchase_order': purchase_order,
        'receiving_records': receiving_records,
        'total_items_received': total_items_received,
        'unique_products_affected': unique_products_affected,
    }
    
    return render(request, 'stock/receive_purchase_order_item.html', context)


@login_required
def receiving_summary_api(request, pk):
    """API endpoint for receiving summary data"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    items_data = []
    for item in purchase_order.items.all():
        items_data.append({
            'id': item.pk,
            'product': item.product,
            'ordered': item.quantity,
            'received': item.total_received_quantity,
            'remaining': item.remaining_quantity,
            'status': item.receiving_status,
            'progress_percentage': round((item.total_received_quantity / item.quantity) * 100, 1),
            'is_complete': item.is_fully_received,
        })
    
    summary = {
        'overall_status': purchase_order.overall_receiving_status,
        'total_items': purchase_order.items.count(),
        'completed_items': sum(1 for item in purchase_order.items.all() if item.is_fully_received),
        'total_deliveries': PurchaseOrderReceiving.objects.filter(
            purchase_order_item__purchase_order=purchase_order
        ).count(),
        'items': items_data
    }
    
    return JsonResponse(summary)


def _get_items_with_progress(purchase_order):
    """Helper function to get items with progress data"""
    items = []
    for item in purchase_order.items.all():
        progress_percentage = 0
        if item.quantity > 0:
            progress_percentage = round((item.total_received_quantity / item.quantity) * 100, 1)
        
        items.append({
            'item': item,
            'progress_percentage': progress_percentage,
            'status_class': {
                'not_received': 'danger',
                'partially_received': 'warning', 
                'fully_received': 'success'
            }.get(item.receiving_status, 'secondary')
        })
    
    return items


@login_required
def get_manufacturer_details(request):
    manufacturer_id = request.GET.get('manufacturer_id')
    if manufacturer_id:
        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
            data = {
                'company_name': manufacturer.company_name,
                'company_email': manufacturer.company_email,
                'additional_email': manufacturer.additional_email or '',
                'street_address': manufacturer.street_address,
                'city': manufacturer.city,
                'country': manufacturer.country,
                'region': manufacturer.region,
                'postal_code': manufacturer.postal_code,
                'company_telephone': manufacturer.company_telephone,
            }
            return JsonResponse(data)
        except Manufacturer.DoesNotExist:
            return JsonResponse({'error': 'Manufacturer not found'}, status=404)
    return JsonResponse({'error': 'No manufacturer ID provided'}, status=400)

# Management Views
@login_required
def manage_manufacturers(request):
    manufacturers = Manufacturer.objects.all()
    context = {'title': 'Manage Manufacturers', 'manufacturers': manufacturers}
    return render(request, 'stock/manage_manufacturers.html', context)

@login_required
def add_manufacturer(request):
    if request.method == 'POST':
        form = ManufacturerForm(request.POST)
        if form.is_valid():
            manufacturer = form.save()
            messages.success(request, f'Manufacturer "{manufacturer.company_name}" added successfully!')
            return redirect('manage_manufacturers')
    else:
        form = ManufacturerForm()
    context = {'title': 'Add Manufacturer', 'form': form}
    return render(request, 'stock/add_manufacturer.html', context)

@login_required
def edit_manufacturer(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    if request.method == 'POST':
        form = ManufacturerForm(request.POST, instance=manufacturer)
        if form.is_valid():
            manufacturer = form.save()
            messages.success(request, f'Manufacturer "{manufacturer.company_name}" updated successfully!')
            return redirect('manage_manufacturers')
    else:
        form = ManufacturerForm(instance=manufacturer)
    
    context = {
        'title': f'Edit Manufacturer - {manufacturer.company_name}', 
        'form': form, 
        'manufacturer': manufacturer  # This tells the template it's an edit
    }
    # Use the same template as add_manufacturer
    return render(request, 'stock/add_manufacturer.html', context)

@login_required
def delete_manufacturer(request, pk):
    if request.method == 'POST':
        manufacturer = get_object_or_404(Manufacturer, pk=pk)
        if manufacturer.purchaseorder_set.exists():
            messages.error(request, f'Cannot delete "{manufacturer.company_name}" as it has associated purchase orders.')
        else:
            manufacturer.delete()
            messages.success(request, f'Manufacturer "{manufacturer.company_name}" deleted successfully!')
    return redirect('manage_manufacturers')

@login_required
def manage_delivery_persons(request):
    delivery_persons = DeliveryPerson.objects.all()
    context = {'title': 'Manage Delivery Persons', 'delivery_persons': delivery_persons}
    return render(request, 'stock/manage_delivery_persons.html', context)

@login_required
def add_delivery_person(request):
    if request.method == 'POST':
        form = DeliveryPersonForm(request.POST)
        if form.is_valid():
            delivery_person = form.save()
            messages.success(request, f'Delivery person "{delivery_person.name}" added successfully!')
            return redirect('manage_delivery_persons')
    else:
        form = DeliveryPersonForm()
    
    context = {
        'title': 'Add Delivery Person', 
        'form': form,
        'delivery_person': None  # Explicitly set to None for add operation
    }
    return render(request, 'stock/add_delivery_person.html', context)

@login_required
def edit_delivery_person(request, pk):
    delivery_person = get_object_or_404(DeliveryPerson, pk=pk)
    if request.method == 'POST':
        form = DeliveryPersonForm(request.POST, instance=delivery_person)
        if form.is_valid():
            delivery_person = form.save()
            messages.success(request, f'Delivery person "{delivery_person.name}" updated successfully!')
            return redirect('manage_delivery_persons')
    else:
        form = DeliveryPersonForm(instance=delivery_person)
    
    context = {
        'title': f'Edit Delivery Person - {delivery_person.name}', 
        'form': form, 
        'delivery_person': delivery_person  # Pass the instance for edit operation
    }
    return render(request, 'stock/add_delivery_person.html', context)

@login_required
def delete_delivery_person(request, pk):
    if request.method == 'POST':
        delivery_person = get_object_or_404(DeliveryPerson, pk=pk)
        if delivery_person.purchaseorder_set.exists():
            messages.error(request, f'Cannot delete "{delivery_person.name}" as they have associated purchase orders.')
        else:
            delivery_person.delete()
            messages.success(request, f'Delivery person "{delivery_person.name}" deleted successfully!')
    return redirect('manage_delivery_persons')

@login_required
def manage_stores(request):
    stores = Store.objects.all()
    context = {'title': 'Manage Stores', 'stores': stores}
    return render(request, 'stock/manage_stores.html', context)

@login_required
def add_store(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save()
            messages.success(request, f'Store "{store.name}" added successfully!')
            return redirect('manage_stores')
    else:
        form = StoreForm()
    context = {'title': 'Add Store', 'form': form}
    return render(request, 'stock/add_store.html', context)

@login_required
def edit_store(request, pk):
    store = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            store = form.save()
            messages.success(request, f'Store "{store.name}" updated successfully!')
            return redirect('manage_stores')
    else:
        form = StoreForm(instance=store)
    context = {'title': f'Edit Store - {store.name}', 'form': form, 'store': store}
    return render(request, 'stock/edit_store.html', context)

@login_required
def delete_store(request, pk):
    if request.method == 'POST':
        store = get_object_or_404(Store, pk=pk)
        if store.purchaseorder_set.exists():
            messages.error(request, f'Cannot delete "{store.name}" as it has associated purchase orders.')
        else:
            store.delete()
            messages.success(request, f'Store "{store.name}" deleted successfully!')
    return redirect('manage_stores')

@login_required
def purchase_order_history(request, pk):
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    history = purchase_order.history.all()
    context = {
        'title': f'Purchase Order History - {purchase_order.reference_number}',
        'purchase_order': purchase_order,
        'history': history,
    }
    return render(request, 'stock/purchase_order_history.html', context)