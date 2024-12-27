# -*- coding: utf-8 -*-
# Imports ---------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
import customtkinter as ctk     # Custom tkinter package
from tkinter import ttk         # tkinter package
import sqlite3                  # SQLite3 for database management
import pickle                   # Pickle for data serialization
import spacy                    # SpaCy for text vectorization
from tkcalendar import Calendar # Calendar widget
from datetime import datetime
import tkinter as tk
# Project-specific functions
from functions import update_task_in_db, save_task_to_db
from functions import initialize_database, load_tasks

# Constants -------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
BUTTON_COLOR = "#f9b4ab"
BUTTON_RADIUS = 0
BORDER_WIDTH = 2
BORDER_COLOR = "#264e70"
BG_COLOR = "#fdebd3"

# Load language model and classifiers -----------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
nlp = spacy.load("pl_core_news_sm")

def spacy_tokenizer(text):
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return tokens

with open("svm_model.pkl", "rb") as model_file:
    svm_model = pickle.load(model_file)

with open("onehot_encoder.pkl", "rb") as onehot_file:
    encoder = pickle.load(onehot_file)

with open("vectorizer.pkl", "rb") as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

with open("label_encoder.pkl", "rb") as label_encoder_file:
    label_encoder = pickle.load(label_encoder_file)

# Initialize application window -----------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("TO-DO-ist")
root.geometry("1000x700")
root.configure(fg_color=BG_COLOR)

global_font = ctk.CTkFont(family="Consolas", size=15, weight="bold")

# Initialize the database ----------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
initialize_database()
def open_add_task_window(tasks_tree, root, vectorizer, encoder, svm_model, label_encoder, BG_COLOR, global_font):
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
            load_eisenhower_matrix()
            add_task_window.destroy()

    def add_placeholder_text(event):
        if task_description_entry.get("1.0", "end-1c") == "":
            task_description_entry.insert("1.0", "Description")
            task_description_entry.configure(fg_color="#fff4f1", text_color="gray")

    def remove_placeholder_text(event):
        if task_description_entry.get("1.0", "end-1c") == "Description":
            task_description_entry.delete("1.0", "end")
            task_description_entry.configure(fg_color="#fff4f1")

    add_task_window = ctk.CTkToplevel(root, fg_color=BG_COLOR)
    add_task_window.title("Add New Task")
    add_task_window.geometry("400x600")
    add_task_window.grab_set()  # Ensures focus remains on this window
    add_task_window.attributes("-topmost", True)  # Keeps the window on top

    task_title_entry = ctk.CTkEntry(add_task_window, width=300, placeholder_text="Task Title", fg_color="#fff4f1", font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray")
    task_title_entry.pack(pady=10)

    task_description_entry = ctk.CTkTextbox(add_task_window, width=300, height=100)
    task_description_entry.pack(pady=5)
    task_description_entry.insert("1.0", "Description")
    task_description_entry.configure(fg_color="#fff4f1",font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray", border_width = 2)
    task_description_entry.bind("<FocusIn>", remove_placeholder_text)
    task_description_entry.bind("<FocusOut>", add_placeholder_text)

    priority_combobox = ctk.CTkComboBox(add_task_window, values=["Low", "Medium", "High", "Highest"],fg_color="#fff4f1", font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray",
                                        button_hover_color = "#f9b4ab",
                                        dropdown_fg_color = "#fff4f1",
                                        dropdown_hover_color = "#f9b4ab",
                                        dropdown_text_color = "gray",
                                        dropdown_font = global_font,
                                        button_color="#f9b4ab")
    priority_combobox.set("Medium")
    priority_combobox.pack(pady=5)

    category_combobox = ctk.CTkComboBox(add_task_window, values=["Work", "Study", "Personal Life", "Workout"],fg_color="#fff4f1", font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray",
                                        button_hover_color = "#f9b4ab",
                                        dropdown_fg_color = "#fff4f1",
                                        dropdown_hover_color = "#f9b4ab",
                                        dropdown_text_color = "gray",
                                        dropdown_font = global_font,
                                        button_color="#f9b4ab")
    category_combobox.set("Study")
    category_combobox.pack(pady=5)

    due_date_calendar = Calendar(add_task_window, selectmode='day',
                                background = "#a07273",
                                foreground = "#fff4f1",
                                selectbackground="#f9b4ab",
                                headersbackground="#f9b4ab",
                                weekendbackground ="#db9c97",
                                othermonthbackground="#fdebd3",
                                othermonthwebackground="#bd8785")
    due_date_calendar.pack(pady=5)

    save_button = tk.Button(
        add_task_window,
        text="ADD TASK",
        command=lambda: save_task(),
        bg="#f9b4ab",
        font=global_font,
        relief="raised",
        bd=2,
        width=20,
        height=2
    )
    save_button.pack(pady=20)
    

def open_task_details_window(tasks_tree, root, task_title):
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
            updated_result = result_combobox.get()
            update_task_in_db(task[0], updated_title, updated_description, updated_priority, updated_category, updated_due_date, updated_result)

            # Refresh task in Treeview
            selected_item = tasks_tree.selection()[0]
            tasks_tree.item(selected_item, values=(updated_title, updated_category, updated_priority, updated_due_date))
            load_eisenhower_matrix()
            details_window.destroy()

        details_window = ctk.CTkToplevel(root, fg_color=BG_COLOR)
        details_window.title("Task Details")
        details_window.geometry("400x600")
        details_window.grab_set()
        details_window.attributes("-topmost", True)

        task_title_entry = ctk.CTkEntry(details_window, width=300, fg_color="#fff4f1", font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray")
        task_title_entry.insert(0, task[1])
        task_title_entry.pack(pady=10)

        task_description_entry = ctk.CTkTextbox(details_window, width=300, height=100)
        task_description_entry.insert("1.0", task[2])
        task_description_entry.configure(fg_color="#fff4f1",font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray", border_width = 2)
        task_description_entry.pack(pady=10)

        priority_combobox = ctk.CTkComboBox(details_window, values=["Low", "Medium", "High", "Highest"],fg_color="#fff4f1", font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray",
                                        button_hover_color = "#f9b4ab",
                                        dropdown_fg_color = "#fff4f1",
                                        dropdown_hover_color = "#f9b4ab",
                                        dropdown_text_color = "gray",
                                        dropdown_font = global_font,
                                        button_color="#f9b4ab")
        priority_combobox.set(task[3])
        priority_combobox.pack(pady=5)

        category_combobox = ctk.CTkComboBox(details_window, values=["Work", "Study", "Personal Life", "Workout"],fg_color="#fff4f1", font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray",
                                        button_hover_color = "#f9b4ab",
                                        dropdown_fg_color = "#fff4f1",
                                        dropdown_hover_color = "#f9b4ab",
                                        dropdown_text_color = "gray",
                                        dropdown_font = global_font,
                                        button_color="#f9b4ab")
        category_combobox.set(task[4])
        category_combobox.pack(pady=5)

        result_combobox = ctk.CTkComboBox(details_window, values=["Do Now", "Schedule", "Delegate", "Delete"],fg_color="#fff4f1", font=global_font, corner_radius=0, border_color="#f9b4ab", text_color="gray",
                                        button_hover_color = "#f9b4ab",
                                        dropdown_fg_color = "#fff4f1",
                                        dropdown_hover_color = "#f9b4ab",
                                        dropdown_text_color = "gray",
                                        dropdown_font = global_font,
                                        button_color="#f9b4ab")
        result_combobox.set(task[7])
        result_combobox.pack(pady=5)

        due_date_calendar = Calendar(details_window, selectmode='day',
                                background = "#a07273",
                                foreground = "#fff4f1",
                                selectbackground="#f9b4ab",
                                headersbackground="#f9b4ab",
                                weekendbackground ="#db9c97",
                                othermonthbackground="#fdebd3",
                                othermonthwebackground="#bd8785")
        due_date_calendar.pack(pady=10)
        due_date_calendar.selection_set(task[5])

        save_button = tk.Button(
            details_window,
            text="SAVE",
            command=lambda: save_edits(),
            bg="#f9b4ab",
            font=global_font,
            relief="raised",
            bd=2,
            width=20,
            height=2
        )
        save_button.pack(pady=20)

# Tab view for different sections ---------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
tab_view = ctk.CTkTabview(root, fg_color=BG_COLOR, corner_radius=0, border_color=BORDER_COLOR, border_width=0,
                          segmented_button_fg_color=BG_COLOR,
                          segmented_button_selected_color=BUTTON_COLOR,
                          segmented_button_selected_hover_color="#fff4f1",
                          segmented_button_unselected_color="#fff4f1",
                          segmented_button_unselected_hover_color=BUTTON_COLOR,
                          text_color=BORDER_COLOR)
tab_view.pack(fill="both", expand=True)
tab_view._segmented_button.configure(font=global_font)

# Tasks Tab -------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
tasks_tab = tab_view.add("Tasks")

# Buttons ---------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
buttons_frame = tk.Frame(tasks_tab, bg=BG_COLOR)
buttons_frame.pack(pady=20)

add_task_button = tk.Button(
    buttons_frame,
    text="ADD TASK",
    command=lambda: open_add_task_window(tasks_tree, root, vectorizer, encoder, svm_model, label_encoder, BG_COLOR, global_font),
    bg=BUTTON_COLOR,
    font=global_font,
    relief="raised",
    bd=BORDER_WIDTH,
    width=20,
    height=2
)
add_task_button.pack(side="left", padx=10)

delete_task_button = tk.Button(
    buttons_frame,
    text="DELETE TASK",
    command=lambda: delete_selected_tasks(tasks_tree),
    bg="#fecbcb",
    font=global_font,
    relief="raised",
    bd=BORDER_WIDTH,
    width=20,
    height=2
)
delete_task_button.pack(side="left", padx=10)

# Tasks Frame ------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
tasks_frame = ctk.CTkFrame(tasks_tab, fg_color=BG_COLOR)
tasks_frame.pack(pady=10, fill="both", expand=True, padx=10)

# Treeview for task list ------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
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

# Apply Treeview styles -------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#fff4f1", foreground="#264e70", fieldbackground="#fff4f1")
style.configure("Treeview.Heading", background=BUTTON_COLOR, foreground=BORDER_COLOR)
style.configure("Treeview", font=("Consolas", 12), rowheight=25)
style.configure("Treeview.Heading", font=("Consolas", 12, "bold"))
style.map("Treeview.Heading", background=[("active", BUTTON_COLOR)], foreground=[("active", "#FFFFFF")])
style.map("Treeview", background=[("selected", BUTTON_COLOR)], foreground=[("selected", "#FFFFFF")])

# Load tasks into Treeview ---------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
load_tasks(tasks_tree)

# Eisenhower Matrix Tab ------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
matrix_tab = tab_view.add("Matrix")

matrix_frame = ctk.CTkFrame(matrix_tab,fg_color=BG_COLOR)
matrix_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Quadrants -------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
do_now_frame = ctk.CTkFrame(matrix_frame, fg_color="#b12b41", corner_radius=10)
schedule_frame = ctk.CTkFrame(matrix_frame, fg_color="#457b9d", corner_radius=10)
delegate_frame = ctk.CTkFrame(matrix_frame, fg_color="#ffb290", corner_radius=10)
delete_frame = ctk.CTkFrame(matrix_frame, fg_color="#a8dadc", corner_radius=10)

do_now_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
schedule_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
delegate_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
delete_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

ctk.CTkLabel(do_now_frame, text="Important and Urgent (Do Now)", text_color="#FFFFFF", font=global_font).pack(pady=5)
ctk.CTkLabel(schedule_frame, text="Important but Not Urgent (Schedule)", text_color="#FFFFFF", font=global_font).pack(pady=5)
ctk.CTkLabel(delegate_frame, text="Not Important but Urgent (Delegate)", text_color="#264e70", font=global_font).pack(pady=5)
ctk.CTkLabel(delete_frame, text="Not Important and Not Urgent (Delete)", text_color="#264e70", font=global_font).pack(pady=5)

# Task List for Quadrants -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
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

def on_matrix_task_double_click(event, tree):
    selected_item = tree.selection()
    if selected_item:
        task_title = tree.item(selected_item, 'values')[0]
        open_task_details_window(tree, root, task_title)

for tree in [do_now_list, schedule_list, delegate_list, delete_list]:
    tree.bind("<Double-1>", lambda event, t=tree: on_matrix_task_double_click(event, t))

def load_eisenhower_matrix():
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("SELECT title, due_date, result FROM tasks")
    tasks = cursor.fetchall()
    connection.close()

    for tree in [do_now_list, schedule_list, delegate_list, delete_list]:
        for item in tree.get_children():
            tree.delete(item)

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

load_eisenhower_matrix()

matrix_frame.rowconfigure([0, 1], weight=1)
matrix_frame.columnconfigure([0, 1], weight=1)

# Run the application ---------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
root.mainloop()
