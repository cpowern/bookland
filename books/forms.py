# books/forms.py
from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score']
        labels = {'score': 'Deine Bewertung (1–5)'}
