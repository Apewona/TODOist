# -*- coding: utf-8 -*-
# Imports ---------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
import customtkinter as ctk     # Custom tkinter package
from tkinter import ttk         # tkinter package
import sqlite3                  # sqlite3 -> Database package
import pickle                   # pickle -> to store data 
import spacy                    # spaCy -> text vectorization model
from tkcalendar import Calendar # calendar object 
import tkinter as tk
# Project functions
from functions import open_add_task_window, update_task_in_db
from functions import initialize_database, load_tasks

# Vectorization language model and classificator elements load ----------------------------------------
# -----------------------------------------------------------------------------------------------------
nlp = spacy.load("pl_core_news_sm") # Loads spacy language package

# Tokenizer function, have to be here, because pkl load vectorizer
def spacy_tokenizer(text):          
    doc = nlp(text)
    tokens = [token.text for token in doc
             if not token.is_stop and not token.is_punct]
    return tokens

# Load pre-trained model, encoder and vectorizer
with open("svm_model.pkl", "rb") as model_file:
    svm_model = pickle.load(model_file)

with open("onehot_encoder.pkl", "rb") as onehot_file:
    encoder = pickle.load(onehot_file)

with open("vectorizer.pkl", "rb") as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

with open("label_encoder.pkl", "rb") as label_encoder_file:
    label_encoder = pickle.load(label_encoder_file)

# Main application window class -----------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # class variables
        self.bg_color = "#fdebd3"
        self.border_color = "#264e70"
        self.button_color = "#f9b4ab"
        
        # window configuration
        self.title("ToDo-ist")                 # Window name
        self.geometry("1000x700")               # Window size
        self.configure(fg_color=self.bg_color)  # Window background color

        self.global_font = ctk.CTkFont(         # Font configuration     
            family="Consolas",                  # Font family
            size=15,                            # Font size 
            weight="bold"                       # Font weight
            ) 
        
        # Style Configuration
        ctk.set_appearance_mode("light")        # Set appearance mode
        ctk.set_default_color_theme("dark-blue")# Set color theme

        # Tab View configuration
        self.tab_view = ctk.CTkTabview(  
            self,                                                       # Root window
            fg_color=self.bg_color,                                     # foreground color
            corner_radius=0,                                            # corner radius
            border_color=self.border_color,                             # border color
            border_width=0,                                             # border width
            segmented_button_fg_color = self.bg_color,                  # button fg color
            segmented_button_selected_color = self.button_color,        # selected button color
            segmented_button_selected_hover_color = "#fff4f1",          # hovered selected color
            segmented_button_unselected_color = "#fff4f1",              # unselected color
            segmented_button_unselected_hover_color= self.button_color, # unselected hovered color
            text_color = self.border_color                              # text color
            )
        self.tab_view.pack(fill="both", expand=True)
        self.tab_view._segmented_button.configure(font=self.global_font)# Tab View FONT

        # Add Tabs
        self.tasks_tab = TasksTab(
            self.tab_view,
            self.global_font,
            self.bg_color,
            self.button_color
            )
        self.tab_view.add("Tasks")

# Tasks Tab class -------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
class TasksTab(ctk.CTkFrame):
    def __init__(self, parent, global_font, bg_color, button_color):
        super().__init__(parent, fg_color=bg_color)
        # Class variables
        self.global_font = global_font

        # On button hover functions
        def on_hover(event, button, hover_color):
            button.configure(bg=hover_color)

        def on_leave(event, button, original_color):
            button.configure(bg=original_color)

        # Delete selected task function
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

        # Buttons Frame
        self.buttons_frame = ctk.CTkFrame(self, fg_color=bg_color)
        self.buttons_frame.pack(pady=20)

        # Buttons
        self.add_task_button = tk.Button(
            self.buttons_frame,
            text="ADD TASK",
            command=lambda: open_add_task_window(self.tasks_tree, parent, vectorizer, encoder, svm_model, label_encoder),
            bg=button_color,
            font=global_font,
            relief="raised",
            bd=2,
            width=20,
            height=2
        )
        self.add_task_button.pack(pady=10)

        self.delete_task_button = tk.Button(
            self.buttons_frame,
            text="DELETE TASK",
            command=lambda: delete_selected_tasks(self.tasks_tree),
            bg="#fecbcb",
            font=global_font,
            relief="raised",
            bd=2,
            width=20,
            height=2
        )
        self.delete_task_button.pack(pady=10)

        # Buttons Events
        self.add_task_button.bind("<Enter>", lambda e: on_hover(e, self.add_task_button, "#f08080"))  
        self.add_task_button.bind("<Leave>", lambda e: on_leave(e, self.add_task_button, button_color))

        self.delete_task_button.bind("<Enter>", lambda e: on_hover(e, self.delete_task_button, "#ff9999"))
        self.delete_task_button.bind("<Leave>", lambda e: on_leave(e, self.delete_task_button, "#fecbcb"))

        self.add_task_button.pack(side="left", padx=10)
        self.delete_task_button.pack(side="left", padx=10)

        # Task Database View Frame
        self.tasks_frame = ctk.CTkFrame(parent, fg_color=bg_color)
        self.tasks_frame.pack(pady=10, fill="both", expand=True, padx=10)

        # Using ttk.Treeview for task list
        self.tasks_tree = ttk.Treeview(self.tasks_frame, columns=("Task", "Category", "Priority", "Due"), show="headings")
        self.tasks_tree.heading("Task", text="Task")
        self.tasks_tree.heading("Category", text="Category")
        self.tasks_tree.heading("Priority", text="Priority")
        self.tasks_tree.heading("Due", text="Due")

        def sort_column(tree, col, reverse):
            data = [(tree.set(child, col), child) for child in tree.get_children('')]
            data.sort(reverse=reverse)

            for index, (val, child) in enumerate(data):
                tree.move(child, '', index)

            tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

        self.tasks_tree.heading("Task", text="Task", command=lambda: sort_column(self.tasks_tree, "Task", False))
        self.tasks_tree.heading("Category", text="Category", command=lambda: sort_column(self.tasks_tree, "Category", False))
        self.tasks_tree.heading("Priority", text="Priority", command=lambda: sort_column(self.tasks_tree, "Priority", False))
        self.tasks_tree.heading("Due", text="Due", command=lambda: sort_column(self.tasks_tree, "Due", False))

        self.tasks_tree.pack(fill="both", expand=True)

        # Apply theme to Treeview
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", background="#fff4f1", foreground="#264e70", fieldbackground="#fff4f1")
        self.style.configure("Treeview.Heading", background="#f9b4ab", foreground="#264e70")
        self.style.configure("Treeview", font=("Consolas", 12), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Consolas", 12, "bold"))
        self.style.map("Treeview.Heading", background=[("active", "#f9b4ab")], foreground=[("active", "#FFFFFF")])
        self.style.map("Treeview", background=[("selected", "#f9b4ab")], foreground=[("selected", "#FFFFFF")])

        # Load tasks from database
        load_tasks(self.tasks_tree)
# Main Entry Point ------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()