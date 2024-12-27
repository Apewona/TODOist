import customtkinter as ctk
from tkcalendar import Calendar
import sqlite3
from datetime import datetime
from scipy.sparse import hstack
import pandas as pd
# -*- coding: utf-8 -*-

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

def open_add_task_window(tasks_tree, root, vectorizer, encoder, svm_model, label_encoder):
    def save_task():
        task_title = task_title_entry.get()
        task_description = task_description_entry.get("1.0", "end-1c")
        task_priority = priority_combobox.get()
        task_category = category_combobox.get()
        task_due = due_date_calendar.get_date()
        due_date_obj = datetime.strptime(task_due, "%m/%d/%y")
        current_date = datetime.now()
        day_difference = (due_date_obj - current_date).days
        if task_title:
            save_task_to_db(task_title, task_description, task_priority, task_category, task_due, day_difference, vectorizer, encoder,  svm_model, label_encoder)
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

    priority_combobox = ctk.CTkComboBox(add_task_window, values=["Lowest", "Low", "Medium", "High", "Highest"])
    priority_combobox.set("Medium")
    priority_combobox.pack(pady=5)

    category_combobox = ctk.CTkComboBox(add_task_window, values=["Work", "Study", "Personal Life", "Workout"])
    category_combobox.set("Study")
    category_combobox.pack(pady=5)

    due_date_calendar = Calendar(add_task_window, selectmode='day')
    due_date_calendar.pack(pady=5)

    ctk.CTkButton(add_task_window, text="Save Task", command=save_task, fg_color="#4B0082").pack(pady=20)

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
    cursor.execute("INSERT INTO tasks (title, description, priority, category, due_date, day_difference) VALUES (?, ?, ?, ?, ?, ?)",
                   (title, description, priority, category, due_date, day_difference))
    connection.commit()
    connection.close()

def update_task_in_db(task_id, title, description, priority, category, due_date):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET title = ?, description = ?, priority = ?, category = ?, due_date = ? WHERE id = ?",
                   (title, description, priority, category, due_date, task_id))
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