# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkcalendar import Calendar
import sqlite3
from datetime import datetime
from scipy.sparse import hstack
import pandas as pd
import tkinter as tk
# Load tasks from database
def load_tasks(tasks_tree):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("SELECT title, category, priority, due_date FROM tasks")
    tasks = cursor.fetchall()
    for task in tasks:
        tasks_tree.insert("", "end", values=task)
    connection.close()

# Database setup
def initialize_database():
    connection = sqlite3.connect("tasks.db")
    connection.text_factory = str  # Ustawia obsługę tekstu na UTF-8
    cursor = connection.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL COLLATE NOCASE,
                description TEXT COLLATE NOCASE,
                priority TEXT,
                category TEXT,
                due_date TEXT,
                day_difference TEXT,
                result TEXT
            )''')
    connection.commit()
    connection.close()


# Save a task to the database
def save_task_to_db(title, description, priority, category, due_date, day_difference, vectorizer, encoder, svm_model, label_encoder):

    # Zamiana tekstu na wektor
    combined_text = f"{title} {description}"
    tfidf_vector = vectorizer.transform([combined_text])
    
    # Tworzenie ramki danych dla priorytetu i kategorii
    priority_category_df = pd.DataFrame([[priority, category]], columns=["Priority", "Category"])

    # Enkodowanie priorytetu i kategorii w taki sam sposób jak w treningu
    priority_category_encoded = encoder.transform(priority_category_df)
    
    # Połączenie cech (konwersja do tablicy)
    feature_vector = hstack([tfidf_vector, priority_category_encoded, [[day_difference]]]).toarray()[0]
    
    # Klasyfikacja wyniku za pomocą modelu SVM
    result_index = svm_model.predict([feature_vector])[0]
    result = label_encoder.inverse_transform([result_index])[0]
    print(result)
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO tasks (title, description, priority, category, due_date, day_difference, result) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (title, description, priority, category, due_date, day_difference, result))
    connection.commit()
    connection.close()

def update_task_in_db(task_id, title, description, priority, category, due_date, result):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET title = ?, description = ?, priority = ?, category = ?, due_date = ?, result = ? WHERE id = ?",
                   (title, description, priority, category, due_date, result, task_id))
    connection.commit()
    connection.close()


