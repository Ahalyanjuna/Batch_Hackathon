import pickle

# Load once when service starts
#with open("model.pkl", "rb") as f:
model = 2

def classify_category(subject: str, description: str) -> str:
    text = f"{subject} {description}"
    prediction = model.predict([text])  # real model prediction
    return prediction[0]