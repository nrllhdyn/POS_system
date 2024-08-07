from datetime import timedelta
import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Floor, IncomeExpense, IncomeExpenseCategory, Payment, Restaurant, Category, MenuItem, Order , OrderItem, Staff, Stock, Table
from django.contrib.auth.decorators import login_required , user_passes_test
from django.views.decorators.http import require_POST
from .forms import FloorForm, IncomeExpenseForm, SalaryForm, TableForm, StaffEditForm
from django.db.models import F, Sum, Count, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncHour, TruncDay
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User, Group
# Create your views here.
def home(request):
    contex = {
        'page_title':'Home',
        'welcome_message':'Welcome to Restaurant POS System',
    }
    return render(request,'core/home.html',contex)

def is_restaurant_admin(user):
    return user.groups.filter(name='Restaurant Admin').exists()

def is_waiter_or_admin(user):
    return user.groups.filter(name__in=['Waiter', 'Restaurant Admin']).exists()

@user_passes_test(is_restaurant_admin)
def add_staff(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        role = request.POST['role']
        
        if Staff.objects.filter(restaurant=restaurant, role='waiter').count() >= 10 and role == 'waiter':
            messages.error(request, 'Maximum number of waiters reached for this restaurant.')
            return redirect('add_staff', restaurant_id=restaurant_id)
        
        try:
            user = User.objects.create_user(
                username=username, 
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            if role == 'admin':
                group = Group.objects.get(name='Restaurant Admin')
            else:
                group = Group.objects.get(name='Waiter')
            user.groups.add(group)
            
            Staff.objects.create(user=user, restaurant=restaurant, role=role, phone=phone)
            messages.success(request, f'{role.capitalize()} added successfully.')
            return redirect('restaurant_staff', restaurant_id=restaurant_id)
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    return render(request, 'core/add_staff.html', {'restaurant': restaurant})

@user_passes_test(is_restaurant_admin)
def restaurant_staff(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    staff = Staff.objects.filter(restaurant=restaurant).select_related('user')
    return render(request, 'core/restaurant_staff.html', {'restaurant': restaurant, 'staff': staff})

@user_passes_test(is_restaurant_admin)
def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        form = StaffEditForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member updated successfully.')
            return redirect('restaurant_staff', restaurant_id=staff.restaurant.id)
    else:
        form = StaffEditForm(instance=staff)
    return render(request, 'core/edit_staff.html', {'form': form, 'staff': staff})

@user_passes_test(is_restaurant_admin)
def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    restaurant_id = staff.restaurant.id
    if request.method == 'POST':
        staff.user.delete()  
        messages.success(request, 'Staff member deleted successfully.')
        return redirect('restaurant_staff', restaurant_id=restaurant_id)
    return render(request, 'core/delete_staff_confirm.html', {'staff': staff})


@user_passes_test(is_waiter_or_admin)
@login_required
def restaurant_list(request):
    restaurants = Restaurant.objects.filter(owner=request.user)
    return render(request, 'core/restaurant_list.html', {'restaurants': restaurants})

@user_passes_test(is_waiter_or_admin)
@login_required
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    floors = restaurant.floors.all()
    return render(request, 'core/restaurant_detail.html', {'restaurant': restaurant,'floors':floors})

@user_passes_test(is_restaurant_admin)
@login_required
def add_floor(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == 'POST':
        form = FloorForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            floor = form.save(commit=False)
            floor.restaurant = restaurant
            floor.save()
            messages.success(request, 'Floor added successfully.')
            return redirect('restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = FloorForm(restaurant=restaurant)
    return render(request, 'core/add_floor.html', {'form': form, 'restaurant': restaurant})

@user_passes_test(is_restaurant_admin)
@login_required
def add_table(request, floor_id):
    floor = get_object_or_404(Floor, id=floor_id, restaurant__owner=request.user)
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.floor = floor
            table.save()
            messages.success(request, 'Table added successfully.')
            return redirect('restaurant_detail', restaurant_id=floor.restaurant.id)
    else:
        form = TableForm()
    return render(request, 'core/add_table.html', {'form': form, 'floor': floor})

@user_passes_test(is_restaurant_admin)
@login_required
def edit_floor(request, floor_id):
    floor = get_object_or_404(Floor, id=floor_id, restaurant__owner=request.user)
    if request.method == 'POST':
        form = FloorForm(request.POST, instance=floor, restaurant=floor.restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Floor updated successfully.')
            return redirect('restaurant_detail', restaurant_id=floor.restaurant.id)
    else:
        form = FloorForm(instance=floor, restaurant=floor.restaurant)
    return render(request, 'core/edit_floor.html', {'form': form, 'floor': floor})

@user_passes_test(is_restaurant_admin)
@login_required
def edit_table(request, table_id):
    table = get_object_or_404(Table, id=table_id, floor__restaurant__owner=request.user)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            messages.success(request, 'Table updated successfully.')
            return redirect('restaurant_detail', restaurant_id=table.floor.restaurant.id)
    else:
        form = TableForm(instance=table)
    return render(request, 'core/edit_table.html', {'form': form, 'table': table})

@user_passes_test(is_restaurant_admin)
@login_required
def delete_floor(request, floor_id):
    floor = get_object_or_404(Floor, id=floor_id, restaurant__owner=request.user)
    if request.method == 'POST':
        restaurant_id = floor.restaurant.id
        floor.delete()
        messages.success(request, 'Floor deleted successfully.')
        return redirect('restaurant_detail', restaurant_id=restaurant_id)
    return render(request, 'core/delete_floor.html', {'floor': floor})

@user_passes_test(is_restaurant_admin)
@login_required
def delete_table(request, table_id):
    table = get_object_or_404(Table, id=table_id, floor__restaurant__owner=request.user)
    if request.method == 'POST':
        restaurant_id = table.floor.restaurant.id
        table.delete()
        messages.success(request, 'Table deleted successfully.')
        return redirect('restaurant_detail', restaurant_id=restaurant_id)
    return render(request, 'core/delete_table.html', {'table': table})

@user_passes_test(is_restaurant_admin)
@login_required
def menu_management(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    categories = restaurant.categories.all()
    return render(request, 'core/menu_management.html', {'restaurant': restaurant, 'categories': categories})

@user_passes_test(is_restaurant_admin)
@login_required
def add_category(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        Category.objects.create(restaurant=restaurant, name=name)
        messages.success(request, 'Category added successfully.')
        return redirect('menu_management', restaurant_id=restaurant.id)
    return render(request, 'core/add_category.html', {'restaurant': restaurant})

@user_passes_test(is_restaurant_admin)
@login_required
def add_menu_item(request, category_id):
    category = get_object_or_404(Category, id=category_id, restaurant__owner=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        MenuItem.objects.create(category=category, name=name, description=description, price=price)
        messages.success(request, 'Menu item added successfully.')
        return redirect('menu_management', restaurant_id=category.restaurant.id)
    return render(request, 'core/add_menu_item.html', {'category': category})

@user_passes_test(is_waiter_or_admin)
@login_required
def floor_list(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    floors = restaurant.floors.all()
    return render(request, 'core/floor_list.html', {'restaurant': restaurant, 'floors': floors})

@user_passes_test(is_waiter_or_admin)
@login_required
def table_list(request, floor_id):
    floor = get_object_or_404(Floor, id=floor_id)
    tables = floor.tables.order_by('number')
    
    context = {
        'floor': floor,
        'tables': tables,
    }
    return render(request, 'core/table_list.html', context)

@user_passes_test(is_waiter_or_admin)
@login_required
def create_order(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    restaurant = table.floor.restaurant
    
    if request.method == 'POST':
        menu_item_ids = request.POST.getlist('menu_item_ids')
        
        if menu_item_ids:
            order = Order.objects.create(table=table, status='active')
            
            for item_id in menu_item_ids:
                quantity = int(request.POST.get(f'quantities_{item_id}', 1))
                notes = request.POST.get(f'notes_{item_id}', '')
                menu_item = MenuItem.objects.get(id=item_id)
                
                try:
                    if menu_item.track_stock:
                        stock = Stock.objects.get(restaurant=restaurant, menu_item=menu_item)
                        if stock.quantity < quantity:
                            raise ValidationError(f"Not enough stock for {menu_item.name}. Available: {stock.quantity}")
                        
                        new_stock_level = stock.quantity - quantity
                        if new_stock_level <= stock.warning_threshold:
                            messages.warning(request, f"Low stock warning for {menu_item.name}. Current stock: {new_stock_level}")
                    
                    order_item = OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity, notes=notes)
                    
                    if menu_item.track_stock:
                        stock.quantity = new_stock_level
                        stock.save()
                
                except ValidationError as e:
                    messages.error(request, str(e))
                    order.delete()
                    return redirect('create_order', table_id=table.id)
            
            table.status = 'occupied'
            table.save()
            
            messages.success(request, 'Order created successfully.')
            return redirect('table_detail', table_id=table.id)
    
    menu_items = MenuItem.objects.filter(category__restaurant=restaurant)
    for item in menu_items:
        item.current_stock = item.get_stock(restaurant)

    return render(request, 'core/create_order.html', {'table': table, 'menu_items': menu_items})

@user_passes_test(is_waiter_or_admin)
@login_required
def close_table(request, table_id):
  table = get_object_or_404(Table, id=table_id)
  restaurant_id = table.floor.restaurant.id  # Masanın bağlı olduğu restoranın ID'sini al
  
  if request.method == 'POST':
      # Masayı kapat
      table.status = 'available'
      table.save()
      
      # Aktif siparişleri tamamla
      active_orders = table.orders.filter(status='active')
      for order in active_orders:
          order.status = 'completed'
          order.save()
  
  return redirect('floor_list', restaurant_id=restaurant_id)

@user_passes_test(is_waiter_or_admin)
@login_required
def table_detail(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    active_orders = table.orders.filter(status='active').order_by('-created_at')
    return render(request, 'core/table_detail.html', {'table': table, 'active_orders': active_orders})

@user_passes_test(is_waiter_or_admin)
@login_required
def transfer_table(request, from_table_id):
    # Get the staff member and their associated restaurant
    staff = get_object_or_404(Staff, user=request.user)
    restaurant = staff.restaurant

    # Get the from_table, ensuring it belongs to the staff's restaurant
    from_table = get_object_or_404(Table, id=from_table_id, floor__restaurant=restaurant)
    
    if request.method == 'POST':
        to_table_id = request.POST.get('to_table_id')
        # Ensure the to_table also belongs to the same restaurant
        to_table = get_object_or_404(Table, id=to_table_id, floor__restaurant=restaurant)
        
        if to_table.status != 'available':
            messages.error(request, 'The destination table is not available.')
            return redirect('table_detail', table_id=from_table_id)
        
        # Transfer orders
        active_orders = from_table.orders.filter(status='active')
        for order in active_orders:
            order.table = to_table
            order.save()
        
        # Update table statuses
        from_table.status = 'available'
        from_table.save()
        to_table.status = 'occupied'
        to_table.save()
        
        messages.success(request, f'Orders transferred from Table {from_table.number} to Table {to_table.number}.')
        return redirect('table_detail', table_id=to_table_id)
    
    # If GET request, show form to select destination table
    available_tables = Table.objects.filter(
        floor__restaurant=restaurant,
        status='available'
    ).exclude(id=from_table_id)
    
    return render(request, 'core/transfer_table.html', {'from_table': from_table, 'available_tables': available_tables})

@user_passes_test(is_waiter_or_admin)
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, table__floor__restaurant__owner=request.user)
    return render(request, 'core/order_detail.html', {'order': order})

@user_passes_test(is_waiter_or_admin)
@login_required
def delete_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = order_item.order

    if request.method == 'POST':
        decrease_amount = int(request.POST.get('decrease_amount', 0))
        if 0 < decrease_amount <= order_item.quantity:
            # Decrease quantity
            order_item.quantity = F('quantity') - decrease_amount
            order_item.save()
            order_item.refresh_from_db()  # Refresh to get the updated quantity

            if order_item.quantity == 0:
                # Remove item if quantity becomes zero
                order_item.delete()
                messages.success(request, f'Removed {order_item.menu_item.name} from the order.')
            else:
                messages.success(request, f'Decreased quantity of {order_item.menu_item.name} by {decrease_amount}.')
        else:
            messages.error(request, 'Invalid decrease amount.')

        # Check if order is now empty
        if order.items.count() == 0:
            order.delete()
            messages.info(request, 'Order was empty and has been deleted.')
            return redirect('table_detail', table_id=order.table.id)

        return redirect('order_detail', order_id=order.id)

    return render(request, 'core/delete_order_item.html', {'order_item': order_item})

@user_passes_test(is_waiter_or_admin)
@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, table__floor__restaurant__owner=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('order_detail', order_id=order.id)

@user_passes_test(is_waiter_or_admin)
@login_required
def payment_view(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    orders = table.orders.filter(status='active')
    
    if request.method == 'POST':
        discount = Decimal(request.POST.get('discount', '0'))
        cash_amount = Decimal(request.POST.get('cash_amount', '0'))
        credit_card_amount = Decimal(request.POST.get('credit_card_amount', '0'))
        
        with transaction.atomic():
            # İndirim uygula
            if discount > 0:
                discount_per_order = discount / len(orders)
                for order in orders:
                    order.discount += discount_per_order
                    order.save()

            # Ödemeleri işle
            for order in orders:
                order_remaining = order.get_remaining_amount()
                
                if cash_amount > 0:
                    payment_amount = min(cash_amount, order_remaining)
                    Payment.objects.create(order=order, amount=payment_amount, payment_type='cash')
                    cash_amount -= payment_amount
                    order_remaining -= payment_amount

                if credit_card_amount > 0 and order_remaining > 0:
                    payment_amount = min(credit_card_amount, order_remaining)
                    Payment.objects.create(order=order, amount=payment_amount, payment_type='credit_card')
                    credit_card_amount -= payment_amount
                    order_remaining -= payment_amount

                if order_remaining <= 0:
                    order.status = 'completed'
                    order.save()

            if all(order.status == 'completed' for order in orders):
                table.status = 'available'
                table.save()
                messages.success(request, 'All payments completed. Table is now available.')
            else:
                messages.success(request, 'Partial payment processed successfully.')

        return redirect('table_detail', table_id=table.id)

    total_amount = sum(order.get_total() for order in orders)
    total_paid = sum(order.get_total_paid() for order in orders)
    remaining_amount = sum(order.get_remaining_amount() for order in orders)

    context = {
        'table': table,
        'orders': orders,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount,
    }
    return render(request, 'core/payment.html', context)

@user_passes_test(is_waiter_or_admin)
@login_required
def income_expense_list(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    income_expenses = IncomeExpense.objects.filter(restaurant=restaurant).order_by('-date')
    return render(request, 'core/income_expense_list.html', {'restaurant': restaurant, 'income_expenses': income_expenses})

@user_passes_test(is_waiter_or_admin)
@login_required
def add_income_expense(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        form = IncomeExpenseForm(request.POST)
        if form.is_valid():
            income_expense = form.save(commit=False)
            income_expense.restaurant = restaurant
            income_expense.created_by = request.user
            income_expense.save()
            messages.success(request, 'Income/Expense added successfully.')
            return redirect('income_expense_list', restaurant_id=restaurant.id)
    else:
        form = IncomeExpenseForm()
    return render(request, 'core/add_income_expense.html', {'form': form, 'restaurant': restaurant})

@user_passes_test(is_waiter_or_admin)
@login_required
@require_POST
def add_income_expense_category(request):
    data = json.loads(request.body)
    name = data.get('name')
    is_income = data.get('is_income')

    if not name:
        return JsonResponse({'success': False, 'error': 'Category name is required.'})

    category = IncomeExpenseCategory.objects.create(name=name, is_income=is_income)
    return JsonResponse({
        'success': True,
        'category': {
            'id': category.id,
            'name': category.name
        }
    })

@user_passes_test(is_waiter_or_admin)
@login_required
def cancel_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    
    if request.method == 'POST':
        cancel_quantity = int(request.POST.get('cancel_quantity', 0))
        cancellation_reason = request.POST.get('cancellation_reason', '')
        
        if cancel_quantity <= 0 or cancel_quantity > order_item.quantity - order_item.cancelled_quantity:
            messages.error(request, 'Invalid cancellation quantity.')
            return redirect('order_detail', order_id=order_item.order.id)
        
        order_item.cancelled_quantity += cancel_quantity
        order_item.cancellation_reason = cancellation_reason
        order_item.save()
        
        if order_item.cancelled_quantity == order_item.quantity:
            order_item.is_cancelled = True
            order_item.save()
        
        messages.success(request, f'{cancel_quantity} x {order_item.menu_item.name} has been cancelled.')
        return redirect('order_detail', order_id=order_item.order.id)
    
    return render(request, 'core/cancel_order_item.html', {'order_item': order_item})

@user_passes_test(is_waiter_or_admin)
@login_required
def manage_stock(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = MenuItem.objects.filter(category__restaurant=restaurant)

    if request.method == 'POST':
        for item in menu_items:
            quantity = request.POST.get(f'quantity_{item.id}')
            warning_threshold = request.POST.get(f'warning_threshold_{item.id}')
            track_stock = request.POST.get(f'track_stock_{item.id}') == 'on'

            if quantity is not None and warning_threshold is not None:
                stock, created = Stock.objects.get_or_create(restaurant=restaurant, menu_item=item)
                stock.quantity = int(quantity)
                stock.warning_threshold = int(warning_threshold)
                stock.save()

            item.track_stock = track_stock
            item.save()

        messages.success(request, 'Stock information updated successfully.')
        return redirect('manage_stock', restaurant_id=restaurant_id)

    for item in menu_items:
        stock = Stock.objects.filter(restaurant=restaurant, menu_item=item).first()
        if stock:
            item.current_stock = stock.quantity
            item.current_warning_threshold = stock.warning_threshold
        else:
            item.current_stock = 0
            item.current_warning_threshold = 5

    return render(request, 'core/manage_stock.html', {'restaurant': restaurant, 'menu_items': menu_items})

@user_passes_test(is_restaurant_admin)
@login_required
def sales_report(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)  # Son 30 günün verilerini al

    # Toplam fiyatı hesapla
    total_price_expression = ExpressionWrapper(
        Sum(F('items__quantity') * F('items__menu_item__price')) - F('discount'),
        output_field=DecimalField()
    )

    # Günlük satışlar
    daily_sales = Order.objects.filter(
        created_at__range=(start_date, end_date),
        status='completed',
        table__floor__restaurant=restaurant  # Restorana göre filtreleme
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total_sales=total_price_expression
    ).order_by('date')

    # Haftalık satışlar
    weekly_sales = Order.objects.filter(
        created_at__range=(start_date, end_date),
        status='completed',
        table__floor__restaurant=restaurant  # Restorana göre filtreleme
    ).annotate(
        week=TruncWeek('created_at')
    ).values('week').annotate(
        total_sales=total_price_expression
    ).order_by('week')

    # Aylık satışlar
    monthly_sales = Order.objects.filter(
        created_at__range=(start_date, end_date),
        status='completed',
        table__floor__restaurant=restaurant  # Restorana göre filtreleme
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_sales=total_price_expression
    ).order_by('month')

    # En yoğun saatler
    busiest_hours = Order.objects.filter(
        created_at__range=(start_date, end_date),
        status='completed',
        table__floor__restaurant=restaurant  # Restorana göre filtreleme
    ).annotate(
        hour=TruncHour('created_at')
    ).values('hour').annotate(
        order_count=Count('id')
    ).order_by('-order_count')[:5]  # En yoğun 5 saat

    # En yoğun günler
    busiest_days = Order.objects.filter(
        created_at__range=(start_date, end_date),
        status='completed',
        table__floor__restaurant=restaurant  # Restorana göre filtreleme
    ).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        order_count=Count('id')
    ).order_by('-order_count')[:5]  # En yoğun 5 gün

    context = {
        'restaurant': restaurant,
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'busiest_hours': busiest_hours,
        'busiest_days': busiest_days,
    }

    return render(request, 'core/sales_report.html', context)

@login_required
@user_passes_test(is_restaurant_admin)
def add_salary(request):
    try:
        staff = request.user.staff
        restaurant = staff.restaurant
    except Staff.DoesNotExist:
        return redirect('restaurant_list')  # veya uygun bir hata sayfasına yönlendirin

    if request.method == 'POST':
        form = SalaryForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            salary = form.save(commit=False)
            salary.restaurant = restaurant
            salary.type = 'expense'
            salary.created_by = request.user
            category, _ = IncomeExpenseCategory.objects.get_or_create(name="Staff Salary", is_income=False)
            salary.category = category
            salary.save()
            messages.success(request, "Salary information added successfully.")
            return redirect('add_salary')  # veya uygun bir sayfaya yönlendirin
    else:
        form = SalaryForm(restaurant=restaurant)

    return render(request, 'core/add_salary.html', {'form': form})
