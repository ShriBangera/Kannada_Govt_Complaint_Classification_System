import pandas as pd
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

# Load dataset
data = pd.read_csv("data.csv", encoding="utf-8")

# Clean dataset (same as training)
data = data.drop_duplicates()
data = data[data['text'] != 'text']

# Features and labels
X = data['text']
y = data['category']

# Split data (same random_state used for reproducibility)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Load saved model and vectorizer
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Convert test text to vectors
X_test_vec = vectorizer.transform(X_test)

# Predict
y_pred = model.predict(X_test_vec)

# Generate confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display and save
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=model.classes_
)

fig, ax = plt.subplots(figsize=(8, 6))
disp.plot(ax=ax, xticks_rotation=45, cmap="Blues")
plt.title("Confusion Matrix")
plt.tight_layout()

# Save image
plt.savefig("confusion_matrix.png")

# Show on screen
plt.show()

print("✅ Confusion matrix saved as confusion_matrix.png")