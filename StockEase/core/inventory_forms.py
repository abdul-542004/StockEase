from django import forms
from .models import Inventory

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'warehouse', 'minimumStockLevel', 'maximumStockLevel']
        widgets = {
            'product': forms.Select(attrs={'class': 'input input-bordered w-full'}),
            'warehouse': forms.Select(attrs={'class': 'input input-bordered w-full'}),
            'minimumStockLevel': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'maximumStockLevel': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
        }
