import pickle
import pandas as pd
from scipy.sparse import hstack
from sklearn.preprocessing import LabelEncoder
import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def classify_category(subject, content):
    
    # Create dataframe (same format as training)
    new_data = pd.DataFrame({
        "subject": [subject],
        "content": [content]
    })
    
    # Apply cleaning
    new_data['clean_subject'] = new_data['subject'].apply(clean_text)
    new_data['description'] = new_data['content'].apply(clean_text)

    #Load the saved model
    with open("best_model.pkl", "rb") as f:
        model = pickle.load(f)

    #Load the vectorizers
    with open("subject_vectorizer.pkl", "rb") as f:
        sub_vectorizer = pickle.load(f)

    with open("content_vectorizer.pkl", "rb") as f:
        des_vectorizer = pickle.load(f)

    #Load the label encoder 
    with open("label_encoder.pkl", "rb") as f: 
        le = pickle.load(f)
    
    #Transform using saved vectorizers
    X_subject = sub_vectorizer.transform(new_data['clean_subject'])
    X_content = des_vectorizer.transform(new_data['description'])
    
    #Combine features
    X_new_vec = hstack([X_subject, X_content])
    
    #Predict
    pred_numeric = model.predict(X_new_vec)
    
    #Convert numeric label back to original class
    pred_class = le.inverse_transform(pred_numeric)
    
    return pred_class[0]