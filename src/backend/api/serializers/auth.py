from rest_framework import serializers
from django.contrib.auth.models import User
from stock.models import UserRole


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['role', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    role = UserRoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'role']
        read_only_fields = ['id', 'username', 'is_active', 'date_joined']


class UserPermissionsSerializer(serializers.Serializer):
    """Serializer for user role permissions"""
    can_manage_users = serializers.BooleanField(read_only=True)
    can_manage_access_control = serializers.BooleanField(read_only=True)
    can_create_purchase_order = serializers.BooleanField(read_only=True)
    can_edit_purchase_order = serializers.BooleanField(read_only=True)
    can_view_purchase_order = serializers.BooleanField(read_only=True)
    can_receive_purchase_order = serializers.BooleanField(read_only=True)
    can_view_purchase_order_amounts = serializers.BooleanField(read_only=True)
    can_create_stock = serializers.BooleanField(read_only=True)
    can_edit_stock = serializers.BooleanField(read_only=True)
    can_view_stock = serializers.BooleanField(read_only=True)
    can_transfer_stock = serializers.BooleanField(read_only=True)
    can_commit_stock = serializers.BooleanField(read_only=True)
    can_fulfill_commitment = serializers.BooleanField(read_only=True)
    can_issue_stock = serializers.BooleanField(read_only=True)
    can_receive_stock = serializers.BooleanField(read_only=True)
    can_view_warehouse_receiving = serializers.BooleanField(read_only=True)
    can_manage_payments = serializers.BooleanField(read_only=True)
    can_create_invoices = serializers.BooleanField(read_only=True)
    can_view_financial_reports = serializers.BooleanField(read_only=True)