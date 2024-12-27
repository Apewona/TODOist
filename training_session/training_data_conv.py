import pandas as pd
import random
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from sklearn.preprocessing import OneHotEncoder
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
import pickle

# Załaduj model języka polskiego
nlp = spacy.load("pl_core_news_sm")

# Tokenizer z obsługą polskich znaków
def spacy_tokenizer(text):
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return tokens

# Funkcja przetwarzająca plik tekstowy
def process_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = []
            for line in file:
                items = line.strip().split("], [")
                items = [item.strip("[]") for item in items]
                if len(items) >= 4:
                    data.append(items)

        df = pd.DataFrame(data, columns=["Title", "Description", "Priority", "Category"])
        df["DayTillDue"] = df["Priority"].apply(lambda _: random.randint(-10, 30))
        df["ResultEisenhower"] = df.apply(
            lambda row: assign_result(row["Priority"], row["DayTillDue"]), axis=1
        )
        return df
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing file: {e}")
        return pd.DataFrame()

# Funkcja przypisująca kategorię w macierzy Eisenhowera
def assign_result(priority, day_till_due):
    if day_till_due <= 7:
        return "Do Now"
    if priority == "High":
        return "Schedule"
    if priority == "Medium":
        return "Delegate"
    return "Delete"

# Główne wykonanie
if __name__ == "__main__":
    # Plik wejściowy
    file_path = "tasks_description.txt"
    df = process_text_file(file_path)

    # Tworzenie kolumny Combined
    df["Combined"] = df["Title"] + " " + df["Description"]

    # Tworzenie obiektu TfidfVectorizer z tokenizatorem spaCy
    vectorizer = TfidfVectorizer(tokenizer=spacy_tokenizer, lowercase=True, token_pattern=None)
    tfidf_matrix = vectorizer.fit_transform(df["Combined"])

    # One-hot encoding dla kolumn 'Priority' i 'Category'
    encoder = OneHotEncoder(sparse_output=False)
    priority_category_encoded = encoder.fit_transform(df[["Priority", "Category"]])

    # Przekształcenie 'DayTillDue' na macierz sparse
    day_till_due = df["DayTillDue"].values.reshape(-1, 1)

    # Łączenie wszystkich cech w jedną macierz
    X = hstack([tfidf_matrix, priority_category_encoded, day_till_due])

    # Target labels (ResultEisenhower)
    y = df["ResultEisenhower"]

    # Podział danych na zestawy treningowe i testowe
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Trening modelu SVM
    model = SVC(kernel='linear', C=1)  # Linear kernel
    model.fit(X_train, y_train)

    # Zapis modelu SVM
    with open("svm_model.pkl", "wb") as model_file:
        pickle.dump(model, model_file)

    # Zapis encodera
    with open("encoder.pkl", "wb") as encoder_file:
        pickle.dump(encoder, encoder_file)

    # Zapis vectorizera
    with open("vectorizer.pkl", "wb") as vectorizer_file:
        pickle.dump(vectorizer, vectorizer_file)

    # Predykcja na danych testowych
    y_pred = model.predict(X_test)

    # Ocena modelu
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
