# phishing_app.py

import streamlit as st
import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# -------------------------------
# Feature extraction function
# -------------------------------
def extract_features(url):
    return {
        "url_length": len(url),
        "has_at": 1 if "@" in url else 0,
        "has_https": 1 if url.startswith("https") else 0,
        "num_dots": url.count("."),
        "has_hyphen": 1 if "-" in url else 0
    }

# -------------------------------
# Load dataset
# -------------------------------
@st.cache_data
def load_data():
    # Example dataset (replace with a larger CSV dataset for real use!)
    data = {
        "url": [
            "http://example.com",                # legit
            "https://secure-login.com",          # legit
            "http://phishing-site.com@evil.com", # phishing
            "http://paypal.login.verify.com",    # phishing
            "https://google.com",                # legit
            "http://192.168.0.1/login",          # phishing
            "https://microsoft.com",             # legit
            "http://update-your-bank.com"        # phishing
        ],
        "label": [0, 0, 1, 1, 0, 1, 0, 1]  # 0 = Legit, 1 = Phishing
    }
    df = pd.DataFrame(data)
    features = df["url"].apply(lambda x: pd.Series(extract_features(x)))
    df = pd.concat([df, features], axis=1)
    return df

# -------------------------------
# Train model
# -------------------------------
@st.cache_resource
def train_model(df):
    X = df[["url_length", "has_at", "has_https", "num_dots", "has_hyphen"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    model = LogisticRegression()
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    return model, acc

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🔎 Phishing Website Detection")
st.write("Enter a website URL to check if it's **Legitimate** or **Phishing**")

# Load dataset and train model
df = load_data()
model, acc = train_model(df)

st.sidebar.success(f"Model trained with accuracy: {acc*100:.2f}%")

# Input URL
url_input = st.text_input("Enter URL here:")

if st.button("Check URL"):
    if url_input.strip() == "":
        st.warning("Please enter a URL!")
    else:
        features = extract_features(url_input)
        X_new = pd.DataFrame([features])
        prediction = model.predict(X_new)[0]

        # Show result clearly
        if prediction == 1:
            st.error("🚨 This looks like a **Phishing Website**!")
        else:
            st.success("✅ This looks like a **Legitimate Website**!")

        # Show extracted features (optional for debugging)
        with st.expander("🔍 See extracted features"):
            st.json(features)
