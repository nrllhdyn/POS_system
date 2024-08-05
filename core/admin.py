from django.contrib import admin

from .models import Category, Floor, MenuItem, Order, OrderItem, Payment, Restaurant, Stock, Table , IncomeExpense, IncomeExpenseCategory

# Register your models here.

admin.site.register(Restaurant)
admin.site.register(Floor)
admin.site.register(Table)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(IncomeExpense)
admin.site.register(IncomeExpenseCategory)

class StockAdmin(admin.ModelAdmin):
  list_display = ('menu_item', 'restaurant', 'quantity', 'warning_threshold')
  list_filter = ('restaurant', 'menu_item')

admin.site.register(Stock, StockAdmin)

class MenuItemAdmin(admin.ModelAdmin):
  list_display = ('name', 'price', 'category', 'track_stock')
  list_filter = ('category', 'track_stock')

admin.site.register(MenuItem, MenuItemAdmin)

