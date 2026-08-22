import pickle

# Load model & vectorizer
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

def predict(text):
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]

# Test
print(predict("ನೀರು ಸಮಸ್ಯೆ ಇದೆ"))