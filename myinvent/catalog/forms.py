from django import forms
from .models import Category, RawMaterial, Transaction

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = ['name', 'SKU', 'category', 'quantity',  'reorder_level',
                 'location']
        
    def clean_SKU(self):
        sku = self.cleaned_data.get('SKU')
        if self.instance.pk is None:  # Only for new entries
            existing_material = RawMaterial.objects.filter(SKU=sku).first()
            if existing_material:
                return sku
            # If no existing material, check that this SKU is unique
            if RawMaterial.objects.filter(SKU=sku).exists():
                raise forms.ValidationError("This SKU is already in use.")
        return sku

# class TransactionForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         fields = ['material', 'transaction_type', 'quantity', 'notes']
#         widgets = {
#             'notes': forms.Textarea(attrs={'rows': 3}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         material = cleaned_data.get('material')
#         quantity = cleaned_data.get('quantity')
#         transaction_type = cleaned_data.get('transaction_type')

#         if not all([material, quantity, transaction_type]):
#             return cleaned_data

#         if quantity <= 0:
#             raise forms.ValidationError("Quantity must be greater than 0")

#         if transaction_type == Transaction.STOCK_OUT:
#             if material.quantity < quantity:
#                 raise forms.ValidationError(
#                     f"Cannot remove {quantity} units. Only {material.quantity} units available in stock."
#                 )

#         return cleaned_data
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['material', 'transaction_type', 'quantity']

# class RawMaterialForm(forms.ModelForm):
#     class Meta:
#         model = RawMaterial
#         fields = ['name', 'SKU', 'category', 'quantity', 'reorder_level', 'location']

  
