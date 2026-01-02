from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views.stock import (
    CategoryViewSet, StoreViewSet, StockViewSet, StockHistoryViewSet,
    CommittedStockViewSet, StockReservationViewSet, StockTransferViewSet,
    ManufacturerViewSet, DeliveryPersonViewSet, StockLocationViewSet
)
from .views.purchase_orders import PurchaseOrderViewSet, InvoiceViewSet, PaymentViewSet
from .views.stocktake import StockAuditViewSet
from .views.auth import user_profile, update_profile, user_permissions, check_permission
from .views.health import health_check

# Create a router and register our viewsets
router = DefaultRouter()

# Stock management endpoints
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'manufacturers', ManufacturerViewSet, basename='manufacturer')
router.register(r'delivery-persons', DeliveryPersonViewSet, basename='deliveryperson')
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'stock-locations', StockLocationViewSet, basename='stocklocation')
router.register(r'stock-history', StockHistoryViewSet, basename='stockhistory')
router.register(r'committed-stock', CommittedStockViewSet, basename='committedstock')
router.register(r'reservations', StockReservationViewSet, basename='stockreservation')
router.register(r'transfers', StockTransferViewSet, basename='stocktransfer')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'stock-audits', StockAuditViewSet, basename='stockaudit')

# API patterns
urlpatterns = [
    # Health check endpoint (for Docker health checks)
    path('v1/health/', health_check, name='health_check'),

    # Authentication endpoints (under v1 for consistency)
    path('v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('v1/auth/user/profile/', user_profile, name='user_profile'),
    path('v1/auth/user/update/', update_profile, name='update_profile'),
    path('v1/auth/user/permissions/', user_permissions, name='user_permissions'),
    path('v1/auth/user/check-permission/', check_permission, name='check_permission'),

    # API Documentation endpoints
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints
    path('v1/', include(router.urls)),
]