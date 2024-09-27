import logging
import os
import sqlite3
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SalesManager:
    def __init__(self, parent, main_menu_callback=None):
        self.main_menu_callback = main_menu_callback
        self.parent = parent
        self.db_name = 'db/inventory.db'  
        self.setup_window()
        self.create_header_frame()
        self.create_content_frame()
        self.add_image()
        self.create_sales_widgets()
        self.create_sales_table()
        self.create_footer()
        self.update_time_date()

    def go_back(self):
        self.parent.destroy()
        if self.main_menu_callback:
            self.main_menu_callback()

    def setup_window(self):
        self.parent.title("Inventory Management System - Sales")
        self.parent.geometry("1200x700")
        self.parent.configure(bg="light grey")

    def create_header_frame(self):
        self.header_frame = tk.Frame(self.parent, bg="Pink")
        self.header_frame.pack(fill=tk.X)
        
        self.header_label = tk.Label(self.header_frame, text="Sales Management", bg="Pink", fg="white", font=("Arial", 18))
        self.header_label.pack(pady=10)
        
        self.date_label = tk.Label(self.header_frame, text="", bg="Pink", fg="white", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(self.header_frame, text="", bg="Pink", fg="white", font=("Arial", 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)

        self.back_button = tk.Button(self.header_frame, text="Back", bg="red", fg="white", command=self.go_back)
        self.back_button.pack(side=tk.RIGHT, padx=10)

    def create_content_frame(self):
        self.content_frame = tk.Frame(self.parent, bg="light grey")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def add_image(self):
        image_path = r"C:\Users\Craig\Desktop\Projects\assets\images\Sales.jpeg"
        try:
            image = Image.open(image_path)
            image = image.resize((400, 200))  # Adjust size as needed
            photo = ImageTk.PhotoImage(image)

            image_label = tk.Label(self.content_frame, image=photo, bg="light grey")
            image_label.image = photo
            image_label.pack(side=tk.RIGHT, padx=20, pady=20)
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
        except IOError:
            print(f"Error: Unable to open image file at {image_path}")


    def create_sales_widgets(self):
        self.sales_frame = tk.Frame(self.content_frame, bg="light grey")
        self.sales_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        labels = ["Product ID", "Quantity", "Lookup Product ID"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.sales_frame, text=label, bg="light grey").grid(row=i, column=0, sticky='e', padx=5, pady=5)
            self.entries[label] = tk.Entry(self.sales_frame, bg="white")
            self.entries[label].grid(row=i, column=1, padx=5, pady=5)

        button_frame = tk.Frame(self.sales_frame, bg="light grey")
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)

        buttons = [
            ("Process Sale", self.process_sale_button_clicked, "green"),
            ("View Sales", self.show_sales_list, "orange"),
            ("Lookup Product", self.lookup_product_button_clicked, "red"),
            ("Show Analytics", self.show_sales_analytics, "blue")
        ]

        for i, (text, command, color) in enumerate(buttons):
            tk.Button(button_frame, text=text, bg=color, command=command).grid(row=0, column=i, padx=5)

    def process_sale_button_clicked(self):
        product_id = self.entries["Product ID"].get()
        quantity = self.entries["Quantity"].get()
        self.process_sale(product_id, quantity)
        
    def create_sales_table(self):
        self.tree_frame = tk.Frame(self.parent, bg="light grey")
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(self.tree_frame, columns=('ID', 'Product Name', 'Quantity', 'Sale Date'), show='headings', yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)

        self.show_sales_list()


    def create_footer(self):
        self.footer_frame = tk.Frame(self.parent, bg="light grey")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System. All rights reserved.", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=2)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=2)

    def update_time_date(self):
        now = datetime.now()
        current_date = now.strftime("%d-%m-%Y")
        current_time = now.strftime("%H:%M:%S")
        self.date_label.config(text=f"Date: {current_date}")
        self.time_label.config(text=f"Time: {current_time}")
        self.parent.after(1000, self.update_time_date)

    def validate_input(self, product_id, quantity):
        if not product_id.isdigit() or not quantity.isdigit():
            raise ValueError("Product ID and Quantity must be integers.")
        if int(quantity) <= 0:
            raise ValueError("Quantity must be greater than zero.")

    def process_sale(self, product_id, quantity):
        try:
            self.validate_input(product_id, quantity)
            product_id = int(product_id)
            quantity = int(quantity)

            current_stock = self.execute_query(
                'SELECT Stock FROM Products WHERE ID = ?', (product_id,), fetchone=True
            )[0]
            if current_stock < quantity:
                raise ValueError(f"Insufficient stock. Available: {current_stock}")

            new_stock = current_stock - quantity
            self.execute_query(
                'UPDATE Products SET Stock = ? WHERE ID = ?', (new_stock, product_id), commit=True
            )

            sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.execute_query(
                'INSERT INTO Sales (ProductID, Quantity, SaleDate) VALUES (?, ?, ?)', (product_id, quantity, sale_date), commit=True
            )

            receipt = self.generate_receipt(product_id, quantity, sale_date)
            messagebox.showinfo("Sale Processed", f"Sale processed successfully.\n\n{receipt}")
            logging.info(f"Sale processed: ProductID={product_id}, Quantity={quantity}, SaleDate={sale_date}")

            self.check_stock_alert()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))

    def process_sale_button_clicked(self):
        product_id = self.entries["Product ID"].get()
        quantity = self.entries["Quantity"].get()
        self.process_sale(product_id, quantity)

    def lookup_product(self, product_id):
        product = self.execute_query(
            'SELECT * FROM Products WHERE ID = ?', (product_id,), fetchone=True
        )
        if product:
            return product
        else:
            raise ValueError("Product not found.")

    def lookup_product_button_clicked(self):
        product_id = self.entries["Lookup Product ID"].get()
        try:
            product = self.lookup_product(product_id)
            details = f"ProductID: {product[0]}\nName: {product[1]}\nStock: {product[2]}"
            messagebox.showinfo("Product Details", details)
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))

    def check_stock_alert(self):
        low_stock_products = self.execute_query(
            'SELECT ID, Name, Stock FROM Products WHERE Stock <= 5', fetchall=True
        )
        if low_stock_products:
            alert_message = "Low Stock Alert:\n"
            for product in low_stock_products:
                alert_message += f"ProductID: {product[0]}, Name: {product[1]}, Stock: {product[2]}\n"
            messagebox.showwarning("Stock Alert", alert_message)

    def show_sales_analytics(self):
        total_sales = self.execute_query(
            'SELECT SUM(Quantity) FROM Sales', fetchone=True
        )[0] or 0

        total_days = total_sales = self.execute_query(
            'SELECT COUNT(DISTINCT SaleDate) FROM Sales', fetchone=True
        )[0] or 1

        average_sales_per_day = total_sales / total_days

        analytics_message = (
            f"Total Sales Quantity: {total_sales}\n"
            f"Average Sales Per Day: {average_sales_per_day:.2f}"
        )
        messagebox.showinfo("Sales Analytics", analytics_message)

    def generate_receipt(self, product_id, quantity, sale_date):
        product = self.db_manager.execute_query(
            'SELECT Name FROM Products WHERE ID = ?', (product_id,), fetchone=True
        )[0]
        receipt = (
            f"--- Receipt ---\n"
            f"Product Name: {product}\n"
            f"Quantity: {quantity}\n"
            f"Sale Date: {sale_date}\n"
            f"----------------"
        )
        return receipt


    def execute_query(self, query, params=(), fetchone=False, fetchall=False, commit=False):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(query, params)

            if commit:
                conn.commit()

            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def show_sales_list(self):
        sales = self.execute_query(
            'SELECT Sales.ID, Products.Name, Sales.Quantity, Sales.SaleDate '
            'FROM Sales '
            'INNER JOIN Products ON Sales.ProductID = Products.ID', 
            fetchall=True
        )
        for i in self.tree.get_children():
            self.tree.delete(i)
        for sale in sales:
            self.tree.insert('', 'end', values=sale)

    def go_back(self):
        self.parent.destroy()  
        if self.main_menu_callback:
            self.main_menu_callback()  
        else:
            print("Warning: No main Menu callback provided. Unable to return to main Menu.")
            sys.exit()

