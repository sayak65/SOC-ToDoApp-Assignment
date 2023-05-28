################################################## MODULES & PACKAGES ##################################################

import tkinter as tk
import sqlite3
import datetime
import plyer

from tkcalendar import DateEntry
from tkinter import messagebox

################################################### SQLITE DATABASE ####################################################

# Create A SQLite Database
connection = sqlite3.connect("taskmaster.db")
cursor = connection.cursor()
cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_table
                (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_detail TEXT,
                    task_date DATE,
                    task_time TIME
                )
                """)
connection.commit()

################################################### GLOBAL VARIABLES ###################################################

label_font_style = "Segoe UI"
text_box_font_style = "Dotum"
font_size = 10  # px
label_padx = 10  # px
check_time = (60 * 1000)  # ms

window_bg_color = "#313642"
window_fg_color = "#FFF"
text_box_bg_color = "#3E4553"
listbox_select_bg_color = "#AA9AFF"
listbox_select_fg_color = "#000"
add_button_bg_color = "#B1D199"
remove_button_bg_color = "#FF7360"


#################################################### CRUD FUNCTIONS ####################################################

def update_task_list():
    """
    Update the task list in the GUI by fetching tasks from the database and populating the listbox.
    """
    # Reset Existing List
    task_listbox.delete(0, tk.END)

    # Fetch All Tasks
    cursor.execute("""SELECT * FROM task_table""")
    task_list = cursor.fetchall()

    # Update Task List
    for index, task in enumerate(task_list):
        task = f"{index + 1}) {task[1]} | {'-'.join(task[2].split('-')[::-1])} | {task[3]}"
        task_listbox.insert(tk.END, task)


def add_new_task():
    """
    Add a new task to the database based on user inputs and update the task list in the GUI.
    """
    # Fetch User Inputs
    task_detail = task_detail_input_box.get("1.0", tk.END).strip("\n")
    task_date = task_date_entry_box.get_date()
    task_time = task_time_input_box.get().split(":")

    # Task Detail Entry Error Handling
    if (task_detail == "\n") | (task_detail == ""):
        return messagebox.showerror(title="Null Value Error",
                                    message="Please Fill Task Details")

    # Task Time Entry Error Handling
    if len(task_time) == 2:
        try:
            hour, minute = map(int, task_time)
            if hour < 0 or hour > 23:
                return messagebox.showerror(title="Value Error",
                                            message="HH (Hours) should be a value between 00 to 23")
            if minute < 0 or minute > 59:
                return messagebox.showerror(title="Value Error",
                                            message="MM (Minutes) should be value between 00 to 59")
            task_time = datetime.time(hour, minute)
        except:
            messagebox.showerror(title="Format Error",
                                 message="Please Fill According to HH:MM format" + "\n" +
                                         "HH should be a value between 00 to 23" + "\n" +
                                         "MM should be value between 00 to 59")
    else:
        return messagebox.showerror(title="Format Error",
                                    message="Please Fill According to HH:MM format")

    # Insert Task Into SQLite database
    cursor.execute("""INSERT INTO task_table (task_detail, task_date, task_time) VALUES (?, ?, ?)""",
                   (task_detail, task_date, str(task_time)))
    connection.commit()

    # Reset Entry Fields
    task_detail_input_box.delete("1.0", tk.END)
    task_date_entry_box.set_date(datetime.date.today())
    task_time_input_box.delete(0, tk.END)

    # Update Task-list Manager to Display New Tasks
    update_task_list()

    return True


def remove_task():
    """
    Remove the selected task from the database and update the task list in the GUI.
    """
    # Get Selected Task
    selected_task = task_listbox.get(tk.ACTIVE)
    selected_task = selected_task[selected_task.index(")") + 1:]
    task_detail, task_date, task_time = map(str.strip, selected_task.strip().split("|"))
    task_date = "-".join(task_date.split("-")[::-1])

    # Delete Selected Task
    cursor.execute("""
                    DELETE FROM task_table
                        WHERE (task_date=?) AND (task_time=?)
                    """,
                   (task_date, task_time))
    connection.commit()

    # Update Task Listbox
    update_task_list()

    return True


def check_tasks():
    """
    Check for tasks that match the current date and time and display notifications.
    Remove the matching tasks from the database and update the task list in the GUI.
    Rerun the check loop at the specified interval.
    """
    # Fetch Current Date & Time
    now = datetime.datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M' + ":00")

    # Fetch Matching Tasks
    cursor.execute("""
                    SELECT * FROM task_table
                        WHERE (task_date=?) AND (task_time=?)
                    """,
                   (current_date, current_time))

    matching_task_list = cursor.fetchall()
    print(matching_task_list)
    # Notify Matching Tasks
    for task in matching_task_list:
        task_detail = task[1]
        plyer.notification.notify(title="You Have Pending Task!!!",
                                  message=task_detail,
                                  timeout=2,
                                  app_icon=r"to-do-list.ico")

    cursor.execute("""
                    DELETE FROM task_table
                        WHERE (task_date=?) AND (task_time=?)
                    """,
                   (current_date, current_time))

    update_task_list()

    # Rerun Check Loop
    return main_window.after(ms=check_time, func=check_tasks)


############################################# ROOT WINDOW & CHILD WIDGETS ##############################################

# Instantiate Main Window & Configuring Global Settings
main_window = tk.Tk()
main_window.title("Task Master")
main_window.geometry("340x400")
main_window.resizable(width=False, height=False)
main_window.iconphoto(False, tk.PhotoImage(file="checklist.png"))
main_window.config(bg=window_bg_color)

# Create Task Detail Field
task_detail_label = tk.Label(main_window,
                             text='Task:',
                             padx=label_padx)

task_detail_input_box = tk.Text(main_window,
                                width=35,
                                height=3)

# Create the date entry field
task_date_label = tk.Label(main_window,
                           text='Date:',
                           padx=label_padx)

task_date_entry_box = DateEntry(main_window,
                                width=15,
                                background='darkblue',
                                foreground='white',
                                date_pattern='dd-mm-yyyy')

task_date_entry_box.set_date(datetime.date.today())

# Create the time entry field
task_time_label = tk.Label(main_window,
                           text='Time:')

task_time_input_box = tk.Entry(main_window,
                               width=12)

task_time_input_box.insert(index=0,
                           string="HH:MM")

# Create the add and remove buttons
add_button = tk.Button(main_window,
                       text='Add',
                       width=8,
                       command=add_new_task)

remove_button = tk.Button(main_window,
                          text='Remove',
                          width=8,
                          command=remove_task)

# Create the listbox to display tasks
task_listbox_label = tk.Label(main_window,
                              text="Pending Tasks")

task_listbox = tk.Listbox(main_window,
                          width=35,
                          height=12)

#################################################### WIDGET LAYOUT #####################################################

task_detail_label.grid(row=1, column=1, pady=(20, 5))
task_detail_input_box.grid(row=1, column=2, columnspan=4, pady=(20, 5))

task_date_label.grid(row=2, column=1, pady=5)
task_date_entry_box.grid(row=2, column=2)

task_time_label.grid(row=2, column=3)
task_time_input_box.grid(row=2, column=4)

task_listbox.grid(row=3, column=2, columnspan=3, pady=2)
task_listbox_label.grid(row=4, column=2, columnspan=3)

add_button.grid(row=5, column=0, columnspan=4, pady=10)
remove_button.grid(row=5, column=3, columnspan=5)

################################################# WIDGET CUSTOMIZATION #################################################

label_list = [task_detail_label, task_date_label, task_time_label, task_listbox_label]
for label in label_list:
    label.config(bg=window_bg_color,
                 fg=window_fg_color,
                 font=(label_font_style, font_size, "bold"))

task_detail_input_box.config(bg=text_box_bg_color,
                             fg=window_fg_color,
                             font=(text_box_font_style, 10, "bold"),
                             borderwidth=0,
                             insertbackground=window_fg_color)

task_time_input_box.config(bg=text_box_bg_color,
                           fg=window_fg_color,
                           font=(text_box_font_style, 10, "bold"),
                           borderwidth=0,
                           insertbackground=window_fg_color)

task_date_entry_box.config(background="#22252B",
                           foreground=window_fg_color,
                           headersbackground=listbox_select_bg_color,
                           normalbackground=window_bg_color,
                           normalforeground=window_fg_color,
                           selectbackground="#F8AA4C",
                           selectforeground='Black',
                           weekendbackground=window_bg_color,
                           weekendforeground=window_fg_color,
                           showweeknumbers=False,
                           showothermonthdays=False)

task_listbox.config(bg=text_box_bg_color,
                    fg=window_fg_color,
                    font=(text_box_font_style, 9, "bold"),
                    borderwidth=0,
                    border=0,
                    selectbackground=listbox_select_bg_color,
                    selectforeground=listbox_select_fg_color)

button_list = [add_button, remove_button]
button_list[0].config(bg=add_button_bg_color)
button_list[1].config(bg=remove_button_bg_color)
for button in button_list:
    button.config(fg="#000",
                  borderwidth=0,
                  border=0,
                  font=(label_font_style, 10, "bold"))

if __name__ == "__main__":
    # Fetch Current Tasks
    update_task_list()

    # Periodically Check Tasks
    main_window.after(ms=check_time, func=check_tasks)

    # Start Application
    main_window.mainloop()
