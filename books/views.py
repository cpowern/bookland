from django.shortcuts import render
from joblib import load
import pandas as pd
import numpy as np
from django.contrib.auth.decorators import login_required
from .models import Rating, Book


# Modell laden (Pivot-Tabelle + Ähnlichkeitsmatrix)
pivot, similarity = load('ml/book_model.joblib')

# Bücher-Datei laden
books = pd.read_csv('ml/raw_data/Books.csv', encoding='latin-1', sep=',', on_bad_lines='skip', low_memory=False)

def get_recommendations_for_user(user_index, num_users=5, num_books=5):
    similar_users = np.argsort(similarity[user_index])[::-1][1:num_users+1]
    user_ratings = pivot.iloc[similar_users]
    mean_ratings = user_ratings.mean().sort_values(ascending=False)
    top_isbns = mean_ratings.head(num_books).index.tolist()

    # Buchdaten filtern
    recommended_books = books[books['ISBN'].isin(top_isbns)][['ISBN', 'Book-Title', 'Book-Author']].drop_duplicates()

    # Für Template: Spaltennamen anpassen
    books_list = recommended_books.rename(columns={
        'Book-Title': 'title',
        'Book-Author': 'author',
        'ISBN': 'isbn'
    }).to_dict(orient='records')

    return books_list

@login_required
def recommendations_view(request):
    # Fester Index (z. B. Nutzer-ID 0 im Pivot) zum Testen
    user_index = 0

    recommended_books = get_recommendations_for_user(user_index)

    return render(request, 'books/recommendations.html', {
        'books': recommended_books,
    })

@login_required
def profile_view(request):
    user = request.user
    ratings = Rating.objects.filter(user=user)
    total_ratings = ratings.count()
    
    return render(request, "books/profile.html", {
        "user": user,
        "ratings": ratings,
        "total_ratings": total_ratings
    })

