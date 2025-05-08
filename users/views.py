from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm

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
