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
    CommittedStockViewSet, StockReservationViewSet, StockTransferViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()

# Stock management endpoints
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'stock-history', StockHistoryViewSet, basename='stockhistory')
router.register(r'committed-stock', CommittedStockViewSet, basename='committedstock')
router.register(r'reservations', StockReservationViewSet, basename='stockreservation')
router.register(r'transfers', StockTransferViewSet, basename='stocktransfer')

# API patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API Documentation endpoints
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints
    path('v1/', include(router.urls)),
]