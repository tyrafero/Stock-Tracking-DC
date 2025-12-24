from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import UserRole

def get_user_role(user):
    """Get user's role object"""
    try:
        return user.role
    except UserRole.DoesNotExist:
        # Create default sales role for users without roles
        role = UserRole.objects.create(user=user, role='sales')
        return role

def has_permission(user, permission):
    """Check if user has specific permission"""
    if not user.is_authenticated:
        return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    role = get_user_role(user)
    return role.has_permission(permission)

def require_permission(permission, redirect_url='/'):
    """Decorator to require specific permission"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not has_permission(request.user, permission):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_any_permission(*permissions, redirect_url='/'):
    """Decorator to require at least one of the specified permissions"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not any(has_permission(request.user, perm) for perm in permissions):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_role(*roles, redirect_url='/'):
    """Decorator to require specific role(s)"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            user_role = get_user_role(request.user)
            if user_role.role not in roles:
                messages.error(request, 'You do not have the required role to access this page.')
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def filter_purchase_order_data(purchase_order, user):
    """Filter purchase order data based on user permissions"""
    if not has_permission(user, 'can_view_purchase_order_amounts'):
        # Hide amount-related fields for warehouse users
        filtered_data = {
            'id': purchase_order.id,
            'reference_number': purchase_order.reference_number,
            'manufacturer': purchase_order.manufacturer,
            'delivery_person': purchase_order.delivery_person,
            'delivery_type': purchase_order.delivery_type,
            'store': purchase_order.store,
            'status': purchase_order.status,
            'created_at': purchase_order.created_at,
            'updated_at': purchase_order.updated_at,
            'note_for_manufacturer': purchase_order.note_for_manufacturer,
            'items': []
        }
        
        # Filter items too
        for item in purchase_order.items.all():
            filtered_item = {
                'id': item.id,
                'product': item.product,
                'quantity': item.quantity,
                'received_quantity': item.received_quantity,
                'associated_order_number': item.associated_order_number,
                # Hide price and discount information
            }
            filtered_data['items'].append(filtered_item)
        
        return filtered_data
    else:
        return purchase_order

class PermissionMixin:
    """Mixin to add permission checking to class-based views"""
    required_permission = None
    required_permissions = None
    required_role = None
    required_roles = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check single permission
        if self.required_permission and not has_permission(request.user, self.required_permission):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # Check multiple permissions (all required)
        if self.required_permissions:
            if not all(has_permission(request.user, perm) for perm in self.required_permissions):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('/')
        
        # Check single role
        if self.required_role:
            user_role = get_user_role(request.user)
            if not request.user.is_superuser and user_role.role != self.required_role:
                messages.error(request, 'You do not have the required role to access this page.')
                return redirect('/')
        
        # Check multiple roles (any one required)
        if self.required_roles:
            user_role = get_user_role(request.user)
            if not request.user.is_superuser and user_role.role not in self.required_roles:
                messages.error(request, 'You do not have the required role to access this page.')
                return redirect('/')
        
        return super().dispatch(request, *args, **kwargs)