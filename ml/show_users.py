import joblib

# Modell laden
pivot, _ = joblib.load('book_model.joblib')

print("✅ Folgende Nutzer-IDs sind im Modell verfügbar (gefiltert auf aktive Nutzer):")
for user_id in pivot.index[:20]:
    print(user_id)
print(f"... insgesamt {len(pivot.index)} Nutzer.")