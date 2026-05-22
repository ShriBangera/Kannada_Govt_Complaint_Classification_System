import pandas as pd
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load dataset
data = pd.read_csv("data.csv", encoding='utf-8')

# Clean dataset
data = data.drop_duplicates()
data = data[data['text'] != 'text']

# 🔥 Remove confusing samples (strict filtering)
def clean_row(row):
    text = row['text']
    cat = row['category']

    if 'ನೀರು' in text and cat != 'water':
        return False
    if ('ವಿದ್ಯುತ್' in text or 'ಕರಂಟ್' in text) and cat != 'electricity':
        return False
    if 'ರಸ್ತೆ' in text and cat != 'road':
        return False

    return True

data = data[data.apply(clean_row, axis=1)]

print("After cleaning:", data['category'].value_counts())

# Features
X = data['text']
y = data['category']

# 🔥 Better vectorizer for Kannada
vectorizer = TfidfVectorizer(
    ngram_range=(1,2),
    analyzer='char',   # 👈 VERY IMPORTANT
)

X_vec = vectorizer.fit_transform(X)

# Model
model = LogisticRegression(max_iter=2000)
model.fit(X_vec, y)

# Save
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("✅ Model trained successfully!")