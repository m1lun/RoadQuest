from django import forms
from .models import RouteItem  

class RouteForm(forms.ModelForm):
    class Meta:
        model = RouteItem
        fields = ['start', 'end', 'stop1', 'stop2', 'stop3']