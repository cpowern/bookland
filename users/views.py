# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm                        # eigenes Formular
from books.models import Rating
from books.views import books                          # DataFrame aus CSV

# ---------- Registrierung ----------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

