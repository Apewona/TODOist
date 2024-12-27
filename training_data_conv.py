import pandas as pd
import random
from datetime import datetime, timedelta
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

# Funkcja do generowania losowych dni do terminu
def generate_day_till_due():
    day = random.randint(-10, 30)
    return day

# Funkcja przypisująca kategorię w macierzy Eisenhowera
def assign_result(priority, day_till_due):
    try:
        if day_till_due <= 7:
            return "Do Now"
        if priority == "High":
            return "Schedule"
        if priority == "Medium":
            return "Delegate"
        return "Delete"
    except Exception as e:
        print(f"Error assigning result: {e}")
        return "Unknown"

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
        #print("Loaded DataFrame:")  # Debug: Sprawdź załadowane dane
        #print(df.head())

        df["DayTillDue"] = df["Priority"].apply(lambda _: generate_day_till_due())
        df["ResultEisenhower"] = df.apply(
            lambda row: assign_result(row["Priority"], row["DayTillDue"]), axis=1
        )
        #print("DataFrame after processing:")  # Debug: Sprawdź po dodaniu kolumn
        #print(df.head())
        return df
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing file: {e}")
        return pd.DataFrame()

# Główne wykonanie
if __name__ == "__main__":
    # Plik wejściowy
    file_path = "tasks_description.txt"
    df = process_text_file(file_path)

    # Debug: Oryginalny DataFrame
    #print("Oryginalny DataFrame:")
    #print(df.head())
    #print(f"Rozmiar DataFrame: {df.shape}")

    # Tworzenie kolumny Combined
    df["Combined"] = df["Title"] + " " + df["Description"]

    # Debug: Kolumna Combined
    #print("\nKolumna Combined:")
    #print(df["Combined"].head())

    # Tworzenie obiektu TfidfVectorizer z tokenizatorem spaCy
    vectorizer = TfidfVectorizer(tokenizer=spacy_tokenizer, lowercase=True, token_pattern=None)

    # Dopasowanie wektoryzatora do tekstu i przekształcenie go w macierz
    tfidf_matrix = vectorizer.fit_transform(df["Combined"])

    # Debug: Rozmiar i gęstość macierzy TF-IDF
    #print("\nRozmiar macierzy TF-IDF:")
    #print(tfidf_matrix.shape)
    #print(f"Liczba niezerowych elementów: {tfidf_matrix.nnz}")

    # Konwersja macierzy TF-IDF do DataFrame
    tfidf_df = pd.DataFrame(
        tfidf_matrix.toarray(),
        columns=vectorizer.get_feature_names_out()
    )

    # Debug: Nazwy cech i przykładowe wiersze macierzy TF-IDF
    #print("\nNazwy 20 pierwszych cech TF-IDF:")
    #print(vectorizer.get_feature_names_out()[:20])
    #print("\nPrzykładowe wiersze macierzy TF-IDF:")
    #print(tfidf_df)  


    # One-hot encoding dla kolumn 'Priority' i 'Category'
    encoder = OneHotEncoder()
    priority_category_encoded = encoder.fit_transform(df[["Priority", "Category"]])

    # Przekształcenie 'DayTillDue' na macierz sparse
    day_till_due = df["DayTillDue"].values.reshape(-1, 1)
    #print("\nMacierz sparse")
    #print(day_till_due)

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
    print("Model został zapisany jako 'svm_model.pkl'")

    # Opcjonalnie: Zapis encodera
    with open("encoder.pkl", "wb") as encoder_file:
        pickle.dump(encoder, encoder_file)
    print("Encoder został zapisany jako 'encoder.pkl'")
    # Predykcja na danych testowych
    y_pred = model.predict(X_test)

    # Ocena modelu
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Debugging: Sprawdź kształty macierzy
    print("\nShapes:")
    print(f"TF-IDF shape: {tfidf_matrix.shape}")
    print(f"Encoded Priority and Category shape: {priority_category_encoded.shape}")
    print(f"DayTillDue shape: {day_till_due.shape}")
    print(f"Combined X shape: {X.shape}")
