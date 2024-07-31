from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurant/<int:restaurant_id>/floors/', views.floor_list, name='floor_list'),
    path('restaurant/<int:restaurant_id>/add-floor/', views.add_floor, name='add_floor'),
    path('restaurant/<int:restaurant_id>/menu/', views.menu_management, name='menu_management'),
    path('restaurant/<int:restaurant_id>/income-expenses/', views.income_expense_list, name='income_expense_list'),
    path('restaurant/<int:restaurant_id>/add-income-expense/', views.add_income_expense, name='add_income_expense'),
    path('add-income-expense-category/', views.add_income_expense_category, name='add_income_expense_category'),
    path('restaurant/<int:restaurant_id>/add-category/', views.add_category, name='add_category'),
    path('floor/<int:floor_id>/add-table/', views.add_table, name='add_table'),
    path('floor/<int:floor_id>/tables/', views.table_list, name='table_list'),
    path('floor/<int:floor_id>/edit/', views.edit_floor, name='edit_floor'),
    path('floor/<int:floor_id>/delete/', views.delete_floor, name='delete_floor'),
    path('table/<int:table_id>/edit/', views.edit_table, name='edit_table'),
    path('table/<int:table_id>/delete/', views.delete_table, name='delete_table'),
    path('category/<int:category_id>/add-menu-item/', views.add_menu_item, name='add_menu_item'),
    path('table/<int:table_id>/order/', views.create_order, name='create_order'),
    path('table/<int:table_id>/', views.table_detail, name='table_detail'),
    path('table/<int:table_id>/close/', views.close_table, name='close_table'),
    path('table/<int:from_table_id>/transfer/', views.transfer_table, name='transfer_table'),
    path('table/<int:table_id>/payment/', views.payment_view, name='payment_view'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('order-item/<int:order_item_id>/edit/', views.delete_order_item, name='delete_order_item'),
]