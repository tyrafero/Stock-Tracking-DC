import csv
import os
import re
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, F
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from .form import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from .utils.email_service import send_purchase_order_email_safe

# Create your views here.

@login_required
def pending_approval(request):
    """Show pending approval screen for users waiting for admin approval"""
    user_role = getattr(request.user, 'role', None)
    if not user_role or user_role.role != 'pending':
        return redirect('/')  # Redirect to home if not pending
    
    context = {
        'title': 'Account Pending Approval',
        'user': request.user,
    }
    return render(request, 'stock/pending_approval.html', context)

def create_flexible_search_query(query_text, search_field):
    """
    Create a flexible search Q object that handles partial matches, 
    different spacing, and hyphenation patterns.
    
    For example: "BenQ W2700" can match "w 2700", "2700", "w-2700", etc.
    """
    if not query_text or not query_text.strip():
        return Q()
    
    query = query_text.strip()
    queries = []
    
    # Original query (case-insensitive contains)
    queries.append(Q(**{f"{search_field}__icontains": query}))
    
    # Remove special characters and normalize spaces
    normalized_query = re.sub(r'[^\w\s]', ' ', query)
    normalized_query = ' '.join(normalized_query.split())  # Normalize whitespace
    
    if normalized_query != query:
        queries.append(Q(**{f"{search_field}__icontains": normalized_query}))
    
    # Split query into individual words and search for each
    words = normalized_query.split()
    if len(words) > 1:
        # All words must be present (AND logic)
        word_queries = Q()
        for word in words:
            if len(word) >= 2:  # Only search words with 2+ characters
                word_queries &= Q(**{f"{search_field}__icontains": word})
        
        if word_queries:
            queries.append(word_queries)
        
        # Also try with different separators
        for separator in ['-', '_', '']:
            combined = separator.join(words)
            if combined != query and combined != normalized_query:
                queries.append(Q(**{f"{search_field}__icontains": combined}))
    
    # If query contains numbers, also search for just the numbers
    numbers = re.findall(r'\d+', query)
    if numbers:
        for number in numbers:
            if len(number) >= 3:  # Only search numbers with 3+ digits
                queries.append(Q(**{f"{search_field}__icontains": number}))
    
    # Combine all queries with OR
    final_query = Q()
    for q in queries:
        final_query |= q
    
    return final_query


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
    """Main dashboard view that routes to role-specific dashboards"""
    from .utils.permissions import get_user_role
    
    # Check if user is authenticated and pending approval
    if request.user.is_authenticated:
        user_role = getattr(request.user, 'role', None)
        if user_role and user_role.role == 'pending':
            return redirect('pending_approval')
    
    # Track visitor IP (keeping original functionality)
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
    
    # Route to role-specific dashboard
    try:
        user_role = get_user_role(request.user)
        role_name = user_role.role
        
        if role_name in ['admin', 'owner']:
            return admin_dashboard(request)
        elif role_name == 'sales':
            return sales_dashboard(request)
        elif role_name == 'warehouse':
            return warehouse_dashboard(request)
        elif role_name == 'logistics':
            return logistics_dashboard(request)
        else:
            return admin_dashboard(request)  # Default fallback
            
    except Exception:
        return admin_dashboard(request)  # Fallback for users without roles


@login_required
def admin_dashboard(request):
    """Admin/Owner dashboard with full system overview"""
    labels = []
    label_item = []
    data = []
    issue_data = []
    receive_data = []
    
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
    
    # Get all alerts for admin
    pending_transfers = StockTransfer.objects.filter(status='pending').select_related('stock', 'from_location', 'to_location')
    in_transit_transfers = StockTransfer.objects.filter(status='in_transit').select_related('stock', 'from_location', 'to_location')
    awaiting_collection_transfers = StockTransfer.objects.filter(status='awaiting_collection').select_related('stock', 'from_location', 'to_location')
    active_commitments = CommittedStock.objects.filter(is_fulfilled=False).select_related('stock', 'committed_by')  # Uses model default ordering
    
    # Add active reservations for admin
    from django.utils import timezone
    active_reservations = StockReservation.objects.filter(
        status='active', 
        expires_at__gt=timezone.now()
    ).select_related('stock', 'reserved_by')  # Uses model default ordering
    
    # Admin-specific metrics
    low_stock_items = Stock.objects.filter(quantity__lte=models.F('re_order')).count()
    recent_pos = PurchaseOrder.objects.filter(status__in=['draft', 'submitted']).count()
    total_stock_value = sum(stock.quantity * 100 for stock in Stock.objects.all())  # Placeholder calculation
    
    context = {
        'dashboard_type': 'admin',
        'count': count,
        'body': body,
        'mind': mind,
        'soul': soul,
        'labels': labels,
        'data': data,
        'issue_data': issue_data,
        'receive_data': receive_data,
        'label_item': label_item,
        'pending_transfers': pending_transfers,
        'in_transit_transfers': in_transit_transfers,
        'awaiting_collection_transfers': awaiting_collection_transfers,
        'active_commitments': active_commitments,
        'active_reservations': active_reservations,
        'low_stock_items': low_stock_items,
        'recent_pos': recent_pos,
        'total_stock_value': total_stock_value,
    }
    return render(request, 'stock/dashboards/admin_dashboard.html', context)


@login_required
def sales_dashboard(request):
    """Sales dashboard focused on stock availability and customer commitments"""
    # Available stock for sales  
    available_stock = Stock.objects.filter(quantity__gt=0)  # Uses model default ordering (-last_updated)
    
    # Customer commitments
    active_commitments = CommittedStock.objects.filter(is_fulfilled=False).select_related('stock')  # Uses model default ordering
    
    # Active reservations (relevant for sales)
    from django.utils import timezone
    active_reservations = StockReservation.objects.filter(
        status='active', 
        expires_at__gt=timezone.now()
    ).select_related('stock', 'reserved_by')  # Uses model default ordering
    
    # Awaiting collection (relevant for sales)
    awaiting_collection = StockTransfer.objects.filter(
        status='awaiting_collection', 
        transfer_type='customer_collection'
    ).select_related('stock', 'to_location')
    
    # Recent sales activity (stock issues)
    recent_issues = Stock.objects.filter(issue_quantity__gt=0)[:10]  # Uses model default ordering
    
    # Sales metrics
    total_committed = CommittedStock.objects.filter(is_fulfilled=False).count()
    total_reserved = active_reservations.count()
    total_available = available_stock.count()
    
    context = {
        'dashboard_type': 'sales',
        'available_stock': available_stock[:20],  # Limit for performance
        'active_commitments': active_commitments[:10],
        'active_reservations': active_reservations[:10],
        'awaiting_collection': awaiting_collection,
        'recent_issues': recent_issues,
        'total_committed': total_committed,
        'total_reserved': total_reserved,
        'total_available': total_available,
    }
    return render(request, 'stock/dashboards/sales_dashboard.html', context)


@login_required
def warehouse_dashboard(request):
    """Warehouse dashboard focused on receiving, transfers, and location management"""
    # Pending receiving
    pending_pos = PurchaseOrder.objects.filter(
        status__in=['confirmed', 'sent']
    ).select_related('manufacturer')  # Uses model default ordering
    
    # Transfers requiring warehouse action
    pending_transfers = StockTransfer.objects.filter(status='pending').select_related('stock', 'from_location', 'to_location')
    in_transit_transfers = StockTransfer.objects.filter(status='in_transit').select_related('stock', 'from_location', 'to_location')
    
    # Recent receiving activity
    recent_receiving = PurchaseOrderReceiving.objects.select_related(
        'purchase_order_item__purchase_order', 'received_by'
    ).order_by('-received_at')[:10]
    
    # Stock by location
    stock_by_location = {}
    for location in Store.objects.filter(is_active=True):
        stock_count = StockLocation.objects.filter(store=location).count()
        stock_by_location[location.name] = stock_count
    
    context = {
        'dashboard_type': 'warehouse',
        'pending_pos': pending_pos[:10],
        'pending_transfers': pending_transfers,
        'in_transit_transfers': in_transit_transfers,
        'recent_receiving': recent_receiving,
        'stock_by_location': stock_by_location,
    }
    return render(request, 'stock/dashboards/warehouse_dashboard.html', context)


@login_required
def logistics_dashboard(request):
    """Logistics dashboard focused on purchase orders and supplier management"""
    # Purchase order overview
    draft_pos = PurchaseOrder.objects.filter(status='draft').count()
    sent_pos = PurchaseOrder.objects.filter(status='sent').count()
    confirmed_pos = PurchaseOrder.objects.filter(status='confirmed').count()
    
    # Recent PO activity
    recent_pos = PurchaseOrder.objects.select_related('manufacturer')[:10]  # Uses model default ordering
    
    # Stock forecasting - items approaching reorder level
    low_stock = Stock.objects.filter(
        quantity__lte=models.F('re_order'),
        re_order__gt=0
    ).order_by('quantity')[:20]
    
    # Transfer requests
    transfer_requests = StockTransfer.objects.filter(
        status__in=['pending', 'in_transit']
    ).select_related('stock', 'from_location', 'to_location')  # Uses model default ordering
    
    context = {
        'dashboard_type': 'logistics',
        'draft_pos': draft_pos,
        'sent_pos': sent_pos,
        'confirmed_pos': confirmed_pos,
        'recent_pos': recent_pos,
        'low_stock': low_stock,
        'transfer_requests': transfer_requests,
    }
    return render(request, 'stock/dashboards/logistics_dashboard.html', context)


@login_required
def view_stock(request):
    title = "VIEW STOCKS"
    everything = Stock.objects.all()
    form = StockSearchForm(request.POST or None)

    context = {'everything': everything, 'form': form}
    if request.method == 'POST':
        category = form['category'].value()
        item_name = form['item_name'].value()
        
        # Use flexible search for item names
        if item_name:
            item_search_query = create_flexible_search_query(item_name, 'item_name')
            everything = Stock.objects.filter(item_search_query)
        else:
            everything = Stock.objects.all()
            
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
        # Use flexible search for item names and category names
        item_search_query = create_flexible_search_query(query, 'item_name')
        category_search_query = create_flexible_search_query(query, 'category__group')
        
        # Combine searches with OR logic
        stocks = Stock.objects.filter(
            item_search_query | category_search_query
        ).select_related('category')
        
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
        # Use flexible search for item names and category names
        item_search_query = create_flexible_search_query(query, 'item_name')
        category_search_query = create_flexible_search_query(query, 'category__group')
        
        # Search in Stock items (limit to 10 results for performance)
        stocks = Stock.objects.filter(
            item_search_query | category_search_query
        ).select_related('category')[:10]
        
        suggestions = [{
            'id': stock.id,
            'item_name': stock.item_name,
            'category': stock.category.group if stock.category else 'No Category',
            'quantity': stock.total_across_locations,
            'image_url': stock.image.url if stock.image else None,
            'low_stock': stock.total_across_locations <= (stock.re_order or 0),
            'condition': stock.condition,
            'condition_display': stock.get_condition_display()
        } for stock in stocks]
    
    return JsonResponse({'suggestions': suggestions})

@login_required
def transfer_stock(request, pk):
    """Create a new stock transfer"""
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_transfer_stock'):
        messages.error(request, 'You do not have permission to transfer stock.')
        return redirect('/')
        
    stock = get_object_or_404(Stock, id=pk)
    
    if request.method == 'POST':
        form = StockTransferForm(request.POST, stock=stock)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.stock = stock
            transfer.from_location = stock.location
            transfer.from_aisle = stock.aisle
            transfer.created_by = request.user
            transfer.save()
            
            # Handle quantity based on transfer type and location-based inventory
            if transfer.transfer_type == 'restock':
                # For restock: don't reduce quantity until completion (just move between locations)
                pass
            elif transfer.transfer_type == 'customer_collection':
                # For customer collection: reduce from origin location immediately
                stock.remove_from_location(transfer.from_location, transfer.quantity)
            else:
                # General transfer: reduce from origin location
                stock.remove_from_location(transfer.from_location, transfer.quantity)
            
            # CREATE HISTORY RECORD for transfer initiation
            from django.utils import timezone
            StockHistory.objects.create(
                category=stock.category,
                item_name=stock.item_name,
                quantity=stock.total_across_locations,
                issue_quantity=0,
                receive_quantity=0,
                received_by=str(request.user),
                note=f"Transfer INITIATED: {transfer.quantity} units from {transfer.from_location.name} to {transfer.to_location.name} ({transfer.get_transfer_type_display()})",
                created_by=str(request.user),
                last_updated=timezone.now(),
                timestamp=timezone.now()
            )
            
            messages.success(request, f'Transfer created: {transfer.quantity} units of {stock.item_name} from {transfer.from_location} to {transfer.to_location}')
            return redirect('stock_detail', pk=stock.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StockTransferForm(stock=stock)
    
    context = {
        'title': f'Transfer Stock - {stock.item_name}',
        'stock': stock,
        'form': form,
    }
    return render(request, 'stock/transfer_stock.html', context)

@login_required
def transfer_list(request):
    """List all stock transfers"""
    transfers = StockTransfer.objects.select_related('stock', 'from_location', 'to_location', 'created_by').all()
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        transfers = transfers.filter(status=status_filter)
    
    context = {
        'title': 'Stock Transfers',
        'transfers': transfers,
        'status_choices': StockTransfer.STATUS_CHOICES,
        'current_status': status_filter,
    }
    return render(request, 'stock/transfer_list.html', context)

@login_required
def approve_transfer(request, pk):
    """Approve a pending transfer"""
    transfer = get_object_or_404(StockTransfer, id=pk)
    
    if transfer.can_be_approved():
        transfer.approve(request.user)
        
        # CREATE HISTORY RECORD for approval
        from django.utils import timezone
        StockHistory.objects.create(
            category=transfer.stock.category,
            item_name=transfer.stock.item_name,
            quantity=transfer.stock.total_across_locations,
            issue_quantity=0,
            receive_quantity=0,
            received_by=str(request.user),
            note=f"Transfer APPROVED: {transfer.quantity} units from {transfer.from_location.name} to {transfer.to_location.name} ({transfer.get_transfer_type_display()})",
            created_by=str(request.user),
            last_updated=timezone.now(),
            timestamp=timezone.now()
        )
        
        messages.success(request, f'Transfer approved: {transfer.stock.item_name} from {transfer.from_location} to {transfer.to_location}')
    else:
        messages.error(request, 'This transfer cannot be approved.')
    
    return redirect('transfer_list')

@login_required
def complete_transfer(request, pk):
    """Complete an approved transfer"""
    transfer = get_object_or_404(StockTransfer, id=pk)
    
    if transfer.can_be_completed():
        transfer.complete(request.user)
        
        # CREATE HISTORY RECORD for completion
        from django.utils import timezone
        status_text = "COMPLETED" if transfer.status == 'completed' else "AWAITING COLLECTION"
        StockHistory.objects.create(
            category=transfer.stock.category,
            item_name=transfer.stock.item_name,
            quantity=transfer.stock.total_across_locations,
            issue_quantity=0,
            receive_quantity=0,
            received_by=str(request.user),
            note=f"Transfer {status_text}: {transfer.quantity} units from {transfer.from_location.name} to {transfer.to_location.name} ({transfer.get_transfer_type_display()})",
            created_by=str(request.user),
            last_updated=timezone.now(),
            timestamp=timezone.now()
        )
        
        messages.success(request, f'Transfer completed: {transfer.stock.item_name} is now at {transfer.to_location}')
    else:
        messages.error(request, 'This transfer cannot be completed.')
    
    return redirect('transfer_list')

@login_required
def cancel_transfer(request, pk):
    """Cancel a transfer and restore stock"""
    transfer = get_object_or_404(StockTransfer, id=pk)
    
    if transfer.status in ['pending', 'in_transit', 'awaiting_collection']:
        # Restore stock quantity if it was reduced and transfer hasn't been collected
        if transfer.status != 'completed' and transfer.status != 'collected':
            # Only restore if quantity was actually reduced (not for restock transfers)
            if transfer.transfer_type != 'restock':
                transfer.stock.quantity += transfer.quantity
                transfer.stock.save()
        
        transfer.status = 'cancelled'
        transfer.save()
        
        # CREATE HISTORY RECORD for cancellation
        from django.utils import timezone
        StockHistory.objects.create(
            category=transfer.stock.category,
            item_name=transfer.stock.item_name,
            quantity=transfer.stock.total_across_locations,
            issue_quantity=0,
            receive_quantity=0,
            received_by=str(request.user),
            note=f"Transfer CANCELLED: {transfer.quantity} units from {transfer.from_location.name} to {transfer.to_location.name} ({transfer.get_transfer_type_display()})",
            created_by=str(request.user),
            last_updated=timezone.now(),
            timestamp=timezone.now()
        )
        
        messages.success(request, f'Transfer cancelled: {transfer.quantity} units of {transfer.stock.item_name} restored')
    else:
        messages.error(request, 'This transfer cannot be cancelled.')
    
    return redirect('transfer_list')

@login_required
def mark_collected(request, pk):
    """Mark a customer collection transfer as collected"""
    transfer = get_object_or_404(StockTransfer, id=pk)
    
    if transfer.can_be_collected():
        transfer.mark_collected(request.user)
        
        # CREATE HISTORY RECORD for customer collection
        from django.utils import timezone
        StockHistory.objects.create(
            category=transfer.stock.category,
            item_name=transfer.stock.item_name,
            quantity=transfer.stock.total_across_locations,
            issue_quantity=transfer.quantity,  # Mark as issued quantity since it's collected
            receive_quantity=0,
            received_by=str(request.user),
            note=f"Transfer COLLECTED: {transfer.customer_name} collected {transfer.quantity} units from {transfer.to_location.name}",
            created_by=str(request.user),
            last_updated=timezone.now(),
            timestamp=timezone.now()
        )
        
        messages.success(request, f'Customer collection confirmed: {transfer.customer_name} collected {transfer.quantity} units of {transfer.stock.item_name}')
    else:
        messages.error(request, 'This transfer is not awaiting collection.')
    
    return redirect('transfer_list')


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
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_create_stock'):
        messages.error(request, 'You do not have permission to add stock.')
        return redirect('/')
        
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
            
            # Get location and aisle from form
            location = form.cleaned_data.get('location')
            aisle = form.cleaned_data.get('aisle', '')
            quantity = form.cleaned_data.get('quantity', 0)
            
            stock.save()
            
            # Create StockLocation record for the new multi-location system
            if location and quantity > 0:
                StockLocation.objects.create(
                    stock=stock,
                    store=location,
                    quantity=quantity,
                    aisle=aisle
                )
            
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
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_edit_stock'):
        messages.error(request, 'You do not have permission to edit stock.')
        return redirect('/')
        
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
            
            # Handle StockLocation for the updated location
            location = form.cleaned_data.get('location')
            aisle = form.cleaned_data.get('aisle', '')
            new_quantity = updated_stock.quantity
            
            if location:
                # Update or create StockLocation record
                stock_location, created = StockLocation.objects.get_or_create(
                    stock=updated_stock,
                    store=location,
                    defaults={'quantity': new_quantity, 'aisle': aisle}
                )
                if not created:
                    # If StockLocation already exists, update it
                    stock_location.quantity = new_quantity
                    if aisle:
                        stock_location.aisle = aisle
                    stock_location.save()
                
                # Remove any other StockLocation records for this stock (since we're setting a single location)
                StockLocation.objects.filter(stock=updated_stock).exclude(store=location).delete()
            else:
                # If no location is set, remove all StockLocation records
                StockLocation.objects.filter(stock=updated_stock).delete()
            
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
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_issue_stock'):
        messages.error(request, 'You do not have permission to issue stock.')
        return redirect('/')
        
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
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_receive_stock'):
        messages.error(request, 'You do not have permission to receive stock.')
        return redirect('/')
        
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
def commit_stock(request, pk):
    """Handle stock commitment with customer deposit and order details"""
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_commit_stock'):
        messages.error(request, 'You do not have permission to commit stock.')
        return redirect('/')
        
    stock = Stock.objects.get(id=pk)
    
    if request.method == 'POST':
        from .form import CommitStockForm
        form = CommitStockForm(request.POST)
        if form.is_valid():
            commit_quantity = form.cleaned_data['quantity']
            
            # Check if enough stock available
            if commit_quantity > stock.available_for_sale:
                messages.error(request, f'Cannot commit {commit_quantity} items. Only {stock.available_for_sale} available for sale.')
                return render(request, 'stock/commit_stock.html', {'form': form, 'stock': stock})
            
            # Create commitment record
            commitment = form.save(commit=False)
            commitment.stock = stock
            commitment.committed_by = request.user
            commitment.save()
            
            messages.success(request, f'Successfully committed {commit_quantity} {stock.item_name} for order {commitment.customer_order_number}!')
            return redirect('view_stock')
    else:
        from .form import CommitStockForm
        form = CommitStockForm()
    
    context = {
        'form': form, 
        'stock': stock,
        'available_quantity': stock.available_for_sale
    }
    return render(request, 'stock/commit_stock.html', context)

@login_required
def fulfill_commitment(request, pk):
    """Fulfill a stock commitment - customer has paid in full and taken the items"""
    commitment = CommittedStock.objects.get(id=pk)
    
    if commitment.is_fulfilled:
        messages.warning(request, 'This commitment is already fulfilled.')
        return redirect('stock_detail', pk=commitment.stock.pk)
    
    # Check if there's enough stock to fulfill
    if commitment.quantity > commitment.stock.quantity:
        messages.error(request, f'Cannot fulfill commitment. Only {commitment.stock.quantity} items in stock, but {commitment.quantity} needed.')
        return redirect('stock_detail', pk=commitment.stock.pk)
    
    # Issue the stock (reduce quantity)
    commitment.stock.quantity -= commitment.quantity
    commitment.stock.issue_quantity = commitment.quantity
    commitment.stock.issued_by = request.user.username
    commitment.stock.save()
    
    # Mark commitment as fulfilled
    commitment.is_fulfilled = True
    commitment.fulfilled_at = timezone.now()
    commitment.save()
    
    # Create history record for the stock issue
    StockHistory.objects.create(
        category=commitment.stock.category,
        item_name=commitment.stock.item_name,
        quantity=commitment.stock.quantity,
        issue_quantity=commitment.quantity,
        receive_quantity=0,
        issued_by=request.user.username,
        note=f"Fulfilled commitment for order {commitment.customer_order_number} - Customer: {commitment.customer_name}",
        created_by=request.user.username,
        last_updated=timezone.now(),
        timestamp=timezone.now()
    )
    
    messages.success(request, f'Commitment fulfilled! {commitment.quantity} items issued to {commitment.customer_name}.')
    return redirect('stock_detail', pk=commitment.stock.pk)

@login_required
def cancel_commitment(request, pk):
    """Cancel a stock commitment - release the committed stock back to available"""
    commitment = CommittedStock.objects.get(id=pk)
    
    if commitment.is_fulfilled:
        messages.warning(request, 'Cannot cancel a fulfilled commitment.')
        return redirect('stock_detail', pk=commitment.stock.pk)
    
    # Mark commitment as fulfilled (to remove it from active commitments)
    # but don't issue the stock - just release it back to available
    commitment.is_fulfilled = True
    commitment.fulfilled_at = timezone.now()
    commitment.save()
    
    # Note: The stock's committed_quantity will be automatically updated 
    # when the commitment is saved due to the save() method in CommittedStock model
    
    messages.success(request, f'Commitment cancelled for {commitment.customer_name}. Stock is now available for sale. Remember to process deposit refund manually.')
    return redirect('stock_detail', pk=commitment.stock.pk)

@login_required
def delete_stock(request, pk):
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_edit_stock'):
        messages.error(request, 'You do not have permission to delete stock.')
        return redirect('/')
        
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
    
    # Get history for this specific item
    stock_history = StockHistory.objects.filter(
        item_name=detail.item_name
    ).order_by('-timestamp')
    
    # Get commitments for this stock
    commitments = CommittedStock.objects.filter(
        stock=detail
    )  # Uses model default ordering
    
    context = {
        'detail': detail,
        'stock_history': stock_history,
        'commitments': commitments
    }
    return render(request, 'stock/stock_detail.html', context)


@login_required
def issue_item(request, pk):
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_issue_stock'):
        messages.error(request, 'You do not have permission to issue stock.')
        return redirect('/')
        
    issue = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=issue, stock=issue)
    
    if form.is_valid():
        value = form.save(commit=False)
        issue_quantity = value.issue_quantity
        issue_location = form.cleaned_data.get('issue_location')
        
        # Handle location-based issuing
        if issue_location:
            location_stock = issue.get_location_quantity(issue_location)
            if location_stock >= issue_quantity:
                # Remove quantity from the specified location
                success = issue.remove_from_location(issue_location, issue_quantity)
                if success:
                    value.receive_quantity = 0
                    value.issued_by = str(request.user)
                    value.save()
                    
                    # CREATE HISTORY RECORD
                    from django.utils import timezone
                    location_note = f"Issued from {issue_location.name}"
                    full_note = f"{location_note}. {value.note}" if value.note else location_note
                    
                    StockHistory.objects.create(
                        category=value.category,
                        item_name=value.item_name,
                        quantity=issue.total_across_locations,  # Updated total
                        issue_quantity=issue_quantity,
                        receive_quantity=0,
                        issued_by=value.issued_by,
                        note=full_note,
                        created_by=str(request.user),
                        last_updated=timezone.now(),
                        timestamp=timezone.now()
                    )
                    
                    messages.success(request, f"Issued Successfully: {issue_quantity} {issue.item_name}s from {issue_location.name}. Total remaining: {issue.total_across_locations}")
                else:
                    messages.error(request, "Error processing issue request")
            else:
                messages.error(request, f"Insufficient stock at {issue_location.name}. Available: {location_stock}")
        else:
            # If no location specified but we have issue_location form field, this shouldn't happen
            # Fall back to old behavior for backward compatibility
            value.receive_quantity = 0
            value.quantity = value.quantity - value.issue_quantity
            value.issued_by = str(request.user)
            if value.quantity >= 0:
                value.save()
                messages.success(request, "Issued Successfully")
            else:
                messages.error(request, "Insufficient Stock")
                
        return redirect('stock_detail', pk=issue.id)
    
    context = {
        "title": f'Issue {issue.item_name}',
        "issue": issue,
        "form": form,
        "username": f'Issued by: {request.user}',
    }
    return render(request, "stock/add_stock.html", context)


@login_required
def receive_item(request, pk):
    print(f"=== RECEIVE_ITEM DEBUG ===")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    print(f"PK received: {pk}")
    
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_receive_stock'):
        messages.error(request, 'You do not have permission to receive stock.')
        return redirect('/')
    
    receive = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=receive, stock=receive)
    
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
            receive_quantity = value.receive_quantity
            receive_location = form.cleaned_data['receive_location']
            receive_aisle = form.cleaned_data.get('receive_aisle', '')
            
            # Add quantity to the specified location
            value.add_to_location(receive_location, receive_quantity, receive_aisle)
            
            # Update stock metadata
            value.issue_quantity = 0
            value.received_by = str(request.user)
            value.edited_by = str(request.user)
            value.save()
            
            # CREATE HISTORY RECORD
            from django.utils import timezone  # Import moved here
            location_note = f"Received at {receive_location.name}"
            if receive_aisle:
                location_note += f" (Aisle: {receive_aisle})"
            
            full_note = f"{location_note}. {value.note}" if value.note else location_note
            
            StockHistory.objects.create(
                category=value.category,
                item_name=value.item_name,
                quantity=value.total_across_locations,  # Total across all locations
                issue_quantity=0,
                receive_quantity=receive_quantity,
                received_by=value.received_by,
                note=full_note,
                created_by=str(request.user),
                last_updated=timezone.now(),
                timestamp=timezone.now()
            )
            
            messages.success(
                request,
                f"Received Successfully: {receive_quantity} {value.item_name}s added to {receive_location.name}. Total stock: {value.total_across_locations}"
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
    return render(request, "stock/receive_item.html", context)


@login_required
def re_order(request, pk):
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_edit_stock'):
        messages.error(request, 'You do not have permission to modify stock settings.')
        return redirect('/')
        
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
from .tasks import send_email_async

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
            # Use Railway-friendly email service
            email_status_message = send_purchase_order_email_safe(
                purchase_order, 
                recipient_emails, 
                email_subject, 
                email_body
            )
            
            # Update purchase order status immediately (don't wait for email)
            purchase_order.status = 'sent'
            purchase_order.sent_at = timezone.now()
            purchase_order.save()
            PurchaseOrderHistory.objects.create(
                purchase_order=purchase_order,
                action='sent',
                notes=f'Purchase order sent to {", ".join(recipient_emails)}',
                created_by=request.user
            )
            messages.success(request, email_status_message)
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
    return redirect('purchase_order_detail', pk=pk)

@login_required
def receive_purchase_order_items(request, pk=None):
    """Unified receiving interface - shows all items and allows bulk receiving"""
    if pk:
        # Direct PO access - /purchase-order/2/receive/
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    else:
        # PO selection mode - /receive-po-items/
        if request.method == 'POST' and 'select_po' in request.POST:
            po_form = ReceivePOItemsForm(request.POST)
            if po_form.is_valid():
                purchase_order = po_form.cleaned_data['purchase_order']
                # Redirect to the same URL with PO ID
                return redirect('receive_purchase_order_items', pk=purchase_order.pk)
        
        # Show PO selection form
        po_form = ReceivePOItemsForm()
        context = {
            'title': 'Receive PO Items - Select Purchase Order',
            'po_form': po_form,
            'show_po_selection': True,
        }
        return render(request, 'stock/receive_purchase_order_items.html', context)
    
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
                        
                        # Also create/update stock entries if "create_stock" option is selected
                        create_stock = request.POST.get('create_stock', False)
                        if create_stock:
                            # Use PO's designated delivery location
                            delivery_location = purchase_order.store
                            if not delivery_location:
                                # Fallback to first active store if no delivery location set
                                delivery_location = Store.objects.filter(is_active=True).first()
                            
                            if delivery_location:
                                # Check if stock item already exists (regardless of location)
                                existing_stock = Stock.objects.filter(
                                    item_name=item.product,
                                    condition='new'  # Default to new condition
                                ).first()
                                
                                if existing_stock:
                                    # Add to existing stock total quantity
                                    existing_stock.quantity += item_data['quantity']
                                    
                                    # Set primary location if not set
                                    if not existing_stock.location:
                                        existing_stock.location = delivery_location
                                    
                                    existing_stock.note = f"Received from PO - {purchase_order.reference_number}"
                                    existing_stock.save()
                                    
                                    # Update or create StockLocation record for the specific store
                                    stock_location, created = StockLocation.objects.get_or_create(
                                        stock=existing_stock,
                                        store=delivery_location,
                                        defaults={'quantity': 0}
                                    )
                                    stock_location.quantity += item_data['quantity']
                                    stock_location.save()
                                    
                                    # Create StockHistory record for PO receiving (existing stock)
                                    StockHistory.objects.create(
                                        category=existing_stock.category,
                                        item_name=existing_stock.item_name,
                                        quantity=existing_stock.quantity,  # Total quantity after addition
                                        receive_quantity=item_data['quantity'],  # Amount received
                                        received_by=request.user.username,
                                        note=f"Received from PO - {purchase_order.reference_number} | Delivery Ref: {item_data.get('delivery_reference', 'N/A')} | Added to existing stock",
                                        created_by=request.user.username,
                                        last_updated=timezone.now(),
                                        timestamp=timezone.now()
                                    )
                                    
                                else:
                                    # Create new stock entry at delivery location
                                    category, _ = Category.objects.get_or_create(
                                        group='PO Items',
                                        defaults={'group': 'PO Items'}
                                    )
                                    
                                    new_stock = Stock.objects.create(
                                        category=category,
                                        item_name=item.product,
                                        quantity=item_data['quantity'],
                                        location=delivery_location,
                                        condition='new',
                                        note=f"Received from PO - {purchase_order.reference_number}",
                                        created_by=request.user.username
                                    )
                                    
                                    # Create StockLocation record
                                    StockLocation.objects.create(
                                        stock=new_stock,
                                        store=delivery_location,
                                        quantity=item_data['quantity']
                                    )
                                    
                                    # Create StockHistory record for PO receiving
                                    StockHistory.objects.create(
                                        category=category,
                                        item_name=item.product,
                                        quantity=item_data['quantity'],
                                        receive_quantity=item_data['quantity'],
                                        received_by=request.user.username,
                                        note=f"Received from PO - {purchase_order.reference_number} | Delivery Ref: {item_data.get('delivery_reference', 'N/A')}",
                                        created_by=request.user.username,
                                        last_updated=timezone.now(),
                                        timestamp=timezone.now()
                                    )
                    
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
                    
                    # Enhanced success message
                    success_message = f'Successfully received {total_items} items across {len(created_records)} products!'
                    if request.POST.get('create_stock', False) and purchase_order.store:
                        success_message += f' Stock has been added to {purchase_order.store.name} inventory.'
                    
                    messages.success(request, success_message)
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
        form = StoreForm(request.POST, request.FILES)
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
        form = StoreForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            store = form.save()
            messages.success(request, f'Store "{store.name}" updated successfully!')
            return redirect('manage_stores')
    else:
        form = StoreForm(instance=store)
    context = {'title': f'Edit Store - {store.name}', 'form': form, 'store': store}
    return render(request, 'stock/add_store.html', context)

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


# Category Management Views
@login_required
def manage_categories(request):
    categories = Category.objects.all()
    context = {'title': 'Manage Categories', 'categories': categories}
    return render(request, 'stock/manage_categories.html', context)

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            
            # Check if this is an AJAX request (for the modal)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({
                    'success': True,
                    'category': {
                        'id': category.id,
                        'name': category.group
                    },
                    'message': f'Category "{category.group}" added successfully!'
                })
            
            messages.success(request, f'Category "{category.group}" added successfully!')
            return redirect('manage_categories')
        else:
            # Handle AJAX form errors
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f'{field}: {error}')
                
                return JsonResponse({
                    'success': False,
                    'error': '; '.join(errors) if errors else 'Invalid form data'
                })
    else:
        form = CategoryForm()
    context = {'title': 'Add Category', 'form': form}
    return render(request, 'stock/add_category.html', context)

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.group}" updated successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    context = {'title': 'Edit Category', 'form': form}
    return render(request, 'stock/add_category.html', context)

@login_required
def delete_category(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        if category.stock_set.exists():
            messages.error(request, f'Cannot delete "{category.group}" as it has associated stock items.')
        else:
            category.delete()
            messages.success(request, f'Category "{category.group}" deleted successfully!')
    return redirect('manage_categories')


# ----------------------------
# Access Control Management Views
# ----------------------------

from .utils.permissions import require_permission, require_any_permission, get_user_role, has_permission

@require_permission('can_manage_access_control')
def manage_users(request):
    """Manage users and their roles - Admin only"""
    form = UserSearchForm(request.GET or None)
    users = User.objects.select_related('role').all()
    
    # Apply filters
    if form.is_valid():
        username = form.cleaned_data.get('username')
        role = form.cleaned_data.get('role')
        is_active = form.cleaned_data.get('is_active')
        
        if username:
            users = users.filter(username__icontains=username)
        
        if role:
            users = users.filter(role__role=role)
        
        if is_active == 'true':
            users = users.filter(is_active=True)
        elif is_active == 'false':
            users = users.filter(is_active=False)
    
    # Ensure all users have roles
    for user in users:
        if not hasattr(user, 'role'):
            UserRole.objects.create(user=user, role='sales', created_by=request.user)
    
    context = {
        'title': 'Manage Users & Access Control',
        'users': users,
        'form': form,
    }
    return render(request, 'stock/manage_users.html', context)

@require_permission('can_manage_access_control')
def add_user(request):
    """Add new user - Admin only"""
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            user_role = form.save(created_by=request.user)
            messages.success(request, f'User "{user_role.user.username}" created successfully with role "{user_role.get_role_display()}"!')
            return redirect('manage_users')
    else:
        form = UserRoleForm()
    
    context = {
        'title': 'Add New User',
        'form': form,
    }
    return render(request, 'stock/add_user.html', context)

@require_permission('can_manage_access_control')
def edit_user(request, pk):
    """Edit user and role - Admin only"""
    user = get_object_or_404(User, pk=pk)
    user_role = get_user_role(user)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user_role, user_instance=user)
        if form.is_valid():
            user_role = form.save(created_by=request.user)
            messages.success(request, f'User "{user_role.user.username}" updated successfully!')
            return redirect('manage_users')
    else:
        form = UserRoleForm(instance=user_role, user_instance=user)
    
    context = {
        'title': f'Edit User - {user.username}',
        'form': form,
        'user': user,
    }
    return render(request, 'stock/add_user.html', context)

@require_permission('can_manage_access_control')
def delete_user(request, pk):
    """Delete user - Admin only"""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        
        # Prevent deleting superusers and self
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser accounts.')
        elif user == request.user:
            messages.error(request, 'Cannot delete your own account.')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'User "{username}" deleted successfully!')
    
    return redirect('manage_users')

@require_permission('can_view_warehouse_receiving')
def warehouse_receiving(request):
    """Warehouse receiving view - shows items to be received without amounts"""
    # Get purchase orders with items that need receiving
    purchase_orders = PurchaseOrder.objects.filter(
        status__in=['submitted', 'sent', 'confirmed'],
        items__received_quantity__lt=models.F('items__quantity')
    ).select_related('manufacturer', 'delivery_person', 'store').prefetch_related('items').distinct()
    
    # Filter out financial information for warehouse users
    filtered_orders = []
    for po in purchase_orders:
        filtered_po = {
            'id': po.id,
            'reference_number': po.reference_number,
            'manufacturer': po.manufacturer,
            'delivery_person': po.delivery_person,
            'delivery_type': po.delivery_type,
            'store': po.store,
            'status': po.status,
            'created_at': po.created_at,
            'updated_at': po.updated_at,
            'note_for_manufacturer': po.note_for_manufacturer,
            'items': []
        }
        
        for item in po.items.filter(received_quantity__lt=models.F('quantity')):
            filtered_item = {
                'id': item.id,
                'product': item.product,
                'quantity': item.quantity,
                'received_quantity': item.received_quantity,
                'remaining_quantity': item.remaining_quantity,
                'associated_order_number': item.associated_order_number,
            }
            filtered_po['items'].append(filtered_item)
        
        if filtered_po['items']:  # Only include POs with items to receive
            filtered_orders.append(filtered_po)
    
    context = {
        'title': 'Warehouse - Items to Receive',
        'purchase_orders': filtered_orders,
    }
    return render(request, 'stock/warehouse_receiving.html', context)

# DEPRECATED: Use receive_purchase_order_items instead
# @require_any_permission('can_receive_purchase_order', 'can_receive_stock')
def receive_po_items_deprecated(request):
    """Receive PO Items - directly add to inventory under Stock Management"""
    selected_po = None
    items_form = None
    
    if request.method == 'POST':
        if 'select_po' in request.POST:
            # Step 1: Select PO
            po_form = ReceivePOItemsForm(request.POST)
            if po_form.is_valid():
                selected_po = po_form.cleaned_data['purchase_order']
                # Get items that need receiving
                items_to_receive = []
                for item in selected_po.items.all():
                    if item.remaining_quantity > 0:
                        items_to_receive.append(item)
                items_form = ReceiveItemForm(items_to_receive)
        
        elif 'receive_items' in request.POST and request.POST.get('purchase_order_id'):
            # Step 2: Process receiving
            selected_po = get_object_or_404(PurchaseOrder, id=request.POST.get('purchase_order_id'))
            # Get items with remaining quantities
            items_to_receive = []
            for item in selected_po.items.all():
                if item.remaining_quantity > 0:
                    items_to_receive.append(item)
            
            received_count = 0
            
            for item in items_to_receive:
                # Get data directly from POST since form might not be properly processing
                receive_qty = int(request.POST.get(f'receive_qty_{item.id}', '0') or '0')
                location_id = request.POST.get(f'location_{item.id}')
                condition = request.POST.get(f'condition_{item.id}', 'new')
                aisle = request.POST.get(f'aisle_{item.id}', '')
                
                if receive_qty > 0 and location_id:
                    try:
                        location = Store.objects.get(id=location_id)
                    except Store.DoesNotExist:
                        continue
                    
                    # Check if stock item already exists (regardless of location)
                    existing_stock = Stock.objects.filter(
                        item_name=item.product,
                        condition=condition
                    ).first()
                    
                    if existing_stock:
                        # Add to existing stock total quantity
                        existing_stock.quantity += receive_qty
                        
                        # Set primary location if not set
                        if not existing_stock.location:
                            existing_stock.location = location
                        
                        existing_stock.note = f"Received from PO - {selected_po.reference_number}"
                        existing_stock.save()
                        
                        # Update or create StockLocation record for the specific store
                        stock_location, created = StockLocation.objects.get_or_create(
                            stock=existing_stock,
                            store=location,
                            defaults={'quantity': 0, 'aisle': aisle}
                        )
                        stock_location.quantity += receive_qty
                        if aisle:
                            stock_location.aisle = aisle
                        stock_location.save()
                        
                        # Create StockHistory record for PO receiving (existing stock)
                        StockHistory.objects.create(
                            category=existing_stock.category,
                            item_name=existing_stock.item_name,
                            quantity=existing_stock.quantity,  # Total quantity after addition
                            receive_quantity=receive_qty,  # Amount received
                            received_by=request.user.username,
                            note=f"Received from PO - {selected_po.reference_number} | Added to existing stock",
                            created_by=request.user.username,
                            last_updated=timezone.now(),
                            timestamp=timezone.now()
                        )
                        
                    else:
                        # Create new stock entry
                        # Get or create category for this product
                        category, _ = Category.objects.get_or_create(
                            group='PO Items',  # Default category for PO items
                            defaults={'group': 'PO Items'}
                        )
                        
                        new_stock = Stock.objects.create(
                            category=category,
                            item_name=item.product,
                            condition=condition,
                            quantity=receive_qty,
                            location=location,
                            aisle=aisle,
                            note=f"Received from PO - {selected_po.reference_number}",
                            received_by=str(request.user),
                            issued_by=str(request.user),
                            re_order=0,
                        )
                        
                        # Create corresponding StockLocation record
                        StockLocation.objects.create(
                            stock=new_stock,
                            store=location,
                            quantity=receive_qty,
                            aisle=aisle
                        )
                        
                        # Create StockHistory record for PO receiving (new stock)
                        StockHistory.objects.create(
                            category=category,
                            item_name=item.product,
                            quantity=receive_qty,
                            receive_quantity=receive_qty,
                            received_by=request.user.username,
                            note=f"Received from PO - {selected_po.reference_number} | New stock created",
                            created_by=request.user.username,
                            last_updated=timezone.now(),
                            timestamp=timezone.now()
                        )
                    
                    # Update PO item received quantity
                    item.received_quantity += receive_qty
                    item.save()
                    
                    # StockHistory creation is now handled above for both existing and new stock cases
                    
                    received_count += 1
                
                if received_count > 0:
                    messages.success(
                        request, 
                        f'Successfully received {received_count} items from PO {selected_po.reference_number}. '
                        f'Items have been added to inventory.'
                    )
                    return redirect('receive_po_items')
                else:
                    messages.warning(request, 'No items were received. Please select quantities and locations.')
    
    # Default form for step 1
    if not selected_po:
        po_form = ReceivePOItemsForm()
    else:
        po_form = ReceivePOItemsForm(initial={'purchase_order': selected_po})
    
    context = {
        'title': 'Receive PO Items',
        'po_form': po_form,
        'selected_po': selected_po,
        'items_form': items_form,
        'stores': Store.objects.all(),
    }
    return render(request, 'stock/receive_po_items.html', context)


# ===================================
# STOCK RESERVATION VIEWS
# ===================================

@login_required
def reserve_stock(request, pk):
    """Create a new stock reservation"""
    stock = get_object_or_404(Stock, pk=pk)
    
    # Check permissions
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_commit_stock'):
        messages.error(request, 'You do not have permission to reserve stock.')
        return redirect('/')
    
    if request.method == 'POST':
        form = StockReservationForm(stock=stock, data=request.POST)
        if form.is_valid():
            reservation = form.save(reserved_by=request.user)
            messages.success(
                request, 
                f'Successfully reserved {reservation.quantity} units of {stock.item_name} '
                f'until {reservation.expires_at.strftime("%Y-%m-%d %H:%M")}'
            )
            return redirect('stock_detail', pk=stock.pk)
    else:
        form = StockReservationForm(stock=stock)
    
    context = {
        'title': f'Reserve Stock: {stock.item_name}',
        'stock': stock,
        'form': form,
    }
    return render(request, 'stock/reserve_stock.html', context)


@login_required
def reservation_list(request):
    """List all stock reservations with filtering"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('/')
    
    # Filter reservations based on status and stock
    status_filter = request.GET.get('status', 'active')
    stock_filter = request.GET.get('stock')
    reservations = StockReservation.objects.select_related('stock', 'reserved_by')  # Uses model default ordering
    
    if status_filter and status_filter != 'all':
        reservations = reservations.filter(status=status_filter)
    
    if stock_filter:
        reservations = reservations.filter(stock_id=stock_filter)
    
    # Handle expired reservations
    from django.utils import timezone
    expired_reservations = reservations.filter(status='active', expires_at__lt=timezone.now())
    for reservation in expired_reservations:
        reservation.expire()
    
    context = {
        'title': 'Stock Reservations',
        'reservations': reservations[:50],  # Limit for performance
        'status_filter': status_filter,
    }
    return render(request, 'stock/reservation_list.html', context)


@login_required
def reservation_detail(request, pk):
    """View details of a specific reservation"""
    reservation = get_object_or_404(StockReservation, pk=pk)
    
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('/')
    
    context = {
        'title': f'Reservation: {reservation.stock.item_name}',
        'reservation': reservation,
    }
    return render(request, 'stock/reservation_detail.html', context)


@login_required
def update_reservation(request, pk):
    """Update an existing stock reservation"""
    reservation = get_object_or_404(StockReservation, pk=pk)
    
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('/')
    
    # Check if reservation can be updated
    if reservation.status not in ['active', 'expired']:
        messages.error(request, 'This reservation cannot be updated.')
        return redirect('reservation_detail', pk=pk)
    
    if request.method == 'POST':
        form = StockReservationUpdateForm(instance=reservation, data=request.POST)
        if form.is_valid():
            reservation = form.save()
            messages.success(request, 'Reservation updated successfully.')
            return redirect('reservation_detail', pk=pk)
    else:
        form = StockReservationUpdateForm(instance=reservation)
    
    context = {
        'title': f'Update Reservation: {reservation.stock.item_name}',
        'reservation': reservation,
        'form': form,
    }
    return render(request, 'stock/update_reservation.html', context)


@login_required
def cancel_reservation(request, pk):
    """Cancel a stock reservation"""
    reservation = get_object_or_404(StockReservation, pk=pk)
    
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('/')
    
    if not reservation.can_be_cancelled():
        messages.error(request, 'This reservation cannot be cancelled.')
        return redirect('reservation_detail', pk=pk)
    
    if request.method == 'POST':
        if reservation.cancel(request.user):
            messages.success(request, 'Reservation cancelled successfully.')
        else:
            messages.error(request, 'Failed to cancel reservation.')
        return redirect('reservation_list')
    
    context = {
        'title': f'Cancel Reservation: {reservation.stock.item_name}',
        'reservation': reservation,
    }
    return render(request, 'stock/cancel_reservation.html', context)


@login_required
def fulfill_reservation(request, pk):
    """Convert reservation to commitment or complete sale"""
    reservation = get_object_or_404(StockReservation, pk=pk)
    
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_commit_stock'):
        messages.error(request, 'You do not have permission to fulfill reservations.')
        return redirect('/')
    
    if not reservation.can_be_fulfilled():
        messages.error(request, 'This reservation cannot be fulfilled.')
        return redirect('reservation_detail', pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'commit':
            # Convert to commitment (redirect to commit stock page)
            reservation.fulfill(request.user)
            messages.success(request, 'Reservation fulfilled. Please create customer commitment.')
            return redirect('commit_stock', pk=reservation.stock.pk)
        
        elif action == 'complete':
            # Complete as sale (fulfill and issue stock)
            if reservation.fulfill(request.user):
                # Issue the stock
                stock = reservation.stock
                if stock.quantity >= reservation.quantity:
                    stock.issue_quantity = (stock.issue_quantity or 0) + reservation.quantity
                    stock.quantity -= reservation.quantity
                    stock.issued_by = request.user.username
                    stock.save()
                    
                    messages.success(
                        request, 
                        f'Reservation fulfilled and {reservation.quantity} units issued to {reservation.customer_name or "customer"}.'
                    )
                else:
                    messages.error(request, 'Insufficient stock to complete the sale.')
            else:
                messages.error(request, 'Failed to fulfill reservation.')
        
        return redirect('reservation_list')
    
    context = {
        'title': f'Fulfill Reservation: {reservation.stock.item_name}',
        'reservation': reservation,
    }
    return render(request, 'stock/fulfill_reservation.html', context)


@login_required
def expire_reservations(request):
    """Manually expire all overdue reservations (admin function)"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_manage_access_control'):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('/')
    
    from django.utils import timezone
    expired_count = 0
    
    # Find and expire overdue reservations
    overdue_reservations = StockReservation.objects.filter(
        status='active',
        expires_at__lt=timezone.now()
    )
    
    for reservation in overdue_reservations:
        if reservation.expire():
            expired_count += 1
    
    if expired_count > 0:
        messages.success(request, f'Expired {expired_count} overdue reservations.')
    else:
        messages.info(request, 'No overdue reservations found.')
    
    return redirect('reservation_list')


# ----------------------------
# Stock Audit Views
# ----------------------------

@login_required
def audit_list(request):
    """Display list of all stock audits"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, 'You do not have permission to view audits.')
        return redirect('/')
    
    audits = StockAudit.objects.all().select_related('created_by', 'approved_by')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        audits = audits.filter(status=status_filter)
    
    # Filter by audit type if requested
    type_filter = request.GET.get('audit_type')
    if type_filter and type_filter != 'all':
        audits = audits.filter(audit_type=type_filter)
    
    context = {
        'title': 'Stock Audits',
        'audits': audits,
        'status_filter': status_filter or 'all',
        'type_filter': type_filter or 'all',
        'status_choices': StockAudit.STATUS_CHOICES,
        'type_choices': StockAudit.AUDIT_TYPE_CHOICES,
    }
    return render(request, 'stock/audit_list.html', context)


@login_required
def audit_detail(request, audit_id):
    """Display detailed view of a specific audit"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, 'You do not have permission to view audits.')
        return redirect('/')
    
    audit = get_object_or_404(StockAudit, pk=audit_id)
    audit_items = audit.audit_items.select_related('stock', 'counted_by').order_by('stock__item_name')
    
    context = {
        'title': f'Audit: {audit.audit_reference}',
        'audit': audit,
        'audit_items': audit_items,
    }
    return render(request, 'stock/audit_detail.html', context)


@login_required
def create_audit(request):
    """Create a new stock audit"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_manage_access_control'):
        messages.error(request, 'You do not have permission to create audits.')
        return redirect('/')
    
    if request.method == 'POST':
        form = StockAuditForm(request.POST, user=request.user)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.created_by = request.user
            audit.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Create audit items based on selected criteria
            create_audit_items(audit)
            
            messages.success(request, f'Stock audit "{audit.title}" created successfully.')
            return redirect('audit_detail', audit_id=audit.pk)
    else:
        form = StockAuditForm(user=request.user)
    
    context = {
        'title': 'Create Stock Audit',
        'form': form,
    }
    return render(request, 'stock/create_audit.html', context)


def create_audit_items(audit):
    """Create audit items based on audit criteria"""
    stock_queryset = Stock.objects.filter(quantity__gt=0)
    
    # Filter by locations if specified
    if audit.audit_locations.exists():
        stock_queryset = stock_queryset.filter(location__in=audit.audit_locations.all())
    
    # Filter by categories if specified
    if audit.audit_categories.exists():
        stock_queryset = stock_queryset.filter(category__in=audit.audit_categories.all())
    
    audit_items = []
    for stock in stock_queryset:
        audit_item = StockAuditItem(
            audit=audit,
            stock=stock,
            system_quantity=stock.quantity,
            committed_quantity=stock.committed_quantity or 0,
            reserved_quantity=stock.reserved_quantity or 0,
        )
        audit_items.append(audit_item)
    
    # Bulk create audit items
    StockAuditItem.objects.bulk_create(audit_items)
    
    # Update audit totals
    audit.total_items_planned = len(audit_items)
    audit.save()


@login_required
def start_audit(request, audit_id):
    """Start an audit by changing its status to in_progress"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_manage_access_control'):
        messages.error(request, 'You do not have permission to start audits.')
        return redirect('/')
    
    audit = get_object_or_404(StockAudit, pk=audit_id)
    
    if audit.status != 'planned':
        messages.error(request, f'Cannot start audit. Current status: {audit.get_status_display()}')
        return redirect('audit_detail', audit_id=audit.pk)
    
    # Start the audit
    from django.utils import timezone
    audit.status = 'in_progress'
    audit.actual_start_date = timezone.now()
    audit.save()
    
    messages.success(request, f'Audit "{audit.title}" has been started.')
    return redirect('audit_detail', audit_id=audit.pk)


@login_required
def count_items(request, audit_id):
    """Bulk counting form for audit items"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, 'You do not have permission to count items.')
        return redirect('/')
    
    audit = get_object_or_404(StockAudit, pk=audit_id)
    
    if audit.status != 'in_progress':
        messages.error(request, 'Audit must be in progress to count items.')
        return redirect('audit_detail', audit_id=audit.pk)
    
    if request.method == 'POST':
        form = AuditItemBulkCountForm(request.POST, audit=audit)
        if form.is_valid():
            updated_items = form.save(audit, request.user)
            
            # Update audit statistics
            audit.update_statistics()
            
            messages.success(request, f'Updated counts for {len(updated_items)} items.')
            return redirect('audit_detail', audit_id=audit.pk)
    else:
        form = AuditItemBulkCountForm(audit=audit)
    
    context = {
        'title': f'Count Items: {audit.audit_reference}',
        'audit': audit,
        'form': form,
        'uncounted_items': audit.audit_items.filter(physical_count__isnull=True).count(),
    }
    return render(request, 'stock/count_items.html', context)


@login_required
def count_single_item(request, audit_id, item_id):
    """Count a single audit item"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_view_stock'):
        messages.error(request, 'You do not have permission to count items.')
        return redirect('/')
    
    audit = get_object_or_404(StockAudit, pk=audit_id)
    audit_item = get_object_or_404(StockAuditItem, pk=item_id, audit=audit)
    
    if audit.status != 'in_progress':
        messages.error(request, 'Audit must be in progress to count items.')
        return redirect('audit_detail', audit_id=audit.pk)
    
    if request.method == 'POST':
        form = StockAuditItemForm(request.POST, instance=audit_item)
        if form.is_valid():
            audit_item = form.save(commit=False)
            audit_item.counted_by = request.user
            from django.utils import timezone
            audit_item.count_date = timezone.now()
            audit_item.save()
            
            # Update audit statistics
            audit.update_statistics()
            
            messages.success(request, f'Updated count for {audit_item.stock.item_name}.')
            return redirect('audit_detail', audit_id=audit.pk)
    else:
        form = StockAuditItemForm(instance=audit_item)
    
    context = {
        'title': f'Count Item: {audit_item.stock.item_name}',
        'audit': audit,
        'audit_item': audit_item,
        'form': form,
    }
    return render(request, 'stock/count_single_item.html', context)


@login_required
def complete_audit(request, audit_id):
    """Complete an audit"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_manage_access_control'):
        messages.error(request, 'You do not have permission to complete audits.')
        return redirect('/')
    
    audit = get_object_or_404(StockAudit, pk=audit_id)
    
    if audit.status != 'in_progress':
        messages.error(request, 'Only in-progress audits can be completed.')
        return redirect('audit_detail', audit_id=audit.pk)
    
    # Check if all items have been counted
    uncounted_items = audit.audit_items.filter(physical_count__isnull=True).count()
    if uncounted_items > 0:
        messages.warning(
            request, 
            f'Audit has {uncounted_items} uncounted items. Complete all counts before finishing the audit.'
        )
        return redirect('audit_detail', audit_id=audit.pk)
    
    # Complete the audit
    from django.utils import timezone
    audit.status = 'completed'
    audit.actual_end_date = timezone.now()
    audit.update_statistics()
    audit.save()
    
    messages.success(request, f'Audit "{audit.title}" has been completed.')
    return redirect('audit_detail', audit_id=audit.pk)


@login_required
def approve_audit(request, audit_id):
    """Approve a completed audit and apply adjustments"""
    from .utils.permissions import has_permission
    if not has_permission(request.user, 'can_manage_access_control'):
        messages.error(request, 'You do not have permission to approve audits.')
        return redirect('/')
    
    audit = get_object_or_404(StockAudit, pk=audit_id)
    
    if audit.status != 'completed':
        messages.error(request, 'Only completed audits can be approved.')
        return redirect('audit_detail', audit_id=audit.pk)
    
    if request.method == 'POST':
        # Apply stock adjustments for items with variances
        variance_items = audit.audit_items.exclude(variance_quantity=0)
        adjustments_applied = 0
        
        for item in variance_items:
            if not item.adjustment_applied:
                # Apply the adjustment to actual stock
                stock = item.stock
                stock.quantity = item.physical_count
                stock.save()
                
                # Mark adjustment as applied
                from django.utils import timezone
                item.adjustment_applied = True
                item.adjustment_date = timezone.now()
                item.save()
                
                adjustments_applied += 1
        
        # Approve the audit
        audit.status = 'approved'
        audit.approved_by = request.user
        audit.save()
        
        messages.success(
            request, 
            f'Audit approved. Applied {adjustments_applied} stock adjustments.'
        )
        return redirect('audit_detail', audit_id=audit.pk)
    
    # Show confirmation page
    variance_items = audit.audit_items.exclude(variance_quantity=0)
    context = {
        'title': f'Approve Audit: {audit.audit_reference}',
        'audit': audit,
        'variance_items': variance_items,
    }
    return render(request, 'stock/approve_audit.html', context)


@login_required
def stock_item_suggestions(request):
    """AJAX endpoint for stock item autocomplete suggestions"""
    from django.http import JsonResponse
    from django.db.models import Q
    
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Search for existing stock items with similar names
    stock_items = Stock.objects.filter(
        Q(item_name__icontains=query) | 
        Q(category__group__icontains=query)
    ).select_related('category', 'location').distinct()[:10]
    
    # Also search for previous PO items to avoid duplicates
    po_items = PurchaseOrderItem.objects.filter(
        product__icontains=query
    ).values_list('product', flat=True).distinct()[:10]
    
    suggestions = []
    
    # Add existing stock items (higher priority)
    for stock in stock_items:
        suggestions.append({
            'type': 'existing_stock',
            'name': stock.item_name,
            'category': stock.category.group if stock.category else '',
            'store': stock.location.name if stock.location else '',
            'quantity': stock.quantity,
            'unit': 'pcs',
            'label': f"{stock.item_name} (In Stock: {stock.quantity} pcs)",
            'priority': 1
        })
    
    # Add previous PO items (lower priority)
    for po_item in po_items:
        if not any(s['name'].lower() == po_item.lower() for s in suggestions):
            suggestions.append({
                'type': 'previous_order',
                'name': po_item,
                'label': f"{po_item} (Previously ordered)",
                'priority': 2
            })
    
    # Sort by priority and name
    suggestions.sort(key=lambda x: (x['priority'], x['name'].lower()))
    
    return JsonResponse({'suggestions': suggestions[:15]})