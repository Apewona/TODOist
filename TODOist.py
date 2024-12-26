import customtkinter as ctk
from tkinter import ttk
from tkcalendar import Calendar

def open_add_task_window():
    def save_task():
        task_title = task_title_entry.get()
        task_description = task_description_entry.get("1.0", "end-1c")
        task_priority = priority_combobox.get()
        task_category = category_combobox.get()
        task_due = due_date_calendar.get_date()

        if task_title:
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

    priority_combobox = ctk.CTkComboBox(add_task_window, values=["Low", "Medium", "High"])
    priority_combobox.set("Select Priority")
    priority_combobox.pack(pady=5)

    category_combobox = ctk.CTkComboBox(add_task_window, values=["Work", "Study", "Personal Life"])
    category_combobox.set("Select Category")
    category_combobox.pack(pady=5)

    due_date_calendar = Calendar(add_task_window, selectmode='day')
    due_date_calendar.pack(pady=5)

    ctk.CTkButton(add_task_window, text="Save Task", command=save_task, fg_color="#4B0082").pack(pady=20)

# Main application window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("TaskMaster")
root.geometry("800x600")

# Add Task Button
add_task_button = ctk.CTkButton(root, text="Add Task", command=open_add_task_window, fg_color="#4B0082", text_color="#FFFFFF")
add_task_button.pack(pady=10)

# Task list section
tasks_frame = ctk.CTkFrame(root, fg_color="#2C2C2C")
tasks_frame.pack(pady=10, fill="both", expand=True, padx=10)

# Using ttk.Treeview for task list
tasks_tree = ttk.Treeview(tasks_frame, columns=("Task", "Category", "Priority", "Due"), show="headings")
tasks_tree.heading("Task", text="Task")
tasks_tree.heading("Category", text="Category")
tasks_tree.heading("Priority", text="Priority")
tasks_tree.heading("Due", text="Due")

tasks_tree.pack(fill="both", expand=True)

# Apply dark theme to Treeview
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#3C3C3C", foreground="#FFFFFF", fieldbackground="#3C3C3C")
style.configure("Treeview.Heading", background="#4B0082", foreground="#FFFFFF")
style.map("Treeview.Heading", background=[("active", "#4B0082")], foreground=[("active", "#FFFFFF")])
style.map("Treeview", background=[("selected", "#4B0082")], foreground=[("selected", "#FFFFFF")])

# Start application
root.mainloop()
