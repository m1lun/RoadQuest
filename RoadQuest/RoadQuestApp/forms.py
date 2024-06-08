from django import forms
from .models import RouteItem  

class RouteForm(forms.ModelForm):
    class Meta:
        model = RouteItem
        fields = ['start', 'end']
        widgets = {
            'start': forms.TextInput(attrs={'id': 'start', 'placeholder': 'Enter starting location'}),
            'end': forms.TextInput(attrs={'id': 'end', 'placeholder': 'Enter ending location'}),
        }