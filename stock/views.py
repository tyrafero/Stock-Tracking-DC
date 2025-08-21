import csv
import os
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
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
    u = User(user=ip)
    result = User.objects.filter(Q(user__icontains=ip))
    if len(result) == 1:
        pass
    else:
        u.save()
        return ip
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
    return render(request, 'stock/home.html', context)


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
            from django.utils import timezone
            StockHistory.objects.create(
                category=stock.category,
                item_name=stock.item_name,
                quantity=stock.quantity,
                issue_quantity=0,
                receive_quantity=stock.quantity,
                received_by=request.user.username,
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
            from django.utils import timezone
            quantity_change = updated_stock.quantity - old_quantity
            
            StockHistory.objects.create(
                category=updated_stock.category,
                item_name=updated_stock.item_name,
                quantity=updated_stock.quantity,
                issue_quantity=0 if quantity_change >= 0 else abs(quantity_change),
                receive_quantity=quantity_change if quantity_change >= 0 else 0,
                received_by=request.user.username if quantity_change >= 0 else None,
                issued_by=request.user.username if quantity_change < 0 else None,
                created_by=request.user.username,
                last_updated=timezone.now(),
                timestamp=timezone.now()
            )
            
            messages.success(request, 'Successfully Updated!')
            return redirect('/view_stock')
            
    context = {'form': form, 'update': update, 'title': title}
    return render(request, 'stock/add_stock.html', context)


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
                issued_to=value.issued_to,
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


