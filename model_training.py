import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import joblib

# Load the dataset
file_path = '_table4.csv'
df = pd.read_csv(file_path)

# Rename the column to 'text'
df.columns = ['text']

# Verify the correct column name
if 'text' in df.columns:
    df['HUMAN'] = df['text'].apply(lambda x: x.split('<HUMAN>:')[1].split('<ASSISTANT>:')[0].strip())
    df['ASSISTANT'] = df['text'].apply(lambda x: x.split('<ASSISTANT>:')[1].strip())
else:
    print("Column 'text' not found in the DataFrame. Please check the column names.")
    print("Columns available:", df.columns)
    exit()

# Check for empty entries in HUMAN and ASSISTANT columns
empty_human = df['HUMAN'].isnull().sum()
empty_assistant = df['ASSISTANT'].isnull().sum()

if empty_human > 0 or empty_assistant > 0:
    print(f"Empty entries found - HUMAN: {empty_human}, ASSISTANT: {empty_assistant}")
    exit()

# Print some samples of HUMAN and ASSISTANT columns to verify correct splitting
print(df[['HUMAN', 'ASSISTANT']].head(10))

# Prepare the data for training
X = df['HUMAN']
y = df['ASSISTANT']

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a pipeline with TfidfVectorizer and LogisticRegression
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression())
])

# Train the model
pipeline.fit(X_train, y_train)

# Test the model
y_pred = pipeline.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))

# Save the model
joblib.dump(pipeline, 'mental_health_chatbot_model.pkl')
