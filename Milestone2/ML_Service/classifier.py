import pickle
import pandas as pd
from scipy.sparse import hstack
import re
import os

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def classify_category(subject, content):
    # Get the directory where this file is located
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create dataframe (same format as training)
    new_data = pd.DataFrame({
        "subject": [subject],
        "content": [content]
    })
    
    # Apply cleaning
    new_data['clean_subject'] = new_data['subject'].apply(clean_text)
    new_data['description'] = new_data['content'].apply(clean_text)

    try:
        #Load the saved model
        model_path = os.path.join(model_dir, "best_model.pkl")
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        #Load the vectorizers
        sub_vec_path = os.path.join(model_dir, "subject_vectorizer.pkl")
        with open(sub_vec_path, "rb") as f:
            sub_vectorizer = pickle.load(f)

        des_vec_path = os.path.join(model_dir, "content_vectorizer.pkl")
        with open(des_vec_path, "rb") as f:
            des_vectorizer = pickle.load(f)

        #Load the label encoder 
        le_path = os.path.join(model_dir, "label_encoder.pkl")
        with open(le_path, "rb") as f: 
            le = pickle.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Model files not found in {model_dir}: {e}")
    
    #Transform using saved vectorizers
    X_subject = sub_vectorizer.transform(new_data['clean_subject'])
    X_content = des_vectorizer.transform(new_data['description'])
    
    #Combine features
    X_new_vec = hstack([X_subject, X_content])
    
    #Predict
    try:
        pred_numeric = model.predict(X_new_vec)
        
        #Convert numeric label back to original class
        pred_class = le.inverse_transform(pred_numeric)
        
        return pred_class[0]
    except Exception as e:
        raise ValueError(f"Prediction failed: {e}")