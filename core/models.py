from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your models here.

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    owner_phone = models.CharField(max_length=14)
    restaurant_phone = models.CharField(max_length=14)

    def __str__(self):
        return self.name

class Floor(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='floors')
    name = models.CharField(max_length=50)  

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
    ]
    number = models.IntegerField()
    capacity = models.IntegerField()
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='tables')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Table {self.number} ({self.floor})"
    
    def close_table(self):
        self.status = 'available'
        self.save()
        for order in self.orders.filter(status__in=['pending', 'preparing', 'ready', 'delivered']):
            order.complete()

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

    class Meta:
        unique_together = ('restaurant', 'name')

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    track_stock = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category.restaurant.name} - {self.name}"
    
    def get_stock(self, restaurant):
        stock = self.stocks.filter(restaurant=restaurant).first()
        return stock.quantity if stock else None
    
    def update_stock(self, restaurant, quantity):
        stock, _ = self.stocks.get_or_create(restaurant=restaurant)
        stock.quantity -= quantity
        if stock.quantity < 0:
            raise ValidationError("Not enough stock available.")
        stock.save()

class Order(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    table = models.ForeignKey('Table', on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.table.floor.restaurant.name} - Order {self.id} - Table {self.table.number}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all()) - self.discount
    
    def get_total_with_discount(self):
        return self.get_total() - self.discount
    
    def get_total_paid(self):
        return self.payments.aggregate(total=models.Sum('amount'))['total'] or 0

    def get_remaining_amount(self):
        total_paid = sum(payment.amount for payment in self.payments.all())
        return self.get_total_with_discount() - total_paid

    def complete(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    is_cancelled = models.BooleanField(default=False)
    cancelled_quantity = models.PositiveIntegerField(default=0)
    cancellation_reason = models.TextField(blank=True, null=True)

    
    def get_subtotal(self):
        return (self.quantity - self.cancelled_quantity) * self.menu_item.price

    def __str__(self):
        return f"{self.order} - {self.menu_item.name}"
    
    def save(self, *args, **kwargs):
        if self.menu_item.track_stock:
            self.menu_item.update_stock(self.order.table.floor.restaurant, self.quantity)
        super().save(*args, **kwargs)
    
class IncomeExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    is_income = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class IncomeExpense(models.Model):
    TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='income_expenses')
    category = models.ForeignKey(IncomeExpenseCategory, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} - {self.date}"

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
    ]
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='credit_card')
    created_at = models.DateTimeField(auto_now_add=True)
    income = models.OneToOneField(IncomeExpense, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.payment_type} payment of {self.amount} for Order {self.order.id}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.income:
            category_name = f'Table {self.get_payment_type_display()}'
            income = IncomeExpense.objects.create(
                restaurant=self.order.table.floor.restaurant,
                category=IncomeExpenseCategory.objects.get_or_create(name=category_name, is_income=True)[0],
                type='income',
                amount=self.amount,
                description=f"Table {self.get_payment_type_display()} Payment for Order #{self.order.id}",
                date=self.created_at.date(),
                created_by=None
            )
            self.income = income
            super().save(update_fields=['income'])

class Stock(models.Model):
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='stocks')
    menu_item = models.ForeignKey('MenuItem', on_delete=models.CASCADE, related_name='stocks')
    quantity = models.PositiveIntegerField(default=0)
    warning_threshold = models.PositiveIntegerField(default=10)

    class Meta:
        unique_together = ('restaurant', 'menu_item')

    def __str__(self):
        return f"{self.menu_item.name} - {self.restaurant.name}"

    def clean(self):
        if self.warning_threshold > self.quantity:
            raise ValidationError("Warning threshold cannot be greater than the quantity.")

class Staff(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Restaurant Admin'),
        ('waiter', 'Waiter'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role} at {self.restaurant.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['restaurant', 'user'], name='unique_staff_per_restaurant')
        ]
