import joblib
import numpy as np
import pandas as pd

def get_similar_users(pivot, similarity, user_id, top_n=5):
    if user_id not in pivot.index:
        print(f"❌ Nutzer-ID {user_id} nicht gefunden.")
        return []
    user_idx = pivot.index.get_loc(user_id)
    sim_scores = similarity[user_idx]
    similar_indices = np.argsort(sim_scores)[::-1][1:top_n+1]
    similar_users = pivot.index[similar_indices]
    return similar_users

def recommend_books(user_id, top_n=5):
    similar_users = get_similar_users(pivot, similarity, user_id)
    if not len(similar_users):
        return []

    similar_users_ratings = pivot.loc[similar_users]
    user_rated_books = pivot.loc[user_id]

    # Nur Bücher, die ähnliche Nutzer ≥1 (d. h. ≥4 Sterne) bewertet haben
    candidate_books = similar_users_ratings.loc[:, user_rated_books == 0]

    # Zählen, wie viele ähnliche User positiv bewertet haben
    positive_counts = (candidate_books >= 1).sum(axis=0)

    if positive_counts.empty:
        return []

    # Top-N Bücher mit den meisten positiven Stimmen
    recommended_books = positive_counts.sort_values(ascending=False).head(top_n)
    return recommended_books.index.tolist()

def map_isbn_to_titles(isbn_list, books_df):
    titles = []
    for isbn in isbn_list:
        match = books_df[books_df['ISBN'] == isbn]
        if not match.empty:
            titles.append(match.iloc[0]['Book-Title'])
        else:
            titles.append(f"(Titel nicht gefunden für ISBN {isbn})")
    return titles

if __name__ == "__main__":
    # Lade Modell
    pivot, similarity = joblib.load('book_model.joblib')

    # Lade Buchdaten
    books_df = pd.read_csv("ml/raw_data/Books.csv", encoding="latin-1", on_bad_lines='skip', low_memory=False)

    # Nutzer-ID eingeben
    user_id = int(input("🔍 Nutzer-ID eingeben: "))
    recommendations = recommend_books(user_id)

    if recommendations:
        titles = map_isbn_to_titles(recommendations, books_df)
        print(f"\n📚 Empfehlungen für User {user_id}:\n")
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
    else:
        print(f"❌ Keine Empfehlungen gefunden für User {user_id}.")