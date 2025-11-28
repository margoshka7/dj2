from django import forms
from .models import Product
import json

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'product_type', 'description', 
            'price', 'discount', 'sku', 'is_available', 'stock_quantity', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean_sku(self):
        sku = self.cleaned_data['sku']
        if not sku.isalnum():
            raise forms.ValidationError("Артикул должен содержать только буквы и цифры")
        return sku
    
    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля")
        return price
    
    def clean_discount(self):
        discount = self.cleaned_data['discount']
        if discount < 0 or discount > 100:
            raise forms.ValidationError("Скидка должна быть от 0% до 100%")
        return discount


class JSONImportForm(forms.Form):
    json_file = forms.FileField(
        label="Выберите JSON файл",
        help_text="Поддерживаются только файлы в формате JSON",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )