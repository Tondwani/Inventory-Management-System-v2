import os
import sqlite3
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from PIL import Image, ImageTk


class CategoryManager:
    def __init__(self, parent, main_menu_callback):
        self.main_menu_callback = main_menu_callback
        self.parent = parent
        self.root = parent
        self.setup_window()
        self.create_header_frame()
        self.add_image()
        self.create_widgets()
        self.create_category_table()
        self.create_footer()
        self.update_time_date()

    def setup_window(self):
        self.root.title("Inventory Management System")
        self.root.geometry("900x900")
        self.root.configure(bg="light grey")

    def create_header_frame(self):
        self.header_frame = tk.Frame(self.root, bg="dark blue")
        self.header_frame.pack(fill=tk.X)

        self.header_label = tk.Label(self.header_frame, text="Manage Category", bg="dark blue", fg="white", font=("Arial", 18))
        self.header_label.pack(pady=10)

        self.date_label = tk.Label(self.header_frame, text="", bg="dark blue", fg="white", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=10)

        self.time_label = tk.Label(self.header_frame, text="", bg="dark blue", fg="white", font=("Arial", 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)

        self.back_button = tk.Button(self.header_frame, text="Back", bg="red", fg="white", command=self.go_back)
        self.back_button.pack(side=tk.RIGHT, padx=10)

        self.content_frame = tk.Frame(self.root, bg="light grey")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def update_time_date(self):
        now = datetime.now()
        current_date = now.strftime("%d-%m-%Y")
        current_time = now.strftime("%H:%M:%S")
        self.date_label.config(text=f"Date: {current_date}")
        self.time_label.config(text=f"Time: {current_time}")
        self.root.after(1000, self.update_time_date)

    def add_image(self):
        image_path = r"C:\Users\Craig\Desktop\Projects\assets\images\Catergory.jpeg" 
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

    def create_widgets(self):
        self.category_frame = tk.Frame(self.content_frame, bg="light grey")
        self.category_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        tk.Label(self.category_frame, text="Enter Category Name", bg="light grey").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.category_input = ttk.Entry(self.category_frame, width=30)
        self.category_input.grid(row=0, column=1, padx=5, pady=5)

        button_frame = tk.Frame(self.category_frame, bg="light grey")
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.add_button = tk.Button(button_frame, text="Add", bg="light green", command=self.add_category)
        self.add_button.grid(row=0, column=0, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete", bg="light coral", command=self.delete_category)
        self.delete_button.grid(row=0, column=1, padx=5)

        self.view_button = tk.Button(button_frame, text="View", bg="light blue", command=self.populate_table)
        self.view_button.grid(row=0, column=2, padx=5)

    def create_category_table(self):
        self.tree_frame = tk.Frame(self.root, bg="light grey")
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.category_table = ttk.Treeview(self.tree_frame, columns=("ID", "Name"), show="headings", yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.category_table.heading("ID", text="Category ID")
        self.category_table.heading("Name", text="Category Name")
        self.category_table.column("ID", width=100)
        self.category_table.column("Name", width=200)
        self.category_table.pack(expand=True, fill='both')

        v_scrollbar.config(command=self.category_table.yview)
        h_scrollbar.config(command=self.category_table.xview)

        self.populate_table()

    def create_footer(self):
        self.footer_frame = tk.Frame(self.root, bg="light grey")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System. All rights reserved.", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=2)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=2)

    def add_category(self):
        category_name = self.category_input.get().strip()
        if category_name:
            try:
                conn = sqlite3.connect('db/inventory.db')
                c = conn.cursor()
                c.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
                conn.commit()
                conn.close()
                self.populate_table()
                self.category_input.delete(0, tk.END)
                messagebox.showinfo("Success", f"Category '{category_name}' added successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Category already exists.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error adding category: {e}")
        else:
            messagebox.showwarning("Warning", "Please enter a valid category name.")

    def delete_category(self):
        selected_item = self.category_table.selection()
        if selected_item:
            category_id = self.category_table.item(selected_item)["values"][0]
            try:
                conn = sqlite3.connect('db/inventory.db')
                c = conn.cursor()
                c.execute("DELETE FROM categories WHERE id=?", (category_id,))
                conn.commit()
                conn.close()
                self.populate_table()
                messagebox.showinfo("Success", f"Category ID '{category_id}' deleted successfully!")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error deleting category: {e}")
        else:
            messagebox.showwarning("Warning", "Please select a category to delete.")

    def populate_table(self):
        for row in self.category_table.get_children():
            self.category_table.delete(row)
        try:
            conn = sqlite3.connect('db/inventory.db')
            c = conn.cursor()
            c.execute("SELECT * FROM categories")
            categories = c.fetchall()
            conn.close()
            for category in categories:
                self.category_table.insert("", tk.END, values=category)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error fetching categories: {e}")

    def go_back(self):
        self.root.destroy()  
        if self.main_menu_callback:
            self.main_menu_callback()  
        else:
            print("Warning: No main Menu callback provided. Unable to return to main Menu.")
            sys.exit()

