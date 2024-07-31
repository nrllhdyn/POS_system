from django import forms
from .models import Floor, IncomeExpense, Table

class FloorForm(forms.ModelForm):
  class Meta:
      model = Floor
      fields = ['name']

class TableForm(forms.ModelForm):
  class Meta:
      model = Table
      fields = ['number', 'capacity']


class IncomeExpenseForm(forms.ModelForm):
    class Meta:
        model = IncomeExpense
        fields = ['type','category',  'amount', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
