from .utils.permissions import get_user_role

def user_role(request):
    """Add user role to template context"""
    if request.user.is_authenticated:
        try:
            role = get_user_role(request.user)
            return {
                'user_role': role,
                'user_permissions': role.role_permissions,
            }
        except Exception:
            return {'user_role': None, 'user_permissions': {}}
    return {'user_role': None, 'user_permissions': {}}