import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib
from utils.preprocess import clean_text
import glob

print("Loading dataset parts...")

# Load all sms_part*.csv files
files = glob.glob("sms_part*.csv")

dfs = [pd.read_csv(f) for f in files]
df = pd.concat(dfs, ignore_index=True)

print(f"Total messages loaded: {len(df)}")

# Convert label to numeric 1=spam, 0=ham
df['label'] = df['label'].map(lambda x: 1 if x == "spam" else 0)

# Clean text
df['clean_text'] = df['text'].apply(clean_text)

# Vectorize
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['clean_text'])
y = df['label']

# Train Naive Bayes model
model = MultinomialNB()
model.fit(X, y)

print("Training complete!")

# Save model + vectorizer
joblib.dump(model, "model/spam_model.joblib")
joblib.dump(vectorizer, "model/vectorizer.joblib")

print("Model saved successfully in /model/")
