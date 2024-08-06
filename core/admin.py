from django.contrib import admin
from .models import Category, Floor, MenuItem, Order, OrderItem, Payment, Restaurant, Staff, Stock, Table, IncomeExpense, IncomeExpenseCategory
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class StaffInline(admin.StackedInline):
    model = Staff
    can_delete = False
    verbose_name_plural = 'Staff'

class CustomUserAdmin(UserAdmin):
    inlines = (StaffInline,)

class StaffAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user', 'restaurant', 'role', 'phone', 'get_email')
    list_filter = ('restaurant', 'role')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'user__email', 'phone', 'restaurant__name')
    ordering = ('user__last_name', 'user__first_name', 'restaurant__name')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__last_name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'

    fieldsets = (
        (None, {'fields': ('user', 'restaurant', 'role', 'phone')}),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=False, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    list_filter = ('restaurant', 'role')

class FloorInline(admin.TabularInline):
    model = Floor
    extra = 1

class RestaurantAdmin(admin.ModelAdmin):
  list_display = ('name', 'address', 'email', 'owner_phone','restaurant_phone')
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


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Staff, StaffAdmin)
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