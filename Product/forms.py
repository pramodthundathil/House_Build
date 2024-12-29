from django.forms import ModelForm,TextInput,Select
from .models import ProductDetails
from django import forms

class ProductAddForm(ModelForm):
    class Meta:
        model = ProductDetails
        fields = ["product_name","Product_category","Product_subcategory","product_description","product_price","product_stock","Product_Image"]
        
        widgets = {
            "product_name":TextInput(attrs={"class":'form-control'}),
            "Product_category":Select(attrs={"class":'form-control'}),
            "Product_subcategory":Select(attrs={"class":'form-control'}),
            "product_description":TextInput(attrs={"class":'form-control'}),
            "product_price":TextInput(attrs={"type":"number","class":'form-control'}),
            "product_stock":TextInput(attrs={"type":"number","class":'form-control'}),
            
        }


from .models import Service, ServiceBooking

# Service Form
class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'name', 'description', 'price', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in minutes'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ServiceBookingForm(forms.ModelForm):
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    appointment_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))

    class Meta:
        model = ServiceBooking
        fields = [ 'appointment_date', 'appointment_time', 'notes']
        widgets = {
            
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }