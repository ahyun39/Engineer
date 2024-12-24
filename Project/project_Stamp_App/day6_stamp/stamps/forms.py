from django import forms
from .models import Stamp

class StampForm(forms.ModelForm):
    class Meta:
        model = Stamp
        fields = ['concert_name', 'artist_name', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
