from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from books.models import Rating          # ← für Profil‑Statistik



def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        uname = request.POST["username"]
        pw = request.POST["password"]
        user = authenticate(request, username=uname, password=pw)
        if user:
            login(request, user)
            return redirect("recommendations")
    return render(request, "users/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# Registrierung
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("recommendations")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

# (Login/Logout nimmst du aus django.contrib.auth.urls)

# Profil‑Seite
@login_required
def profile_view(request):
    ratings = Rating.objects.filter(user=request.user).select_related("book")
    total   = ratings.count()
    return render(
        request,
        "profile.html",
        {"ratings": ratings, "total_ratings": total}
    )