from django import forms
from .models import Medicine, Sale, Shop

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'stock', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_superuser:
            self.fields['shop'] = forms.ModelChoiceField(queryset=Shop.objects.all())

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['medicine', 'quantity']
        
    def __init__(self, *args, **kwargs):
        shop = kwargs.pop('shop', None)
        super().__init__(*args, **kwargs)
        if shop:
            self.fields['medicine'].queryset = Medicine.objects.filter(shop=shop)
        else:
            # For superusers (shop=None), show all medicines
            self.fields['medicine'].queryset = Medicine.objects.all()
            self.fields['shop'] = forms.ModelChoiceField(queryset=Shop.objects.all())

    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get('medicine')
        quantity = cleaned_data.get('quantity')
        
        if not medicine:
            raise forms.ValidationError('Medicine is required')
            
        if not quantity:
            raise forms.ValidationError('Quantity is required')
            
        if quantity and quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than 0')
            
        if medicine and quantity and quantity > medicine.stock:
            raise forms.ValidationError(f'Insufficient stock available. Current stock: {medicine.stock}')
            
        # Calculate total_amount when we have both medicine and quantity
        if medicine and quantity:
            cleaned_data['total_amount'] = medicine.price * quantity
            
        return cleaned_data