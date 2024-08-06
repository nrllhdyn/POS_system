# tasks.py
from datetime import timezone
from celery import shared_task
from .models import IncomeExpense, Employee, IncomeExpenseCategory

@shared_task
def add_monthly_salaries(restaurant_id):
  employees = Employee.objects.filter(restaurant_id=restaurant_id)
  for employee in employees:
      IncomeExpense.objects.create(
          restaurant_id=restaurant_id,
          category=IncomeExpenseCategory.objects.get(name='Salary'),  # Maaş kategorisi
          type='expense',
          amount=employee.salary,  # Personelin maaşı
          description=f'Salary for {employee.name}',
          date=timezone.now().date()  # Bugünün tarihi
      )