from django import forms    

class CreateNewRoute(forms.Form):
    start = forms.CharField(label="Start", max_length=200)
    end = forms.CharField(label="End", max_length=200)

