from django.shortcuts import render, redirect, get_object_or_404
from joblib import load
import pandas as pd, numpy as np
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string
import joblib

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
    row = books_csv[books_csv["ISBN"] == isbn]
    if not row.empty:
        book, _ = Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                "title": row["Book-Title"].values[0],
                "author": row["Book-Author"].values[0],
                "created_by": request.user
            }
        )
    else:
        # Fallback, falls Buch nicht gefunden wird
        book, _ = Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                "title": isbn,
                "author": "Unbekannt",
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
    q = request.GET.get("query", "").strip()
    found_books = []

    if q:
        # Bücher aus lokaler DB
        found_books = list(Book.objects.filter(title__icontains=q))

        # Bücher aus CSV, die noch nicht in der DB sind
        found_csv = books_csv[books_csv["Book-Title"].str.contains(q, case=False, na=False)]
        new_books = []

        for _, row in found_csv.iterrows():
            isbn = row["ISBN"]
            if not Book.objects.filter(isbn=isbn).exists():
                new_books.append(Book(
                    isbn=isbn,
                    title=row["Book-Title"],
                    author=row["Book-Author"],
                    created_by=None
                ))

        if new_books:
            Book.objects.bulk_create(new_books)

        # Jetzt erneut alle Bücher (neu + alte) holen
        found_books += list(Book.objects.filter(isbn__in=[b.isbn for b in new_books]))

    html = render_to_string("books/partials/book_list.html", {"books": found_books, "request": request})
    return HttpResponse(html)

# ------------------------- Machine Learning ----------------------
# Modell und Daten laden (einmalig)
pivot, similarity = joblib.load('ml/book_model.joblib')
books_df = pd.read_csv("ml/raw_data/Books.csv", encoding="latin-1", on_bad_lines='skip', low_memory=False)

def get_similar_users(user_id, top_n=5):
    if user_id not in pivot.index:
        return []
    user_idx = pivot.index.get_loc(user_id)
    sim_scores = similarity[user_idx]
    similar_indices = np.argsort(sim_scores)[::-1][1:top_n+1]
    similar_users = pivot.index[similar_indices]
    return similar_users

def recommend_books(user_id, top_n=5):
    similar_users = get_similar_users(user_id)
    if not len(similar_users):
        return []

    similar_users_ratings = pivot.loc[similar_users]
    user_rated_books = pivot.loc[user_id]

    candidate_books = similar_users_ratings.loc[:, user_rated_books == 0]
    positive_counts = (candidate_books >= 1).sum(axis=0)

    if positive_counts.empty:
        return []

    recommended_books = positive_counts.sort_values(ascending=False).head(top_n)
    return recommended_books.index.tolist()

def recommendations_view(request):
    books = []
    hardcoded_ml_user_id = 254  # 🔥 HIER festlegen
    print("DEBUG: Hardcoded ML-User-ID:", hardcoded_ml_user_id)
    print("DEBUG: All Pivot IDs (first 10):", list(pivot.index)[:10])
    print("DEBUG: Is in pivot?:", hardcoded_ml_user_id in pivot.index)

    if hardcoded_ml_user_id in pivot.index:
        recommended_isbns = recommend_books(hardcoded_ml_user_id)
        # 🛑 DEBUG 2: Check what recommend_books returns
        print("DEBUG: Recommended ISBNs:", recommended_isbns)
        for isbn in recommended_isbns:
            match = books_df[books_df['ISBN'] == isbn]
            if not match.empty:
                row = match.iloc[0]
                books.append({
                    'isbn': isbn,
                    'title': row['Book-Title'],
                    'author': row['Book-Author'],
                })
        # 🛑 DEBUG 3: Check final book list for template
        print("DEBUG: Final Books List:", books)

    return render(request, 'books/recommendations.html', {'books': books})