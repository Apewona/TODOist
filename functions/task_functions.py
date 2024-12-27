# -*- coding: utf-8 -*-

import customtkinter as ctk
from tkcalendar import Calendar
import sqlite3
from datetime import datetime


def load_tasks(tasks_tree):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    try:
        # Debug: Sprawdź strukturę bazy danych
        cursor.execute("PRAGMA table_info(tasks)")
        print("Tabela tasks:")
        for column in cursor.fetchall():
            print(column)

        # Pobieranie danych z bazy
        cursor.execute("SELECT title, category, priority, due_date FROM tasks")
        tasks = cursor.fetchall()

        # Debug: Sprawdź pobrane dane
        print("Pobrane dane z bazy:")
        print(tasks)

        # Dodawanie danych do TreeView
        for task in tasks:
            tasks_tree.insert("", "end", values=task)
    except Exception as e:
        print(f"Błąd podczas ładowania zadań: {e}")
    finally:
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

def open_add_task_window(tasks_tree, root,svm_model,label_encoder,vectorizer):
    def save_task():
        task_title = task_title_entry.get()
        task_description = task_description_entry.get("1.0", "end-1c")
        task_priority = priority_combobox.get()
        task_category = category_combobox.get()
        task_due = due_date_calendar.get_date()

        if task_title:
            save_task_to_db(task_title, task_description, task_priority, task_category, task_due,svm_model,label_encoder,vectorizer)
            tasks_tree.insert("", "end", values=(task_title, task_category, task_priority, task_due))
            add_task_window.destroy()

    def add_placeholder_text(event):
        if task_description_entry.get("1.0", "end-1c") == "":
            task_description_entry.insert("1.0", "Description")
            task_description_entry.configure(fg_color="#6c757d")

    def remove_placeholder_text(event):
        if task_description_entry.get("1.0", "end-1c") == "Description":
            task_description_entry.delete("1.0", "end")
            task_description_entry.configure(fg_color="#6c757d")

    add_task_window = ctk.CTkToplevel(root)
    add_task_window.title("Add New Task")
    add_task_window.geometry("400x600")
    add_task_window.grab_set()  # Ensures focus remains on this window
    add_task_window.attributes("-topmost", True)  # Keeps the window on top

    task_title_entry = ctk.CTkEntry(add_task_window, width=300, placeholder_text="Task Title")
    task_title_entry.pack(pady=10)

    task_description_entry = ctk.CTkTextbox(add_task_window, width=300, height=100)
    task_description_entry.pack(pady=5)
    task_description_entry.insert("1.0", "Description")
    task_description_entry.configure(fg_color="#6c757d")
    task_description_entry.bind("<FocusIn>", remove_placeholder_text)
    task_description_entry.bind("<FocusOut>", add_placeholder_text)

    priority_combobox = ctk.CTkComboBox(add_task_window, values=["Low", "Medium", "High", "Highest"])
    priority_combobox.set("Medium")
    priority_combobox.pack(pady=5)

    category_combobox = ctk.CTkComboBox(add_task_window, values=["Work", "Study", "Personal Life", "Workout"])
    category_combobox.set("Personal Life")
    category_combobox.pack(pady=5)

    due_date_calendar = Calendar(add_task_window, selectmode='day')
    due_date_calendar.pack(pady=5)

    ctk.CTkButton(add_task_window, text="Save Task", command=save_task, fg_color="#4B0082").pack(pady=20)

# Save a task to the database
def save_task_to_db(title, description, priority, category, due_date, svm_model, label_encoder, vectorizer):
    # Weryfikacja, czy wybrano priorytet i kategorię
    if priority == "Select Priority" or category == "Select Category":
        print("Error: Priority and Category must be selected.")
        return

    # Calculate day_difference
    try:
        due_date_obj = datetime.strptime(due_date, "%m/%d/%y")
        due_date = due_date_obj.strftime("%Y-%m-%d")
    except ValueError as e:
        print(f"Error parsing due date: {e}")
        return

    current_date = datetime.now()
    day_difference = (due_date_obj - current_date).days

    # Prepare features for classification
    combined_text = f"{title} {description}"
    tfidf_vector = vectorizer.transform([combined_text])  # Vectorize text
    priority_encoded = ["Lowest", "Low", "Medium", "High", "Highest"].index(priority)
    category_encoded = ["Work", "Study", "Personal Life", "Workout"].index(category)

    # Combine features into a single vector
    feature_vector = [
        *tfidf_vector.toarray()[0],  # TF-IDF features
        priority_encoded,
        category_encoded,
        day_difference,
    ]

    # Dopasowanie do liczby cech modelu
    if len(feature_vector) != svm_model.n_features_in_:
        print(f"Feature mismatch: Model expects {svm_model.n_features_in_} features, but got {len(feature_vector)}.")
        return

    # Predict result
    result_index = svm_model.predict([feature_vector])[0]
    result = label_encoder.inverse_transform([result_index])[0]

    # Save task to database
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, description, priority, category, due_date, day_difference, result)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, description, priority, category, due_date, day_difference, result))
    connection.commit()
    connection.close()

def open_task_details_window(tasks_tree,root,task_title):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE title = ?", (task_title,))
    task = cursor.fetchone()
    connection.close()

    if task:
        def save_edits():
            updated_title = task_title_entry.get()
            updated_description = task_description_entry.get("1.0", "end-1c")
            updated_priority = priority_combobox.get()
            updated_category = category_combobox.get()
            updated_due_date = due_date_calendar.get_date()

            update_task_in_db(task[0], updated_title, updated_description, updated_priority, updated_category, updated_due_date)

            # Refresh task in Treeview
            selected_item = tasks_tree.selection()[0]
            tasks_tree.item(selected_item, values=(updated_title, updated_category, updated_priority, updated_due_date))

            details_window.destroy()

        details_window = ctk.CTkToplevel(root)
        details_window.title("Task Details")
        details_window.geometry("400x600")
        details_window.grab_set()  # Ensures focus remains on this window
        details_window.attributes("-topmost", True)  # Keeps the window on top

        task_title_entry = ctk.CTkEntry(details_window, width=300)
        task_title_entry.insert(0, task[1])
        task_title_entry.pack(pady=10)

        task_description_entry = ctk.CTkTextbox(details_window, width=300, height=100)
        task_description_entry.insert("1.0", task[2])
        task_description_entry.pack(pady=10)

        priority_combobox = ctk.CTkComboBox(details_window, values=["Lowest", "Low", "Medium", "High", "Highest"])
        priority_combobox.set(task[3])
        priority_combobox.pack(pady=5)

        category_combobox = ctk.CTkComboBox(details_window, values=["Work", "Study", "Personal Life", "Workout"])
        category_combobox.set(task[4])
        category_combobox.pack(pady=5)

        due_date_calendar = Calendar(details_window, selectmode='day')
        due_date_calendar.pack(pady=10)
        due_date_calendar.selection_set(task[5])

        ctk.CTkButton(details_window, text="Save Changes", command=save_edits, fg_color="#4B0082").pack(pady=20)