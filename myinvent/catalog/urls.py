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
]