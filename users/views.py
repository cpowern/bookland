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


# ---------- Login / Logout ----------
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user:
            login(request, user)
            return redirect("recommendations")
    return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------- Profil ----------
@login_required
def profile_view(request):
    """Zeigt alle eigenen Bewertungen + Buchinfos."""
    qs = Rating.objects.filter(user=request.user)

    ratings = []
    for r in qs:
        row = books[books["ISBN"] == r.isbn]
        if not row.empty:
            title = row.iloc[0]["Book-Title"]
            author = row.iloc[0]["Book-Author"]
        else:
            title, author = r.isbn, "–"
        ratings.append({"title": title, "author": author, "score": r.score})

    return render(
        request,
        "users/profile.html",               # Template-Pfad
        {"ratings": ratings, "total_ratings": qs.count()},
    )
