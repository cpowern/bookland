from django.shortcuts import render, redirect
from joblib import load
import pandas as pd
import numpy as np
from django.contrib.auth.decorators import login_required
from .models import Rating, Book, UserProfile
from .forms import RatingForm

# Modell laden (Pivot-Tabelle + Ähnlichkeitsmatrix)
pivot, similarity = load('ml/book_model.joblib')

# Debug-Ausgabe: zeige gültige User-IDs aus dem Modell (z. B. für Admin-Eintrag)
print("🔍 Verfügbare kaggle_user_id Werte:", list(pivot.index[:10]))

# Bücher-Datei laden
books = pd.read_csv('ml/raw_data/Books.csv', encoding='latin-1', sep=',', on_bad_lines='skip', low_memory=False)

def get_recommendations_for_user(user_index, num_users=5, num_books=5):
    similar_users = np.argsort(similarity[user_index])[::-1][1:num_users+1]
    user_ratings = pivot.iloc[similar_users]
    mean_ratings = user_ratings.mean().sort_values(ascending=False)
    top_isbns = mean_ratings.head(num_books).index.tolist()

    recommended_books = books[books['ISBN'].isin(top_isbns)][['ISBN', 'Book-Title', 'Book-Author']].drop_duplicates()

    books_list = recommended_books.rename(columns={
        'Book-Title': 'title',
        'Book-Author': 'author',
        'ISBN': 'isbn'
    }).to_dict(orient='records')

    return books_list

@login_required
def recommendations_view(request):
    try:
        kaggle_id = request.user.userprofile.kaggle_user_id
        user_index = list(pivot.index).index(kaggle_id)
        recommended_books = get_recommendations_for_user(user_index)
    except (UserProfile.DoesNotExist, ValueError):
        recommended_books = []
    
    return render(request, 'books/recommendations.html', {'books': recommended_books})

@login_required
def profile_view(request):
    user = request.user
    ratings_qs = Rating.objects.filter(user=user)
    ratings = []

    for r in ratings_qs:
        row = books[books['ISBN'] == r.isbn]
        if not row.empty:
            title = row.iloc[0]["Book-Title"]
            author = row.iloc[0]["Book-Author"]
        else:
            title = r.isbn
            author = "Unbekannt"
        ratings.append({
            "title": title,
            "author": author,
            "score": r.score
        })

    return render(request, "books/profile.html", {
        "user": user,
        "ratings": ratings,
        "total_ratings": ratings_qs.count()
    })

@login_required
def rate_book_view(request, isbn):
    book_row = books[books['ISBN'] == isbn].iloc[0]
    book = {
        "title": book_row['Book-Title'],
        "author": book_row['Book-Author'],
        "isbn": isbn
    }

    rating, _ = Rating.objects.get_or_create(user=request.user, isbn=isbn)

    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            return redirect("recommendations")
    else:
        form = RatingForm(instance=rating)

    return render(request, "rating/rate_book.html", {
        "book": book,
        "form": form,
    })
