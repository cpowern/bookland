from django.shortcuts import render, redirect, get_object_or_404
from joblib import load
import pandas as pd, numpy as np
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import Rating, Book, UserProfile
from .forms  import RatingForm, BookForm

# --------------------------------------------------------------
# ML-Teil
pivot, similarity = load("ml/book_model.joblib")
books_csv = pd.read_csv(
    "ml/raw_data/Books.csv",
    encoding="latin-1", sep=",",
    on_bad_lines="skip", low_memory=False,
)

def get_recommendations_for_user(user_index, num_users=5, num_books=5):
    similar = np.argsort(similarity[user_index])[::-1][1:num_users + 1]
    mean    = pivot.iloc[similar].mean().sort_values(ascending=False)
    top     = mean.head(num_books).index.tolist()
    return Book.objects.filter(isbn__in=top)
# --------------------------------------------------------------

# ------------------------- Standard-Views ----------------------
def home_view(request):
    if request.user.is_authenticated:
        return redirect("main")
    return render(request, "books/home.html")


@login_required
def main_view(request):
    # Zähle Bewertungen pro ISBN
    rating_counts = Rating.objects.values("isbn").annotate(count=Count("isbn")).order_by("-count")[:5]

    books_list = []
    for entry in rating_counts:
        try:
            b = Book.objects.get(isbn=entry["isbn"])
            books_list.append({
                "isbn": b.isbn,
                "title": b.title,
                "author": b.author,
                "count": entry["count"],
            })
        except Book.DoesNotExist:
            continue  # falls Buch fehlt → überspringen

    return render(request, "books/main.html", {"books": books_list})


# ----------------------------- CRUD ----------------------------
@login_required
def add_book_view(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            return redirect("main")
    else:
        form = BookForm()
    return render(request, "books/book_form.html", {"form": form, "mode": "add"})


@login_required
def edit_book_view(request, isbn):
    book = get_object_or_404(Book, isbn=isbn)
    if book.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Du darfst dieses Buch nicht bearbeiten.")
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect("main")
    else:
        form = BookForm(instance=book)
    return render(
        request,
        "books/book_form.html",
        {"form": form, "mode": "edit", "book": book},
    )

@login_required
def delete_book_view(request, isbn):
    book = get_object_or_404(Book, isbn=isbn)
    if book.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Du darfst dieses Buch nicht löschen.")
    if request.method == "POST":
        book.delete()
        Rating.objects.filter(isbn=isbn).delete()
        return redirect("main")
    return render(
        request,
        "books/book_form.html",
        {"form": None, "mode": "delete", "book": book},
    )
@login_required
def rate_book_view(request, isbn):
    # falls Buch noch nicht in DB: aus CSV übernehmen – sonst Leereintrag
    defaults = {}
    row = books_csv[books_csv["ISBN"] == isbn]
    if not row.empty:
        defaults = {
            "title":   row.iloc[0]["Book-Title"],
            "author":  row.iloc[0]["Book-Author"],
        }

        book, _ = Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                "title": row["Book-Title"].values[0] if not row.empty else isbn,
                "author": row["Book-Author"].values[0] if not row.empty else "Unbekannt",
                "created_by": request.user
            }
        )


    rating, _ = Rating.objects.get_or_create(user=request.user, isbn=isbn)

    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            return redirect("recommendations")
    else:
        form = RatingForm(instance=rating)

    return render(request, "rating/rate_book.html", {"book": book, "form": form})


@login_required
def profile_view(request):
    qs = Rating.objects.filter(user=request.user)
    ratings = []
    for r in qs:
        try:
            b = Book.objects.get(isbn=r.isbn)
            title, author = b.title, b.author
        except Book.DoesNotExist:
            title, author = r.isbn, "Unbekannt"
        ratings.append({"title": title, "author": author, "score": r.score})

    return render(
        request,
        "books/profile.html",
        {"user": request.user, "ratings": ratings, "total_ratings": qs.count()},
    )


@login_required
def recommendations_view(request):
    # Einfach eigene Bewertungen holen
    qs = Rating.objects.filter(user=request.user).order_by("-score")[:5]
    books = []
    for r in qs:
        try:
            b = Book.objects.get(isbn=r.isbn)
            books.append(b)
        except Book.DoesNotExist:
            pass
    return render(request, "books/recommendations.html", {"books": books})


def search_books_view(request):
    q = request.GET.get("query", "")
    found_books = []

    if q:
        # Lokale DB-Suche
        found_books_db = Book.objects.filter(title__icontains=q)
        for b in found_books_db:
            found_books.append({
                "title": b.title,
                "author": b.author,
                "isbn": b.isbn,
                "count": Rating.objects.filter(isbn=b.isbn).count()
            })

        # CSV-Suche (ergänze nur Bücher, die noch nicht lokal vorhanden sind)
        found_csv = books_csv[books_csv["Book-Title"].str.contains(q, case=False, na=False)]
        for _, row in found_csv.iterrows():
            if not Book.objects.filter(isbn=row["ISBN"]).exists():
                found_books.append({
                    "title": row["Book-Title"],
                    "author": row["Book-Author"],
                    "isbn": row["ISBN"],
                    "count": Rating.objects.filter(isbn=row["ISBN"]).count()
                })

    html = render_to_string("books/partials/book_list.html", {"books": found_books})
    return HttpResponse(html)
