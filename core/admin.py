from django.contrib import admin

from .models import Category, Floor, MenuItem, Order, OrderItem, Payment, Restaurant, Table , IncomeExpense, IncomeExpenseCategory

# Register your models here.

admin.site.register(Restaurant)
admin.site.register(Floor)
admin.site.register(Table)
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(IncomeExpense)
admin.site.register(IncomeExpenseCategory)

