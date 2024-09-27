import os
import sqlite3
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from PIL import Image, ImageTk


class SupplierManager:
    def __init__(self, parent, main_menu_callback=None):
        self.main_menu_callback = main_menu_callback
        self.parent = parent 
        self.database_path = 'db/inventory.db'
        self.initialize_database()
        self.setup_window()
        self.create_header_frame()
        self.add_image()
        self.create_supplier_widgets()
        self.create_supplier_table()
        self.create_footer()
        self.update_time_date()

    def setup_window(self):
        self.parent.title("Inventory Management System")
        self.parent.geometry("1200x700")
        self.parent.configure(bg="light grey")

    def create_header_frame(self):
        self.header_frame = tk.Frame(self.parent, bg="dark blue")
        self.header_frame.pack(fill=tk.X)
        
        self.header_label = tk.Label(self.header_frame, text="Supplier Management", bg="dark blue", fg="white", font=("Arial", 18))
        self.header_label.pack(pady=10)
        
        self.date_label = tk.Label(self.header_frame, text="", bg="dark blue", fg="white", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(self.header_frame, text="", bg="dark blue", fg="white", font=("Arial", 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        self.back_button = tk.Button(self.header_frame, text="Back", bg="red", command=self.go_back)
        self.back_button.pack(side=tk.RIGHT, padx=10)

        self.content_frame = tk.Frame(self.parent, bg="light grey")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def update_time_date(self):
        now = datetime.now()
        current_date = now.strftime("%d-%m-%Y")
        current_time = now.strftime("%H:%M:%S")
        self.date_label.config(text=f"Date: {current_date}")
        self.time_label.config(text=f"Time: {current_time}")
        self.parent.after(1000, self.update_time_date)

    def add_image(self):
        image_path = r"C:\Users\Craig\Desktop\Projects\assets\images\Supplier.jpg"
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

    def initialize_database(self):
        if not os.path.exists(self.database_path):
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS Suppliers
                              (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                               Name TEXT NOT NULL,
                               ContactPerson TEXT NOT NULL,
                               PhoneNumber TEXT NOT NULL,
                               Description TEXT)''')
            conn.commit()
            conn.close()

    def create_supplier_widgets(self):
        self.supplier_frame = tk.Frame(self.content_frame, bg="light grey")
        self.supplier_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        labels = ["Invoice No.", "Supplier Name", "Contact Person", "Phone Number", "Description"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.supplier_frame, text=label, bg="light grey").grid(row=i, column=0, sticky='e', padx=10, pady=5)
            self.entries[label] = tk.Entry(self.supplier_frame, bg="white")
            self.entries[label].grid(row=i, column=1, padx=10, pady=5)

        button_frame = tk.Frame(self.supplier_frame, bg="light grey")
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)

        buttons = [
            ("Save", self.save_supplier, "green"),
            ("Update", self.update_supplier, "orange"),
            ("Delete", self.delete_supplier, "red"),
            ("Clear", self.clear_fields, "blue"),
            ("View Suppliers", self.show_supplier_list, "Dark grey")
        ]

        for i, (text, command, color) in enumerate(buttons):
            tk.Button(button_frame, text=text, bg=color, command=command).grid(row=0, column=i, padx=5)

    def create_supplier_table(self):
        self.tree_frame = tk.Frame(self.parent, bg="light grey")
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.supplier_table = ttk.Treeview(self.tree_frame, columns=('ID', 'Name', 'Contact Person', 'Phone Number', 'Description'), show='headings', yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        for col in self.supplier_table['columns']:
            self.supplier_table.heading(col, text=col)
        self.supplier_table.pack(fill=tk.BOTH, expand=True)

    def create_footer(self):
        self.footer_frame = tk.Frame(self.parent, bg="light grey")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System. All rights reserved.", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=5)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=5)

    def save_supplier(self):
        name = self.entries["Supplier Name"].get()
        contact_person = self.entries["Contact Person"].get()
        phone_number = self.entries["Phone Number"].get()
        description = self.entries["Description"].get()
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Suppliers (Name, ContactPerson, PhoneNumber, Description) 
                          VALUES (?, ?, ?, ?)''', (name, contact_person, phone_number, description))
        conn.commit()
        conn.close()
        self.clear_fields()
        self.show_supplier_list()

    def update_supplier(self):
        selected_item = self.supplier_table.selection()
        if selected_item:
            item_id = self.supplier_table.item(selected_item[0], 'values')[0]
            name = self.entries["Supplier Name"].get()
            contact_person = self.entries["Contact Person"].get()
            phone_number = self.entries["Phone Number"].get()
            description = self.entries["Description"].get()
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''UPDATE Suppliers SET Name=?, ContactPerson=?, PhoneNumber=?, Description=? 
                              WHERE ID=?''', (name, contact_person, phone_number, description, item_id))
            conn.commit()
            conn.close()
            self.clear_fields()
            self.show_supplier_list()

    def delete_supplier(self):
        selected_item = self.supplier_table.selection()
        if selected_item:
            item_id = self.supplier_table.item(selected_item[0], 'values')[0]
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM Suppliers WHERE ID=?''', (item_id,))
            conn.commit()
            conn.close()
            self.clear_fields()
            self.show_supplier_list()

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def show_supplier_list(self):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM Suppliers''')
        suppliers = cursor.fetchall()
        conn.close()
        
        for row in self.supplier_table.get_children():
            self.supplier_table.delete(row)
        for supplier in suppliers:
            self.supplier_table.insert('', 'end', values=supplier)

    def go_back(self):
        self.parent.destroy()  
        if self.main_menu_callback:
            self.main_menu_callback()
        else:
            print("Warning: No main menu callback provided. Unable to return to main menu.")
            sys.exit()

