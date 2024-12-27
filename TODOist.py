# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import ttk
import sqlite3
import pickle
import spacy
from tkcalendar import Calendar

from functions import open_add_task_window, update_task_in_db, initialize_database, load_tasks


# Załaduj model języka polskiego
nlp = spacy.load("pl_core_news_sm")

# Tokenizer z obsługą polskich znaków
def spacy_tokenizer(text):
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return tokens
    
# Load pre-trained model and encoder and vectorizer
with open("svm_model.pkl", "rb") as model_file:
    svm_model = pickle.load(model_file)

with open("onehot_encoder.pkl", "rb") as onehot_file:
    encoder = pickle.load(onehot_file)

with open("vectorizer.pkl", "rb") as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

with open("label_encoder.pkl", "rb") as label_encoder_file:
    label_encoder = pickle.load(label_encoder_file)

# Main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("TaskMaster")
root.geometry("800x600")

# Initialize database
initialize_database()
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
            updated_result = result.get()
            update_task_in_db(task[0], updated_title, updated_description, updated_priority, updated_category, updated_due_date, updated_result)

            # Refresh task in Treeview
            selected_item = tasks_tree.selection()[0]
            tasks_tree.item(selected_item, values=(updated_title, updated_category, updated_priority, updated_due_date))
            load_eisenhower_matrix()
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

        priority_combobox = ctk.CTkComboBox(details_window, values=["Low", "Medium", "High", "Highest"])
        priority_combobox.set(task[3])
        priority_combobox.pack(pady=5)

        category_combobox = ctk.CTkComboBox(details_window, values=["Work", "Study", "Personal Life", "Workout"])
        category_combobox.set(task[4])
        category_combobox.pack(pady=5)

        result = ctk.CTkComboBox(details_window, values=["Do Now", "Schedule", "Delegate", "Delete"])
        result.set(task[7])
        result.pack(pady=5)

        due_date_calendar = Calendar(details_window, selectmode='day')
        due_date_calendar.pack(pady=10)
        due_date_calendar.selection_set(task[5])

        ctk.CTkButton(details_window, text="Save Changes", command=save_edits, fg_color="#4B0082").pack(pady=20)

# Tab view for different sections
tab_view = ctk.CTkTabview(root)
tab_view.pack(fill="both", expand=True)

# Tasks Tab
tasks_tab = tab_view.add("Tasks")
button_frame = ctk.CTkFrame(tasks_tab, fg_color="#2C2C2C")
button_frame.pack(fill="x", pady=10)

add_task_button = ctk.CTkButton(button_frame, text="Add Task", command=lambda: open_add_task_window(tasks_tree, root, vectorizer, encoder, svm_model, label_encoder), fg_color="#4B0082", text_color="#FFFFFF")
delete_task_button = ctk.CTkButton(button_frame, text="Delete Task", command=lambda: delete_selected_tasks(tasks_tree), fg_color="#1E1E1E", text_color="#FFFFFF")
add_task_button.pack(side="left", padx=5)
delete_task_button.pack(side="left", padx=5)
add_task_button.pack(pady=10)

tasks_frame = ctk.CTkFrame(tasks_tab, fg_color="#2C2C2C")
tasks_frame.pack(pady=10, fill="both", expand=True, padx=10)

# Using ttk.Treeview for task list
tasks_tree = ttk.Treeview(tasks_frame, columns=("Task", "Category", "Priority", "Due"), show="headings")
tasks_tree.heading("Task", text="Task")
tasks_tree.heading("Category", text="Category")
tasks_tree.heading("Priority", text="Priority")
tasks_tree.heading("Due", text="Due")

def sort_column(tree, col, reverse):
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    data.sort(reverse=reverse)

    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

tasks_tree.heading("Task", text="Task", command=lambda: sort_column(tasks_tree, "Task", False))
tasks_tree.heading("Category", text="Category", command=lambda: sort_column(tasks_tree, "Category", False))
tasks_tree.heading("Priority", text="Priority", command=lambda: sort_column(tasks_tree, "Priority", False))
tasks_tree.heading("Due", text="Due", command=lambda: sort_column(tasks_tree, "Due", False))

tasks_tree.pack(fill="both", expand=True)

# Double-click to open task details
def delete_selected_tasks(tree):
    selected_items = tree.selection()
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()

    for item in selected_items:
        task_title = tree.item(item, 'values')[0]
        cursor.execute("DELETE FROM tasks WHERE title = ?", (task_title,))
        tree.delete(item)

    connection.commit()
    connection.close()

def on_task_double_click(event):
    selected_item = tasks_tree.selection()
    if selected_item:
        task_title = tasks_tree.item(selected_item, 'values')[0]
        open_task_details_window(tasks_tree, root, task_title)

tasks_tree.bind("<Double-1>", on_task_double_click)

# Apply dark theme to Treeview
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#3C3C3C", foreground="#FFFFFF", fieldbackground="#3C3C3C")
style.configure("Treeview.Heading", background="#4B0082", foreground="#FFFFFF")
style.configure("Treeview", font=("Arial", 10), rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
style.map("Treeview.Heading", background=[("active", "#3A0066")], foreground=[("active", "#FFFFFF")])
style.map("Treeview", background=[("selected", "#4B0082")], foreground=[("selected", "#FFFFFF")])

# Load tasks from database
load_tasks(tasks_tree)

# Matrix Tab
matrix_tab = tab_view.add("Matrix")

# Podział na kwadranty
matrix_frame = ctk.CTkFrame(matrix_tab)
matrix_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Dodanie ramek dla każdego kwadrantu
do_now_frame = ctk.CTkFrame(matrix_frame, fg_color="#FF6347", corner_radius=10)
schedule_frame = ctk.CTkFrame(matrix_frame, fg_color="#FFA500", corner_radius=10)
delegate_frame = ctk.CTkFrame(matrix_frame, fg_color="#4682B4", corner_radius=10)
delete_frame = ctk.CTkFrame(matrix_frame, fg_color="#708090", corner_radius=10)

do_now_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
schedule_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
delegate_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
delete_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

# Etykiety dla każdego kwadrantu
ctk.CTkLabel(do_now_frame, text="Do Now", text_color="#FFFFFF").pack(pady=5)
ctk.CTkLabel(schedule_frame, text="Schedule", text_color="#FFFFFF").pack(pady=5)
ctk.CTkLabel(delegate_frame, text="Delegate", text_color="#FFFFFF").pack(pady=5)
ctk.CTkLabel(delete_frame, text="Delete", text_color="#FFFFFF").pack(pady=5)

# Dodanie Treeview dla każdego kwadrantu
def create_task_list(frame):
    tree = ttk.Treeview(frame, columns=("Task"), show="headings", height=6)
    tree.heading("Task", text="Task")
    tree.column("Task", width=150, anchor="w")
    tree.pack(fill="both", expand=True, padx=5, pady=5)
    return tree

do_now_list = create_task_list(do_now_frame)
schedule_list = create_task_list(schedule_frame)
delegate_list = create_task_list(delegate_frame)
delete_list = create_task_list(delete_frame)

# Funkcja do obsługi podwójnego kliknięcia na zadaniu w macierzy
def on_matrix_task_double_click(event, tree):
    selected_item = tree.selection()
    if selected_item:
        task_title = tree.item(selected_item, 'values')[0]
        open_task_details_window(tree, root, task_title)

# Przypisywanie zdarzenia podwójnego kliknięcia dla każdego Treeview w macierzy
do_now_list.bind("<Double-1>", lambda event: on_matrix_task_double_click(event, do_now_list))
schedule_list.bind("<Double-1>", lambda event: on_matrix_task_double_click(event, schedule_list))
delegate_list.bind("<Double-1>", lambda event: on_matrix_task_double_click(event, delegate_list))
delete_list.bind("<Double-1>", lambda event: on_matrix_task_double_click(event, delete_list))

# Pobieranie danych z bazy danych i przypisywanie do kwadrantów
def load_eisenhower_matrix():
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("SELECT title, due_date, result FROM tasks")
    tasks = cursor.fetchall()
    connection.close()

    # Czyszczenie list przed ponownym załadowaniem danych
    for tree in [do_now_list, schedule_list, delegate_list, delete_list]:
        for item in tree.get_children():
            tree.delete(item)

    # Przypisywanie zadań do odpowiednich list
    for task in tasks:
        title, due_date, result = task
        if result == "Do Now":
            do_now_list.insert("", "end", values=(title, due_date))
        elif result == "Schedule":
            schedule_list.insert("", "end", values=(title, due_date))
        elif result == "Delegate":
            delegate_list.insert("", "end", values=(title, due_date))
        elif result == "Delete":
            delete_list.insert("", "end", values=(title, due_date))

# Ładowanie danych do macierzy przy starcie aplikacji
load_eisenhower_matrix()

# Dynamiczny podział przestrzeni
matrix_frame.rowconfigure(0, weight=1)
matrix_frame.rowconfigure(1, weight=1)
matrix_frame.columnconfigure(0, weight=1)
matrix_frame.columnconfigure(1, weight=1)

# Start application
root.mainloop()

