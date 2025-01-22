import sqlite3
from datetime import date
import tkinter as tk
from tkinter import messagebox, ttk

# Initialize Database
def initialize_db():
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                        id INTEGER PRIMARY KEY,
                        habit_name TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        completed_dates TEXT
                    )''')
    conn.commit()
    conn.close()

# Add a New Habit
def add_habit():
    habit_name = habit_name_entry.get()
    if not habit_name:
        messagebox.showerror("Error", "Habit name cannot be empty.")
        return

    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    start_date = date.today().isoformat()
    cursor.execute("INSERT INTO habits (habit_name, start_date, completed_dates) VALUES (?, ?, ?)",
                   (habit_name, start_date, ""))
    conn.commit()
    conn.close()
    refresh_habits()
    habit_name_entry.delete(0, tk.END)
    messagebox.showinfo("Success", f"Habit '{habit_name}' added!")

# Mark Habit as Completed
def mark_completed():
    selected_item = habit_list.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a habit to mark as completed.")
        return

    habit_id = habit_list.item(selected_item, "values")[0]
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("SELECT completed_dates FROM habits WHERE id=?", (habit_id,))
    result = cursor.fetchone()
    completed_dates = result[0].split(",") if result[0] else []

    today = date.today().isoformat()
    if today not in completed_dates:
        completed_dates.append(today)

    cursor.execute("UPDATE habits SET completed_dates=? WHERE id=?", (",".join(completed_dates), habit_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Habit marked as completed for today!")
    refresh_habits()

# View Habit Progress
def view_progress():
    selected_item = habit_list.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a habit to view progress.")
        return

    habit_id = habit_list.item(selected_item, "values")[0]
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("SELECT habit_name, completed_dates FROM habits WHERE id=?", (habit_id,))
    result = cursor.fetchone()
    conn.close()

    habit_name, completed_dates = result
    completed_dates = completed_dates.split(",") if completed_dates else []
    streak = calculate_streak(completed_dates)

    messagebox.showinfo("Progress", f"Habit: {habit_name}\nDays Completed: {len(completed_dates)}\nStreak: {streak}")

# Calculate Streak
def calculate_streak(dates):
    if not dates:
        return 0

    dates = sorted([date.fromisoformat(d) for d in dates])
    streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
        else:
            streak = 1
    return streak

# Refresh Habits List
def refresh_habits():
    for item in habit_list.get_children():
        habit_list.delete(item)

    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, habit_name, start_date FROM habits")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        habit_list.insert("", "end", values=row)

# Delete Habit
def delete_habit():
    selected_item = habit_list.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a habit to delete.")
        return

    habit_id = habit_list.item(selected_item, "values")[0]
    conn = sqlite3.connect("habits.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE id=?", (habit_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Habit deleted successfully!")
    refresh_habits()

# GUI Setup
root = tk.Tk()
root.title("Habit Tracker")
root.geometry("600x400")
root.configure(bg="lightblue")

# Title Label
title_label = tk.Label(root, text="Habit Tracker", font=("Arial", 24, "bold"), bg="lightblue", fg="darkblue")
title_label.pack(pady=10)

# Input Frame
input_frame = tk.Frame(root, bg="lightblue")
input_frame.pack(pady=10)

habit_name_label = tk.Label(input_frame, text="Habit Name:", font=("Arial", 14), bg="lightblue")
habit_name_label.grid(row=0, column=0, padx=5, pady=5)
habit_name_entry = tk.Entry(input_frame, width=30, font=("Arial", 14))
habit_name_entry.grid(row=0, column=1, padx=5, pady=5)
add_button = tk.Button(input_frame, text="Add Habit", font=("Arial", 12), bg="green", fg="white", command=add_habit)
add_button.grid(row=0, column=2, padx=5, pady=5)

# Habit List
columns = ("ID", "Habit Name", "Start Date")
habit_list = ttk.Treeview(root, columns=columns, show="headings", height=10)
habit_list.pack(pady=10, fill="x")

for col in columns:
    habit_list.heading(col, text=col)
    habit_list.column(col, width=200)

# Action Buttons
action_frame = tk.Frame(root, bg="lightblue")
action_frame.pack(pady=10)

mark_button = tk.Button(action_frame, text="Mark as Completed", font=("Arial", 12), bg="orange", fg="white",
                        command=mark_completed)
mark_button.grid(row=0, column=0, padx=10)

progress_button = tk.Button(action_frame, text="View Progress", font=("Arial", 12), bg="blue", fg="white",
                            command=view_progress)
progress_button.grid(row=0, column=1, padx=10)

delete_button = tk.Button(action_frame, text="Delete Habit", font=("Arial", 12), bg="red", fg="white",
                          command=delete_habit)
delete_button.grid(row=0, column=2, padx=10)

# Initialize Database and Load Habits
initialize_db()
refresh_habits()

# Run App
root.mainloop()
