from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('materials/',views.items,name='material_list'),
    path('materials/add/',views.add_material,name='add_material'),
    path('transactions/',views.transaction_history,name='transaction_history'),
    path('alerts/',views.low_stock_alerts,name='low_stock_alerts'),
    path('categories/',views.manage_categories,name='manage_categories'),
    path('transaction/new/', views.create_transaction, name='create_transaction'),
    path('transaction/history/', views.transaction_history, name='transaction_history'),
    path('stock/in/<int:material_id>/', views.stock_in, name='stock_in'),
    path('stock/out/<int:material_id>/', views.stock_out, name='stock_out'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('bom/', views.bom_list, name='bom_list'),
    path('bom/create/', views.create_bom, name='create_bom'),
    path('bom/<int:pk>/', views.bom_detail, name='bom_detail'),
    path('bom/item/<int:pk>/delete/', views.delete_bom_item, name='delete_bom_item'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:pk>/check/', views.check_order, name='check_order'),
    path('orders/<int:pk>/update/', views.update_order_status, name='update_order_status'),
    path('scanner/', views.scanner_view, name='scanner'),
    path('api/material/scan/<str:barcode>/', views.scan_material, name='scan_material'),
]