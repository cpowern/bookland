import joblib
import numpy as np

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

    # Nur Bücher, die ähnliche Nutzer ≥4 bewertet haben
    candidate_books = similar_users_ratings.loc[:, user_rated_books == 0]

    # Summiere, wie viele ähnliche User das Buch ≥4 bewertet haben
    positive_counts = (candidate_books >= 1).sum(axis=0)

    if positive_counts.empty:
        return []

    # Top-N Bücher mit den meisten positiven Stimmen
    recommended_books = positive_counts.sort_values(ascending=False).head(top_n)
    return recommended_books.index.tolist()


if __name__ == "__main__":
    pivot, similarity = joblib.load('book_model.joblib')
    user_id = int(input("🔍 Nutzer-ID eingeben: "))
    recommendations = recommend_books(user_id)
    if recommendations:
        print(f"📚 Empfehlungen für User {user_id}: {recommendations}")
    else:
        print(f"❌ Keine Empfehlungen gefunden für User {user_id}.")