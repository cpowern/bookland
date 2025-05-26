import joblib
import numpy as np

def get_similar_users(pivot, similarity, user_id, top_n=5):
    if user_id not in pivot.index:
        print("❌ Nutzer-ID nicht gefunden.")
        return []
    
    user_idx = pivot.index.get_loc(user_id)
    sim_scores = similarity[user_idx]
    similar_indices = np.argsort(sim_scores)[::-1][1:top_n+1]
    similar_users = pivot.index[similar_indices]
    
    return similar_users

def recommend_books(pivot, similarity, user_id, top_n=5):
    similar_users = get_similar_users(pivot, similarity, user_id)
    if not len(similar_users):
        return []
    
    similar_users_ratings = pivot.loc[similar_users]
    mean_ratings = similar_users_ratings.mean(axis=0)
    user_rated_books = pivot.loc[user_id]
    unrated_books = mean_ratings[user_rated_books == 0]
    recommended_books = unrated_books.sort_values(ascending=False).head(top_n)
    
    return recommended_books.index.tolist()

if __name__ == "__main__":
    pivot, similarity = joblib.load('book_model.joblib')
    user_id = int(input("🔍 Nutzer-ID eingeben: "))
    recommendations = recommend_books(pivot, similarity, user_id)
    print(f"📚 Empfehlungen für User {user_id}: {recommendations}")
