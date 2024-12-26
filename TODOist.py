import customtkinter as ctk
from tkinter import ttk
import sqlite3
from functions import open_add_task_window, open_task_details_window, initialize_database, load_tasks

# Main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("TaskMaster")
root.geometry("800x600")

# Initialize database
initialize_database()

# Tab view for different sections
tab_view = ctk.CTkTabview(root)
tab_view.pack(fill="both", expand=True)

# Tasks Tab
tasks_tab = tab_view.add("Tasks")
add_task_button = ctk.CTkButton(tasks_tab, text="Add Task", command=lambda: open_add_task_window(tasks_tree, root), fg_color="#4B0082", text_color="#FFFFFF")
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
style.map("Treeview.Heading", background=[("active", "#4B0082")], foreground=[("active", "#FFFFFF")])
style.map("Treeview", background=[("selected", "#4B0082")], foreground=[("selected", "#FFFFFF")])

# Load tasks from database
load_tasks(tasks_tree)

# Matrix Tab
matrix_tab = tab_view.add("Matrix")
matrix_label = ctk.CTkLabel(matrix_tab, text="Eisenhower Matrix (Coming soon)", anchor="center", text_color="#FFFFFF")
matrix_label.pack(fill="both", expand=True, pady=20)

# Today Tab
today_tab = tab_view.add("Today")
today_label = ctk.CTkLabel(today_tab, text="Today's Tasks (Coming soon)", anchor="center", text_color="#FFFFFF")
today_label.pack(fill="both", expand=True, pady=20)

# Start application
root.mainloop()
