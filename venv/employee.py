import tkinter as tk
from tkinter import ttk
from datetime import datetime
import sqlite3
import os
import sys
from PIL import Image, ImageTk

class EmployeeManager:
    def __init__(self, parent, main_menu_callback=None):
        self.main_menu_callback = main_menu_callback
        self.parent = parent
        self.database_path = 'db/inventory.db'
        self.initialize_database()
        self.setup_window()
        self.create_header_frame()
        self.add_image()
        self.create_employee_widgets()
        self.create_employee_table()
        self.create_footer()
        self.update_time_date()

    def setup_window(self):
        self.parent.title("Inventory Management System")
        self.parent.geometry("800x600")
        self.parent.configure(bg="light grey")

    def create_header_frame(self):
        self.header_frame = tk.Frame(self.parent, bg="dark blue")
        self.header_frame.pack(fill=tk.X)
        
        self.header_label = tk.Label(self.header_frame, text="Employee Management", bg="dark blue", fg="white", font=("Arial", 18))
        self.header_label.pack(pady=10)
        
        self.date_label = tk.Label(self.header_frame, text="", bg="dark blue", fg="white", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(self.header_frame, text="", bg="dark blue", fg="white", font=("Arial", 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        self.back_button = tk.Button(self.header_frame, text="Back", bg="red", command=self.go_back)
        self.back_button.pack(side=tk.RIGHT, padx=10)

        self.content_frame = tk.Frame(self.parent, bg="light grey")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def add_image(self):
        image_path = r"C:\Users\Craig\Desktop\Projects\assets\images\EMS1.jpeg" 
        try:
            image = Image.open(image_path)
            image = image.resize((400, 200)) 
            photo = ImageTk.PhotoImage(image)

            image_label = tk.Label(self.content_frame, image=photo, bg="light grey")
            image_label.image = photo  
            image_label.pack(side=tk.RIGHT, padx=20, pady=20)
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
        except IOError:
            print(f"Error: Unable to open image file at {image_path}")

    def update_time_date(self):
        now = datetime.now()
        current_date = now.strftime("%d-%m-%Y")
        current_time = now.strftime("%H:%M:%S")
        self.date_label.config(text=f"Date: {current_date}")
        self.time_label.config(text=f"Time: {current_time}")
        self.parent.after(1000, self.update_time_date)

    def initialize_database(self):
        if os.path.exists(self.database_path):
            try:
                with sqlite3.connect(self.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT 1')
            except sqlite3.DatabaseError as e:
                print(f"Database error: {e}")
                os.remove(self.database_path)
                print("Corrupted database removed. A new database will be created.")

        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Employees (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Gender TEXT NOT NULL,
                    Contact TEXT NOT NULL,
                    Email TEXT NOT NULL,
                    Password TEXT NOT NULL,
                    Address TEXT NOT NULL,
                    Position TEXT NOT NULL,
                    Salary REAL NOT NULL
                )
            ''')
            conn.commit()

    def create_employee_widgets(self):
        self.employee_frame = tk.Frame(self.content_frame, bg="light grey")
        self.employee_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        labels = ["Employee Name", "Gender", "Contact", "Email", "Password", "Address", "Position", "Salary"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.employee_frame, text=label, bg="light grey").grid(row=i+1, column=0, sticky='e')
            if label == "Gender":
                self.gender_var = tk.StringVar()
                tk.Radiobutton(self.employee_frame, text='Male', variable=self.gender_var, value='Male', selectcolor='light grey', bg="light grey").grid(row=i+1, column=1, sticky='w')
                tk.Radiobutton(self.employee_frame, text='Female', variable=self.gender_var, value='Female', selectcolor='light grey', bg="light grey").grid(row=i+1, column=2, sticky='w')
            elif label == "Password":
                self.entries[label] = tk.Entry(self.employee_frame, show='*', bg="white")
                self.entries[label].grid(row=i+1, column=1)
            else:
                self.entries[label] = tk.Entry(self.employee_frame, bg="white")
                self.entries[label].grid(row=i+1, column=1)

        button_frame = tk.Frame(self.employee_frame, bg="light grey")
        button_frame.grid(row=len(labels)+1, column=0, columnspan=3, pady=10)

        buttons = [
            ("Save", self.save_employee_button_clicked, "orange"),
            ("Update", self.update_employee_button_clicked, "light blue"),
            ("Delete", self.delete_employee_button_clicked, "light green"),
            ("View", self.show_employee_list, "red")
        ]

        for i, (text, command, color) in enumerate(buttons):
            tk.Button(button_frame, text=text, bg=color, command=command).grid(row=0, column=i, padx=5)

    def create_employee_table(self):
        self.tree_frame = tk.Frame(self.parent, bg="light grey")
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(self.tree_frame, columns=('ID', 'Name', 'Gender', 'Contact', 'Email', 'Password', 'Address', 'Position', 'Salary'), show='headings', yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.show_employee_list()

    def create_footer(self):
        self.footer_frame = tk.Frame(self.parent, bg="light grey")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System. All rights reserved.", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=2)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=2)

    def save_employee_button_clicked(self):
        name = self.entries["Employee Name"].get().strip()
        gender = self.gender_var.get()
        contact = self.entries["Contact"].get().strip()
        email = self.entries["Email"].get().strip()
        password = self.entries["Password"].get().strip()
        address = self.entries["Address"].get().strip()
        position = self.entries["Position"].get().strip()
        salary = self.entries["Salary"].get().strip()

        if not all([name, gender, contact, email, password, address, position, salary]):
            print("All fields are required.")
            return

        try:
            salary = float(salary)
        except ValueError:
            print("Salary must be a number.")
            return

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO Employees (Name, Gender, Contact, Email, Password, Address, Position, Salary) 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                               (name, gender, contact, email, password, address, position, salary))
                conn.commit()
            print("Employee saved successfully.")
            self.show_employee_list()
        except Exception as e:
            print(f"Error saving employee: {e}")

    def update_employee_button_clicked(self):
        selected_item = self.tree.selection()
        if not selected_item:
            print("No employee selected.")
            return
        
        emp_id = self.tree.item(selected_item[0])['values'][0]
        name = self.entries["Employee Name"].get().strip()
        gender = self.gender_var.get()
        contact = self.entries["Contact"].get().strip()
        email = self.entries["Email"].get().strip()
        password = self.entries["Password"].get().strip()
        address = self.entries["Address"].get().strip()
        position = self.entries["Position"].get().strip()
        salary = self.entries["Salary"].get().strip()

        if not all([name, gender, contact, email, password, address, position, salary]):
            print("All fields are required.")
            return

        try:
            salary = float(salary)
        except ValueError:
            print("Salary must be a number.")
            return

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''UPDATE Employees SET Name = ?, Gender = ?, Contact = ?, Email = ?, Password = ?, Address = ?, Position = ?, Salary = ? WHERE ID = ?''',
                               (name, gender, contact, email, password, address, position, salary, emp_id))
                conn.commit()
            print("Employee updated successfully.")
            self.show_employee_list()
        except Exception as e:
            print(f"Error updating employee: {e}")

    def delete_employee_button_clicked(self):
        selected_item = self.tree.selection()
        if not selected_item:
            print("No employee selected.")
            return

        emp_id = self.tree.item(selected_item[0])['values'][0]

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''DELETE FROM Employees WHERE ID = ?''', (emp_id,))
                conn.commit()
            print("Employee deleted successfully.")
            self.show_employee_list()
        except Exception as e:
            print(f"Error deleting employee: {e}")

    def show_employee_list(self):
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT * FROM Employees''')
                employees = cursor.fetchall()
            
            for i in self.tree.get_children():
                self.tree.delete(i)

            for emp in employees:
                self.tree.insert("", "end", values=emp)
        except Exception as e:
            print(f"Error retrieving employee list: {e}")

    def go_back(self):
        self.parent.destroy()  
        if self.main_menu_callback:
            self.main_menu_callback()
        else:
            print("Warning: No main menu callback provided. Unable to return to main menu.")
            sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeManager(root)
    root.mainloop()
