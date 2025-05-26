import pandas as pd

df = pd.read_csv('ml/raw_data/Ratings.csv', encoding='latin-1', on_bad_lines='skip')

print("📊 Spaltenübersicht:")
print(df.columns)

print("\n🔍 Beispiel-Daten:")
print(df.head(10))
