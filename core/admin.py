from django.contrib import admin
from .models import Category, Floor, MenuItem, Order, OrderItem, Payment, Restaurant, Stock, Table, IncomeExpense, IncomeExpenseCategory

class FloorInline(admin.TabularInline):
  model = Floor
  extra = 1

class RestaurantAdmin(admin.ModelAdmin):
  list_display = ('name', 'address')
  search_fields = ('name', 'address')
  inlines = [FloorInline]

class TableInline(admin.TabularInline):
  model = Table
  extra = 1

class FloorAdmin(admin.ModelAdmin):
  list_display = ('name', 'restaurant')
  list_filter = ('restaurant',)
  inlines = [TableInline]

class TableAdmin(admin.ModelAdmin):
  list_display = ('number', 'floor', 'status')
  list_filter = ('floor', 'status')
  search_fields = ('number',)

class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'restaurant')
  list_filter = ('restaurant',)
  search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
  model = OrderItem
  extra = 1

class OrderAdmin(admin.ModelAdmin):
  list_display = ('id', 'table', 'status', 'created_at')
  list_filter = ('status', 'created_at')
  search_fields = ('id', 'table__number')
  inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
  list_display = ('order', 'menu_item', 'quantity', 'notes')
  list_filter = ('order__status', 'menu_item')
  search_fields = ('order__id', 'menu_item__name')

class PaymentAdmin(admin.ModelAdmin):
  list_display = ('order', 'amount', 'payment_type', 'created_at')
  list_filter = ('payment_type', 'created_at')
  search_fields = ('order__id',)

class IncomeExpenseAdmin(admin.ModelAdmin):
  list_display = ('restaurant', 'category', 'amount', 'date', 'type')
  list_filter = ('restaurant', 'category', 'type', 'date')
  search_fields = ('description',)

class IncomeExpenseCategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'is_income')
  list_filter = ('is_income',)
  search_fields = ('name',)

class StockAdmin(admin.ModelAdmin):
  list_display = ('menu_item', 'restaurant', 'quantity', 'warning_threshold')
  list_filter = ('restaurant', 'menu_item')
  search_fields = ('menu_item__name', 'restaurant__name')

class MenuItemAdmin(admin.ModelAdmin):
  list_display = ('name', 'price', 'category', 'track_stock')
  list_filter = ('category', 'track_stock')
  search_fields = ('name', 'description')

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Floor, FloorAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(IncomeExpense, IncomeExpenseAdmin)
admin.site.register(IncomeExpenseCategory, IncomeExpenseCategoryAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(MenuItem, MenuItemAdmin)