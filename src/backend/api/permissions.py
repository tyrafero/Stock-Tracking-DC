from rest_framework import permissions


class StockPermissions(permissions.BasePermission):
    """
    Custom permission class for stock operations based on user roles
    """

    def has_permission(self, request, view):
        """
        Check if user has permission to access stock endpoints
        """
        if not request.user.is_authenticated:
            return False

        # Get user role
        try:
            user_role = request.user.role
        except:
            # If user doesn't have a role assigned, deny access
            return False

        # Define permissions based on HTTP method and view action
        if view.action == 'list' or view.action == 'retrieve':
            # All authenticated users with roles can view stock
            return user_role.has_permission('can_view_stock')

        elif view.action == 'create':
            return user_role.has_permission('can_create_stock')

        elif view.action in ['update', 'partial_update']:
            return user_role.has_permission('can_edit_stock')

        elif view.action == 'destroy':
            # Only admin and owner can delete stock
            return user_role.role in ['admin', 'owner']

        elif view.action in ['issue_stock', 'receive_stock']:
            # Check specific permissions for stock operations
            if view.action == 'issue_stock':
                return user_role.has_permission('can_issue_stock')
            elif view.action == 'receive_stock':
                return user_role.has_permission('can_receive_stock')

        elif view.action in ['reserve_stock', 'commit_stock']:
            # Check transfer and commit permissions
            if view.action == 'commit_stock':
                return user_role.has_permission('can_commit_stock')
            elif view.action == 'reserve_stock':
                return user_role.has_permission('can_transfer_stock')

        elif view.action in ['stock_history', 'stock_locations']:
            # Read-only actions follow view permissions
            return user_role.has_permission('can_view_stock')

        # Stocktake/Audit actions
        elif view.action in ['start', 'complete', 'cancel', 'approve']:
            # Allow managers, warehouse staff, and admins to manage stocktakes
            return user_role.role in ['admin', 'owner', 'warehouse', 'stocktake_manager']

        elif view.action in ['items', 'count_item']:
            # Allow any authenticated user with stock view permission to count items
            return user_role.has_permission('can_view_stock')

        # Default to requiring admin/owner for any other actions
        return user_role.role in ['admin', 'owner']

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions
        """
        if not request.user.is_authenticated:
            return False

        try:
            user_role = request.user.role
        except:
            return False

        # For stock objects, check the same permissions as has_permission
        return self.has_permission(request, view)


class PurchaseOrderPermissions(permissions.BasePermission):
    """
    Custom permission class for purchase order operations
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            user_role = request.user.role
        except:
            return False

        if view.action in ['list', 'retrieve']:
            return user_role.has_permission('can_view_purchase_order')

        elif view.action == 'create':
            return user_role.has_permission('can_create_purchase_order')

        elif view.action in ['update', 'partial_update']:
            return user_role.has_permission('can_edit_purchase_order')

        elif view.action == 'destroy':
            # Only admin and owner can delete POs
            return user_role.role in ['admin', 'owner']

        elif view.action in ['receive_items']:
            return user_role.has_permission('can_receive_purchase_order')

        return user_role.role in ['admin', 'owner']


class TransferPermissions(permissions.BasePermission):
    """
    Custom permission class for stock transfer operations
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            user_role = request.user.role
        except:
            return False

        if view.action in ['list', 'retrieve']:
            # Most roles can view transfers
            return user_role.has_permission('can_transfer_stock')

        elif view.action == 'create':
            return user_role.has_permission('can_transfer_stock')

        elif view.action in ['approve_transfer', 'complete_transfer', 'mark_collected']:
            # Transfer operations require warehouse or logistics permissions
            return user_role.role in ['admin', 'owner', 'warehouse', 'logistics', 'stocktake_manager']

        return user_role.role in ['admin', 'owner']


class CommittedStockPermissions(permissions.BasePermission):
    """
    Custom permission class for committed stock operations
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            user_role = request.user.role
        except:
            return False

        if view.action in ['list', 'retrieve']:
            return user_role.has_permission('can_view_stock')

        elif view.action == 'create':
            return user_role.has_permission('can_commit_stock')

        elif view.action == 'fulfill_commitment':
            return user_role.has_permission('can_fulfill_commitment')

        return user_role.role in ['admin', 'owner']


class ReservationPermissions(permissions.BasePermission):
    """
    Custom permission class for stock reservation operations
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            user_role = request.user.role
        except:
            return False

        # Most roles can manage reservations as they're temporary
        return user_role.has_permission('can_transfer_stock')


class ViewOnlyPermission(permissions.BasePermission):
    """
    Permission class that allows read-only access
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            user_role = request.user.role
        except:
            return False

        # Allow read operations for users who can view stock
        if request.method in permissions.SAFE_METHODS:
            return user_role.has_permission('can_view_stock')

        return False