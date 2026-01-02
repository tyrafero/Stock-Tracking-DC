from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from stock.models import UserRole
from ..serializers.auth import UserProfileSerializer, UserPermissionsSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current authenticated user's profile information
    """
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update current user's profile information
    """
    user = request.user
    serializer = UserProfileSerializer(user, data=request.data, partial=request.method == 'PATCH')

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request):
    """
    Get current user's role permissions
    """
    try:
        user_role = request.user.role
        permissions = user_role.role_permissions
        serializer = UserPermissionsSerializer(permissions)
        return Response(serializer.data)
    except UserRole.DoesNotExist:
        return Response(
            {"error": "User role not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_permission(request):
    """
    Check if current user has a specific permission
    """
    permission_name = request.data.get('permission')
    if not permission_name:
        return Response(
            {"error": "Permission name is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_role = request.user.role
        has_permission = user_role.has_permission(permission_name)
        return Response({"has_permission": has_permission})
    except UserRole.DoesNotExist:
        return Response({"has_permission": False})