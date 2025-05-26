import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib

def train_and_save_model():
    print("🚀 Starte Modelltraining...")
    df = pd.read_csv("ml/raw_data/Ratings.csv", encoding="latin-1", on_bad_lines='skip')
    df = df[df['Book-Rating'] > 0]

    user_counts = df['User-ID'].value_counts()
    active_users = user_counts[user_counts > 10].index
    df = df[df['User-ID'].isin(active_users)]

    book_counts = df['ISBN'].value_counts()
    popular_books = book_counts[book_counts > 10].index
    df = df[df['ISBN'].isin(popular_books)]

    # Nur Bewertungen ≥ 4 berücksichtigen
    df['Positive-Rating'] = df['Book-Rating'].apply(lambda x: 1 if x >= 4 else 0)

    pivot = df.pivot_table(index='User-ID', columns='ISBN', values='Positive-Rating').fillna(0)
    similarity = cosine_similarity(pivot)

    joblib.dump((pivot, similarity), 'book_model.joblib')
    print("✅ Modell erfolgreich gespeichert als 'book_model.joblib'.")

if __name__ == "__main__":
    train_and_save_model()
