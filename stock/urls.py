from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', views.get_client_ip, name="home"),
    path('search/', views.global_search, name="global_search"),
    path('api/live-search/', views.live_search, name="live_search"),
    path('view_stock', views.view_stock, name="view_stock"),
    path('add_stock', views.add_stock, name="add_stock"),
    path('update_stock/<str:pk>/', views.update_stock, name="update_stock"),
    path('delete_stock/<str:pk>/', views.delete_stock, name="delete_stock"),
    path('stock_detail/<str:pk>/', views.stock_detail, name="stock_detail"),
    path('issue_item/<str:pk>/', views.issue_item, name="issue_item"),
    path('receive_item/<str:pk>/', views.receive_item, name="receive_item"),
    path('commit_stock/<str:pk>/', views.commit_stock, name="commit_stock"),
    path('fulfill_commitment/<int:pk>/', views.fulfill_commitment, name="fulfill_commitment"),
    path('cancel_commitment/<int:pk>/', views.cancel_commitment, name="cancel_commitment"),
    path('transfer_stock/<str:pk>/', views.transfer_stock, name="transfer_stock"),
    path('transfers/', views.transfer_list, name="transfer_list"),
    path('transfers/<int:pk>/approve/', views.approve_transfer, name="approve_transfer"),
    path('transfers/<int:pk>/complete/', views.complete_transfer, name="complete_transfer"),
    path('transfers/<int:pk>/collect/', views.mark_collected, name="mark_collected"),
    path('transfers/<int:pk>/cancel/', views.cancel_transfer, name="cancel_transfer"),
    path('re_order/<str:pk>/', views.re_order, name="re_order"),
    path("register", RedirectView.as_view(url="/accounts/register/", permanent=True)),
    path('view_history', views.view_history, name="view_history"),
    path('dependent_forms', views.dependent_forms, name='dependent_forms'),
    path('dependent_update/<str:pk>/', views.dependent_forms_update, name='dependent_update'),
    path('depend_form_view', views.dependent_forms_view, name='depend_form_view'),
    path('depend_form_delete/<str:pk>', views.delete_dependant, name='delete_dependant'),
    path('ajax/load-states/', views.load_stats, name='ajax_load_states'),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    path('scrumboard', views.scrum_list, name='scrumboard'),
    path('scrumboard_view', views.scrum_view, name='scrumboard_view'),
    path('contacts', views.contact, name='contacts'),
    path('debug/', views.debug_info, name='debug_info'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/update/', views.update_purchase_order, name='update_purchase_order'),
    path('purchase-orders/<int:pk>/submit/', views.submit_purchase_order, name='submit_purchase_order'),
    path('purchase-orders/<int:pk>/send-email/', views.send_purchase_order_email, name='send_purchase_order_email'),
    path('purchase-orders/<int:pk>/history/', views.purchase_order_history, name='purchase_order_history'),
    path('purchase-order/<int:pk>/receive/', views.receive_purchase_order_items, name='receive_purchase_order_items'),
    path('purchase-order/<int:pk>/receiving-history/', views.purchase_order_receiving_history, name='purchase_order_receiving_history'),
    path('purchase-order/<int:pk>/receiving-summary-api/', views.receiving_summary_api, name='receiving_summary_api'),

    
    # AJAX endpoints
    path('api/manufacturer-details/', views.get_manufacturer_details, name='get_manufacturer_details'),
    
    # Management URLs
    path('manufacturers/', views.manage_manufacturers, name='manage_manufacturers'),
    path('manufacturers/add/', views.add_manufacturer, name='add_manufacturer'),
    path('manufacturers/<int:pk>/edit/', views.edit_manufacturer, name='edit_manufacturer'),
    path('manufacturers/<int:pk>/delete/', views.delete_manufacturer, name='delete_manufacturer'),
    
    path('delivery-persons/', views.manage_delivery_persons, name='manage_delivery_persons'),
    path('delivery-persons/add/', views.add_delivery_person, name='add_delivery_person'),
    path('delivery-persons/<int:pk>/edit/', views.edit_delivery_person, name='edit_delivery_person'),
    path('delivery-persons/<int:pk>/delete/', views.delete_delivery_person, name='delete_delivery_person'),
    
    path('stores/', views.manage_stores, name='manage_stores'),
    path('stores/add/', views.add_store, name='add_store'),
    path('stores/<int:pk>/edit/', views.edit_store, name='edit_store'),
    path('stores/<int:pk>/delete/', views.delete_store, name='delete_store'),
    
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    # Access Control URLs
    path('access-control/', views.manage_users, name='manage_users'),
    path('access-control/add-user/', views.add_user, name='add_user'),
    path('access-control/edit-user/<int:pk>/', views.edit_user, name='edit_user'),
    path('access-control/delete-user/<int:pk>/', views.delete_user, name='delete_user'),
    
    # Warehouse URLs
    path('warehouse/receiving/', views.warehouse_receiving, name='warehouse_receiving'),
    
    # Receive PO Items URL - Unified interface
    path('receive-po-items/', views.receive_purchase_order_items, name='receive_po_items'),
    
    # Stock Reservation URLs
    path('stock/<str:pk>/reserve/', views.reserve_stock, name='reserve_stock'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:pk>/update/', views.update_reservation, name='update_reservation'),
    path('reservations/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('reservations/<int:pk>/fulfill/', views.fulfill_reservation, name='fulfill_reservation'),
    path('reservations/expire/', views.expire_reservations, name='expire_reservations'),
    
    # Stock Audit URLs
    path('audits/', views.audit_list, name='audit_list'),
    path('audits/<int:audit_id>/', views.audit_detail, name='audit_detail'),
    path('audits/create/', views.create_audit, name='create_audit'),
    path('audits/<int:audit_id>/start/', views.start_audit, name='start_audit'),
    path('audits/<int:audit_id>/count/', views.count_items, name='count_items'),
    path('audits/<int:audit_id>/count/<int:item_id>/', views.count_single_item, name='count_single_item'),
    path('audits/<int:audit_id>/complete/', views.complete_audit, name='complete_audit'),
    path('audits/<int:audit_id>/approve/', views.approve_audit, name='approve_audit'),

    path('accounts/', include('registration.backends.default.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Always serve media files in development (even when DEBUG=False)
# This helps with local development when Cloudinary isn't properly configured
import os
if not os.environ.get('RAILWAY_ENVIRONMENT'):  # Only for local development
    from django.views.static import serve
    from django.urls import re_path
    
    def serve_media(request, path):
        """Serve media files locally during development"""
        media_root = os.path.join(settings.BASE_DIR, 'media')
        return serve(request, path, document_root=media_root)
    
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media),
        re_path(r'^/(?P<path>stock/images/.*)$', serve_media),  # Handle direct stock image paths
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)