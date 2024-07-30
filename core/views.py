from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Floor, Restaurant, Category, MenuItem, Order , OrderItem, Table
from django.contrib.auth.decorators import login_required
from .forms import FloorForm, TableForm
# Create your views here.
def home(request):
    contex = {
        'page_title':'Home',
        'welcome_message':'Welcome to Restaurant POS System',
    }
    return render(request,'core/home.html',contex)

@login_required
def restaurant_list(request):
    restaurants = Restaurant.objects.filter(owner=request.user)
    return render(request, 'core/restaurant_list.html', {'restaurants': restaurants})

@login_required
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    floors = restaurant.floors.all()
    return render(request, 'core/restaurant_detail.html', {'restaurant': restaurant,'floors':floors})

@login_required
def add_floor(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == 'POST':
        form = FloorForm(request.POST)
        if form.is_valid():
            floor = form.save(commit=False)
            floor.restaurant = restaurant
            floor.save()
            messages.success(request, 'Floor added successfully.')
            return redirect('restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = FloorForm()
    return render(request, 'core/add_floor.html', {'form': form, 'restaurant': restaurant})

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

@login_required
def edit_floor(request, floor_id):
    floor = get_object_or_404(Floor, id=floor_id, restaurant__owner=request.user)
    if request.method == 'POST':
        form = FloorForm(request.POST, instance=floor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Floor updated successfully.')
            return redirect('restaurant_detail', restaurant_id=floor.restaurant.id)
    else:
        form = FloorForm(instance=floor)
    return render(request, 'core/edit_floor.html', {'form': form, 'floor': floor})

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

@login_required
def delete_floor(request, floor_id):
    floor = get_object_or_404(Floor, id=floor_id, restaurant__owner=request.user)
    if request.method == 'POST':
        restaurant_id = floor.restaurant.id
        floor.delete()
        messages.success(request, 'Floor deleted successfully.')
        return redirect('restaurant_detail', restaurant_id=restaurant_id)
    return render(request, 'core/delete_floor.html', {'floor': floor})

@login_required
def delete_table(request, table_id):
    table = get_object_or_404(Table, id=table_id, floor__restaurant__owner=request.user)
    if request.method == 'POST':
        restaurant_id = table.floor.restaurant.id
        table.delete()
        messages.success(request, 'Table deleted successfully.')
        return redirect('restaurant_detail', restaurant_id=restaurant_id)
    return render(request, 'core/delete_table.html', {'table': table})

@login_required
def menu_management(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    categories = restaurant.categories.all()
    return render(request, 'core/menu_management.html', {'restaurant': restaurant, 'categories': categories})

@login_required
def add_category(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        Category.objects.create(restaurant=restaurant, name=name)
        messages.success(request, 'Category added successfully.')
        return redirect('menu_management', restaurant_id=restaurant.id)
    return render(request, 'core/add_category.html', {'restaurant': restaurant})

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

@login_required
def floor_list(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    floors = restaurant.floors.all()
    return render(request, 'core/floor_list.html', {'restaurant': restaurant, 'floors': floors})

@login_required
def table_list(request, floor_id):
    floor = get_object_or_404(Floor, id=floor_id, restaurant__owner=request.user)
    tables = floor.tables.all()
    return render(request, 'core/table_list.html', {'floor': floor, 'tables': tables})

@login_required
def create_order(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    
    if request.method == 'POST':
        menu_item_ids = request.POST.getlist('menu_item_ids')
        
        if menu_item_ids:
            order = Order.objects.create(table=table, status='pending')
            
            for item_id in menu_item_ids:
                quantity = int(request.POST.get(f'quantities_{item_id}', 1))
                menu_item = MenuItem.objects.get(id=item_id)
                OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
            
            table.status = 'occupied'
            table.save()
            
            messages.success(request, 'Order created successfully.')
            return redirect('table_detail', table_id=table.id)
    
    return render(request, 'core/create_order.html', {'table': table})

@login_required
def close_table(request, table_id):
  table = get_object_or_404(Table, id=table_id)
  restaurant_id = table.floor.restaurant.id  # Masanın bağlı olduğu restoranın ID'sini al
  
  if request.method == 'POST':
      # Masayı kapat
      table.status = 'available'
      table.save()
      
      # Aktif siparişleri tamamla
      active_orders = table.orders.exclude(status__in=['paid', 'completed'])
      for order in active_orders:
          order.status = 'completed'
          order.save()
  
  return redirect('floor_list', restaurant_id=restaurant_id)

@login_required
def table_detail(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    active_orders = table.orders.exclude(status__in=['paid', 'completed']).order_by('-created_at')
    return render(request, 'core/table_detail.html', {'table': table, 'active_orders': active_orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, table__floor__restaurant__owner=request.user)
    return render(request, 'core/order_detail.html', {'order': order})

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