from django import forms
from .models import Rating, Book

class RatingForm(forms.ModelForm):
    class Meta:
        model  = Rating
        fields = ["score"]
        labels = {"score": "Deine Bewertung (1–5)"}

class BookForm(forms.ModelForm):
    class Meta:
        model  = Book
        fields = ["isbn", "title", "author"]
        labels = {
            "isbn":   "ISBN",
            "title":  "Titel",
            "author": "Autor",
        }
