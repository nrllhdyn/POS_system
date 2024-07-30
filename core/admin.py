from django.contrib import admin

from .models import Category, Floor, MenuItem, Order, OrderItem, Restaurant, Table

# Register your models here.

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Restaurant)
admin.site.register(Floor)
admin.site.register(Table)

