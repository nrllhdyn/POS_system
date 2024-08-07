from django import forms
from .models import Floor, IncomeExpense, OrderItem, Table , Staff
from django.contrib.auth.models import User

class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.restaurant:
            if Floor.objects.filter(restaurant=self.restaurant, name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A floor with this name already exists in this restaurant.")
        return name


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

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'notes']
    
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Özel notlar...'}))

class StaffEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = Staff
        fields = ['role', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        staff = super().save(commit=False)
        staff.user.first_name = self.cleaned_data['first_name']
        staff.user.last_name = self.cleaned_data['last_name']
        staff.user.email = self.cleaned_data['email']
        if commit:
            staff.user.save()
            staff.save()
        return staff


class SalaryForm(forms.ModelForm):
    staff = forms.ModelChoiceField(queryset=Staff.objects.none(), label='Employee',widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = IncomeExpense
        fields = [ 'amount', 'description', 'date', 'staff']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        if restaurant:
            self.fields['staff'].queryset = Staff.objects.filter(restaurant=restaurant)
