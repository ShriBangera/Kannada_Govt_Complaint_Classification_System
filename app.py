
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)

# Load model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

@app.route('/')
def home():
    return "🚀 Complaint Classification API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400

        text = data['text']

        vec = vectorizer.transform([text])
        category = model.predict(vec)[0]
        confidence = model.predict_proba(vec).max()

        return jsonify({
            "input": text,
            "category": category,
            "confidence": round(float(confidence) * 100, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run app
if __name__ == '__main__':
    app.run(debug=True)
