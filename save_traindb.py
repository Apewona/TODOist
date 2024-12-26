import sqlite3
from datetime import datetime
import random
from datetime import datetime, timedelta

def generate_random_due_date():
    # Określenie zakresu dat
    two_weeks_ago = datetime.now() - timedelta(days=14)
    one_month_from_now = datetime.now() + timedelta(days=30)

    # Generowanie losowej daty w podanym zakresie
    random_date = two_weeks_ago + timedelta(days=random.randint(0, 44))  # 44 dni różnicy między datami

    return random_date.strftime('%Y-%m-%d')  # Formatowanie daty jako string

def generate_random_due_date():
    # Określenie zakresu dat
    two_weeks_ago = datetime.now() - timedelta(days=14)
    one_month_from_now = datetime.now() + timedelta(days=30)

    # Generowanie losowej daty w podanym zakresie
    random_date = two_weeks_ago + timedelta(days=random.randint(0, 44))  # 44 dni różnicy między datami

    return random_date.strftime('%Y-%m-%d')  # Formatowanie daty jako string

def read_and_insert_tasks(filename, db_file):
    """
    Reads tasks from a text file and inserts them into a SQLite database,
    handling potential missing due dates gracefully.

    Args:
        filename (str): The path to the text file containing tasks.
        db_file (str): The path to the SQLite database file.
    """

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    with open(filename, 'r') as file:
        for line in file:
            # Clean and split the line
            task_data = line.strip().split('], [')
            task_data = [item.strip('[]') for item in task_data]

            # Handle potential missing due date gracefully
            try:
                due_date = generate_random_due_date()
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                today = datetime.now()
                day_difference = (due_date_obj - today).days
            except (IndexError, ValueError):
                # If due date is missing or invalid, set defaults
                due_date = None
                day_difference = None
                print(f"Błędny format daty lub brak daty: {line}")

            # Insert task data into the database, handling potential missing elements
            if len(task_data) >= 4:  # Check if there are at least 4 elements
                cursor.execute("""
                    INSERT INTO tasks (title, description, priority, category, due_date, day_difference)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (task_data[0], task_data[1], task_data[2], task_data[3], due_date, day_difference))
            else:
                print(f"Błędny format zadania: {line}")  # Inform about invalid task format

    connection.commit()
    connection.close()

# Example usage
filename = "tasks_description.txt"  # Replace with your actual file path
db_file = "tasks.db"
read_and_insert_tasks(filename, db_file)