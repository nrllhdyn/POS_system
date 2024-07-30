from django import forms
from .models import Floor, Table

class FloorForm(forms.ModelForm):
  class Meta:
      model = Floor
      fields = ['name']

class TableForm(forms.ModelForm):
  class Meta:
      model = Table
      fields = ['number', 'capacity']