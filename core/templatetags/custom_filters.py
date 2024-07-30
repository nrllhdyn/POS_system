from django import template
from django.db.models import Sum

register = template.Library()

@register.filter
def sum_attr(queryset, attr):
  if not queryset:
      return 0
  if isinstance(queryset, (list, tuple)):
      return sum(getattr(item, attr)() if callable(getattr(item, attr)) else getattr(item, attr, 0) for item in queryset)
  try:
      return queryset.aggregate(total=Sum(attr))['total'] or 0
  except:
      return 0

@register.filter
def multiply(value, arg):
  try:
      return float(value) * float(arg)
  except (ValueError, TypeError):
      return 0

@register.filter
def get_item_total(order):
  return sum(item.quantity * item.menu_item.price for item in order.items.all())

@register.filter
def total_of_all_orders(orders):
  return sum(get_item_total(order) for order in orders)