import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from datetime import datetime
from PIL import Image, ImageTk
import sqlite3
import os

class ProductManager:
    def __init__(self, parent, main_menu_callback=None):
        self.parent = parent
        self.main_menu_callback = main_menu_callback
        self.database_path = 'db/inventory.db'
        self.initialize_database()
        self.setup_window()
        self.create_header_frame()
        self.create_content_frame()  
        self.add_image()
        self.create_product_widgets()
        self.create_product_table()
        self.create_footer()
        self.update_time_date()
        self.products = []

    def setup_window(self):
        self.parent.title("Inventory Management System")
        self.parent.geometry("800x600")
        self.parent.configure(bg="light grey")

    def create_header_frame(self):
        self.header_frame = tk.Frame(self.parent, bg="dark blue")
        self.header_frame.pack(fill=tk.X)
        
        self.header_label = tk.Label(self.header_frame, text="Product Management", bg="dark blue", fg="white", font=("Arial", 18))
        self.header_label.pack(pady=10)
        
        self.date_label = tk.Label(self.header_frame, text="", bg="dark blue", fg="white", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(self.header_frame, text="", bg="dark blue", fg="white", font=("Arial", 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        self.back_button = tk.Button(self.header_frame, text="Back", bg="red", fg="white", command=self.go_back)
        self.back_button.pack(side=tk.RIGHT, padx=10)

    def create_content_frame(self):
        """Create the content frame to hold widgets and images."""
        self.content_frame = tk.Frame(self.parent, bg="light grey")
        self.content_frame.pack(fill=tk.BOTH, expand=True)        

    def add_image(self):
        image_path = r"C:\Users\Craig\Desktop\Projects\assets\images\Product.jpg" 
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
                    cursor.execute('DROP TABLE IF EXISTS Products')
            except sqlite3.DatabaseError as e:
                print(f"Database error: {e}")
                os.remove(self.database_path)
                print("Corrupted database removed. A new database will be created.")

        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Products (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Price REAL NOT NULL,
                    Quantity INTEGER NOT NULL,
                    Status TEXT NOT NULL
                )
            ''')
            conn.commit()

    def create_product_widgets(self):
        self.product_frame = tk.Frame(self.content_frame, bg="light grey")
        self.product_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        labels = ["Product Name", "Price", "Quantity", "Status"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.product_frame, text=label, bg="light grey").grid(row=i+1, column=0, sticky='e')
            if label == "Status":
                self.entries[label] = ttk.Combobox(self.product_frame, values=["Available", "Unavailable"])
            else:
                self.entries[label] = tk.Entry(self.product_frame, bg="white")
            self.entries[label].grid(row=i+1, column=1)

        button_frame = tk.Frame(self.product_frame, bg="light grey")
        button_frame.grid(row=len(labels)+1, column=0, columnspan=2, pady=10)

        buttons = [
            ("Add", self.add_product, "green"),
            ("Update", self.edit_product, "orange"),
            ("Delete", self.delete_product, "red"),
            ("Export CSV", self.export_to_csv, "blue"),
            ( "View", self.view_product, "Dark grey")
        ]

        for i, (text, command, color) in enumerate(buttons):
            tk.Button(button_frame, text=text, bg=color, fg="white", command=command).grid(row=0, column=i, padx=5)

        # Search product
        tk.Label(self.product_frame, text="Search Product", bg="light grey").grid(row=0, column=0, sticky='e')
        self.search_entry = tk.Entry(self.product_frame, bg="white")
        self.search_entry.grid(row=0, column=1)
        tk.Button(self.product_frame, text="Search", bg="purple", fg="white", command=self.search_product).grid(row=0, column=2)

    def create_product_table(self):
        self.tree_frame = tk.Frame(self.parent, bg="light grey")
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.product_table = ttk.Treeview(self.tree_frame, columns=("ID", "Name", "Price", "Quantity", "Status"), show="headings",
                                          yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.product_table.heading("ID", text="ID")
        self.product_table.heading("Name", text="Name")
        self.product_table.heading("Price", text="Price")
        self.product_table.heading("Quantity", text="Quantity")
        self.product_table.heading("Status", text="Status")
        self.product_table.pack(fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.product_table.yview)
        h_scrollbar.config(command=self.product_table.xview)

        self.product_table.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.show_product_list()

    def on_tree_select(self, event):
        selected_item = self.product_table.selection()
        if selected_item:
            item = self.product_table.item(selected_item[0])
            values = item['values']
            self.entries["Product Name"].delete(0, tk.END)
            self.entries["Product Name"].insert(0, values[1])
            self.entries["Price"].delete(0, tk.END)
            self.entries["Price"].insert(0, values[2])
            self.entries["Quantity"].delete(0, tk.END)
            self.entries["Quantity"].insert(0, values[3])
            self.entries["Status"].delete(0, tk.END)
            self.entries["Status"].insert(0, values[4])

    def create_footer(self):
        self.footer_frame = tk.Frame(self.parent, bg="light grey")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System. All rights reserved.", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=2)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=2)

    def add_product(self):
        name = self.entries["Product Name"].get().strip()
        price = self.entries["Price"].get().strip()
        quantity = self.entries["Quantity"].get().strip()
        status = self.entries["Status"].get().strip()

        if not all([name, price, quantity, status]):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and Quantity must be an integer.")
            return

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO Products (Name, Price, Quantity, Status) 
                                  VALUES (?, ?, ?, ?)''', 
                               (name, price, quantity, status))
                conn.commit()
            messagebox.showinfo("Success", "Product added successfully.")
            self.show_product_list()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding product: {e}")

    def edit_product(self):
        selected_item = self.product_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "No product selected.")
            return

        name = self.entries["Product Name"].get().strip()
        price = self.entries["Price"].get().strip()
        quantity = self.entries["Quantity"].get().strip()
        status = self.entries["Status"].get().strip()

        if not all([name, price, quantity, status]):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Price must be a number and Quantity must be an integer.")
            return

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                item_id = self.product_table.item(selected_item[0])['values'][0]
                cursor.execute('''UPDATE Products SET Name = ?, Price = ?, Quantity = ?, Status = ? 
                                  WHERE ID = ?''', 
                               (name, price, quantity, status, item_id))
                conn.commit()
            messagebox.showinfo("Success", "Product updated successfully.")
            self.show_product_list()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating product: {e}")

    def delete_product(self):
        selected_item = self.product_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "No product selected.")
            return

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                item_id = self.product_table.item(selected_item[0])['values'][0]
                cursor.execute('''DELETE FROM Products WHERE ID = ?''', (item_id,))
                conn.commit()
            messagebox.showinfo("Success", "Product deleted successfully.")
            self.show_product_list()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting product: {e}")

    def show_product_list(self):
        for row in self.product_table.get_children():
            self.product_table.delete(row)

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM Products')
                products = cursor.fetchall()

                for product in products:
                    self.product_table.insert("", tk.END, values=product)
        except sqlite3.DatabaseError as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def search_product(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.show_product_list()
            return

        for row in self.product_table.get_children():
            self.product_table.delete(row)

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                query = '''SELECT * FROM Products WHERE Name LIKE ?'''
                cursor.execute(query, ('%' + search_term + '%',))
                products = cursor.fetchall()

                for product in products:
                    self.product_table.insert("", tk.END, values=product)
        except sqlite3.DatabaseError as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def export_to_csv(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not file_path:
                return

            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Name', 'Price', 'Quantity', 'Status'])
                
                with sqlite3.connect(self.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM Products')
                    products = cursor.fetchall()
                    
                    for product in products:
                        writer.writerow(product)

            messagebox.showinfo("Success", "Data exported to CSV successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to CSV: {e}")

    def view_product(self):
        selected_item = self.product_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "No product selected.")
            return

        item = self.product_table.item(selected_item[0])
        values = item['values']

        view_window = tk.Toplevel(self.parent)
        view_window.title("View Product")
        view_window.geometry("200x200")

        labels = ["ID", "Product Name", "Price", "Quantity", "Status"]
        for i, label in enumerate(labels):
            tk.Label(view_window, text=f"{label}:").grid(row=i, column=0, sticky='e', padx=5, pady=5)
            tk.Label(view_window, text=values[i]).grid(row=i, column=1, sticky='w', padx=5, pady=5)
        

    def go_back(self):
        self.parent.destroy()
        if self.main_menu_callback:
            self.main_menu_callback()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductManager(root)
    root.mainloop()
