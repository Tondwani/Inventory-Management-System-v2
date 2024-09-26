import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os
from datetime import datetime
import seaborn as sns
import numpy as p
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import subprocess 
import threading
import time
import random
from PIL import Image, ImageTk

class InventoryHomeMenuDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("900x800")
        self.root.configure(bg="light grey")
        self.setup_database()
        self.create_header()
        self.create_hamburger_menu()
        self.create_main_content() # Initializes self.main_content
        self.create_footer()
        self.start_real_time_updates()
        self.open_dashboard()  # Uses self.main_content

    def setup_database(self):
        self.conn = sqlite3.connect('db/inventory.db')
        self.cursor = self.conn.cursor()

    def create_header(self):
        self.header = tk.Frame(self.root, bg="dark blue")
        self.header.pack(fill=tk.X)
    
        tk.Label(self.header, text="Welcome!! Streamline your Inventory & Elevate your Efficiency", fg="white", bg="dark blue", font=("Gabriola", 12)).pack(side=tk.LEFT, padx=10)
    
        self.date_label = tk.Label(self.header, fg="white", bg="dark blue", font=("Arial", 12))
        self.date_label.pack(side=tk.RIGHT, padx=10)
    
        self.time_label = tk.Label(self.header, fg="white", bg="dark blue", font=("Arial", 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)
    
        self.logout_button = tk.Button(self.header, text="Logout", bg="yellow", command=self.logout)
        self.logout_button.pack(side=tk.RIGHT, padx=10)
        
        self.update_datetime()

    def update_datetime(self):
        now = datetime.now()
        self.date_label.config(text=now.strftime("%Y-%m-%d"))
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.root.after(1000, self.update_datetime)

    def create_footer(self):
        self.footer_frame = tk.Frame(self.root, bg="light grey")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=5)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=5)

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if confirm:
            self.parent.destroy()

    def create_hamburger_menu(self):
        # Hamburger menu
        self.menu_frame = tk.Frame(self.root, bg="white", width=200)
        self.menu_frame.place(x=-200, y=50, relheight=0.9)
        self.menu_visible = False

        self.hamburger_image = Image.open(r"C:\Users\Craig\Desktop\Projects\assets\images\hamburger_icon.png").resize((30, 30))
        self.hamburger_icon = ImageTk.PhotoImage(self.hamburger_image)
        self.hamburger_button = tk.Button(self.root, image=self.hamburger_icon, command=self.toggle_menu, bg="white", bd=0)
        self.hamburger_button.place(x=10, y=40)

        menu_items = [
            ("Billing", self.open_billing),
            ("Categories", self.open_categories),
            ("Employees", self.open_employees),
            ("Products", self.open_products),
            ("Sales", self.open_sales),
            ("Settings", self.open_settings),
            ("Suppliers", self.open_suppliers),
            ("Logout", self.logout),
        ]

        for text, command in menu_items:
            button = tk.Button(self.menu_frame, text=text, command=command, bg="white", fg="black", bd=0, padx=20, pady=10, anchor="w", width=15)
            button.pack(fill=tk.X)
            button.bind("<Enter>", lambda e, b=button: b.config(bg="black", fg="white"))
            button.bind("<Leave>", lambda e, b=button: b.config(bg="white", fg="black"))

    def toggle_menu(self):
        if self.menu_visible:
            self.slide_menu(-200)
        else:
            self.slide_menu(0)
        self.menu_visible = not self.menu_visible

    def slide_menu(self, target_x):
        current_x = self.menu_frame.winfo_x()
        total_distance = target_x - current_x
        step = total_distance // 10 if abs(total_distance) >= 10 else 1 

        def perform_slide():
            nonlocal current_x
            current_x += step
            self.menu_frame.place(x=current_x, y=0)
            if (step > 0 and current_x < target_x) or (step < 0 and current_x > target_x):
                self.root.after(10, perform_slide)
            else:
                self.menu_frame.place(x=target_x, y=50)

        perform_slide()

    def start_real_time_updates(self):
        self.update_dashboard()       

    def create_main_content(self):
        # Initializes self.main_content
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.place(x=200, y=50, relwidth=0.8, relheight=0.9)

    def execute_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def create_info_box(self, parent, title, query, col):
        frame = tk.Frame(parent, bg="white", relief="ridge", bd=1)
        frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        tk.Label(frame, text=title, font=("Arial", 10, "bold"), bg="white", fg="black").pack(pady=2)
        value = self.execute_query(query)[0]
        if title in ["Total Sales", "Total Inventory Value"]:
            formatted_value = f"R{value:,.2f}" if value else "R0.00"
        else:
            formatted_value = str(value)
        tk.Label(frame, text=formatted_value, font=("Arial", 9), bg="white", fg="black").pack()
        parent.grid_columnconfigure(col, weight=1)

    def get_total_inventory_value(self):
        query = "SELECT SUM(Price * Quantity) FROM Products"
        return self.execute_query(query)[0] or 0


    def create_products_pie_chart(self, frame):
        try:
            # Check if Categories table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Categories'")
            categories_exist = self.cursor.fetchone() is not None
            if categories_exist:
                query = """
                SELECT COALESCE(c.Name, 'Uncategorized') as Name, COUNT(*) as ProductCount
                FROM Products p
                LEFT JOIN Categories c ON p.CategoryID = c.ID
                GROUP BY c.ID, c.Name
                """
            else:
                query = """
                SELECT 'All Products' as Name, COUNT(*) as ProductCount
                FROM Products
                """
            df = pd.read_sql_query(query, self.conn)
            if df.empty:  
                tk.Label(frame, text="No data available for chart", fg="red", bg="white").pack(pady=10)
                return
            fig, ax = plt.subplots(figsize=(6, 6), facecolor='white')
            colors = sns.color_palette('pastel', len(df))
            wedges, texts, autotexts = ax.pie(df['ProductCount'], labels=df['Name'], autopct='%1.1f%%', colors=colors)
            
            # Enhance visibility of text
            plt.setp(texts, size=8, weight="bold")
            plt.setp(autotexts, size=8, weight="bold")
            
            ax.set_title('Products by Category', color='black', fontsize=12, fontweight='bold')
            # Add a legend
            ax.legend(wedges, df['Name'],
                      title="Categories",
                      loc="center left",
                      bbox_to_anchor=(1, 0, 0.5, 1))
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Error creating products visualization: {str(e)}")
            tk.Label(frame, text=f"Error in products chart: {str(e)}", fg="red", bg="white").pack(pady=10)

    def create_billing_viz(self, frame):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT SUM(TotalAmount) FROM Billing")
            total_billing = cursor.fetchone()[0] or 0

            target = 100000  # Example target
            percentage = min((total_billing / target * 100) if target != 0 else 0, 100)

            fig, ax = plt.subplots(figsize=(4, 3), facecolor='white')
            ax.barh(["Total Billing"], [percentage], height=0.5, color='black')
            ax.set_xlim(0, 100)
            ax.set_title(f"Total Billing: R{total_billing:,.2f} / R{target:,.2f}", color='black')
            ax.tick_params(axis='both', colors='black')
            ax.spines['bottom'].set_color('black')
            ax.spines['top'].set_color('black')
            ax.spines['right'].set_color('black')
            ax.spines['left'].set_color('black')

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        except Exception as e:
            print(f"Error creating billing visualization: {str(e)}")
            tk.Label(frame, text="Error in billing chart", fg="red", bg="white").pack(pady=10)
    

    def update_dashboard(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        info_row = tk.Frame(self.main_frame, bg="white")
        info_row.pack(fill=tk.X, padx=10, pady=10)

        # Create info boxes
        info_queries = [
            ("Total Employees", "SELECT COUNT(*) FROM Employees"),
            ("Total Suppliers", "SELECT COUNT(*) FROM Suppliers"),
            ("Total Sales", "SELECT SUM(TotalAmount) FROM Billing"),
            ("Low Stock Items", "SELECT COUNT(*) FROM Products WHERE Quantity < 10"),
            ("Total Inventory Value", "SELECT SUM(Price * Quantity) FROM Products")
        ]

        for i, (title, query) in enumerate(info_queries):
            self.create_info_box(info_row, title, query, i)

        # Visualizations row
        viz_row = tk.Frame(self.main_frame, bg="white")
        viz_row.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create visualizations
        self.create_products_pie_chart(viz_row)
        self.create_billing_viz(viz_row)

        self.root.after(45000, self.update_dashboard)


    def create_employee_viz(self, frame):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Employees")
        employee_count = cursor.fetchone()[0]

        label = tk.Label(frame, text=f"Total Number of Employees: {employee_count}", font=("Arial", 18))
        label.pack(pady=20)

    def create_sales_viz(self, frame):
        query = """
        SELECT p.Name, SUM(s.Quantity) as TotalQuantity
        FROM Sales s
        JOIN Products p ON s.ProductID = p.ID
        GROUP BY p.ID
        ORDER BY TotalQuantity DESC
        LIMIT 3
        """
        df = pd.read_sql_query(query, self.conn)

        tree = ttk.Treeview(frame, columns=('Product', 'Quantity'), show='headings', height=3)
        tree.heading('Product', text='Product')
        tree.heading('Quantity', text='Quantity')
        tree.column('Product', width=75)
        tree.column('Quantity', width=50)
        
        for index, row in df.iterrows():
            tree.insert('', 'end', values=(row['Name'], row['TotalQuantity']))

        tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")



    def create_products_viz(self, frame):
        try:
            # First, let's check the structure of the Products table
            self.cursor.execute("PRAGMA table_info(Products)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'CategoryID' not in columns:
                # If CategoryID doesn't exist, we'll use a simpler query
                query = """
                SELECT 'Uncategorized' as Name, COUNT(*) as ProductCount
                FROM Products
                """
            else:
                # If CategoryID exists, we'll use the original query
                query = """
                SELECT COALESCE(c.Name, 'Uncategorized') as Name, COUNT(*) as ProductCount
                FROM Products p
                LEFT JOIN Categories c ON p.CategoryID = c.ID
                GROUP BY c.ID, c.Name
                """
            
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty or df['ProductCount'].sum() == 0:
                raise ValueError("No data available for visualization")

            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(df['ProductCount'], labels=df['Name'], autopct='%1.1f%%')
            ax.set_title('Products by Category')
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            error_message = f"Error creating products visualization: {str(e)}"
            print(error_message)
            label = tk.Label(frame, text=error_message, fg="red")
            label.pack(pady=20)
            
    def create_suppliers_viz(self, frame):
        query = "SELECT COUNT(*) FROM Suppliers"
        supplier_count = self.execute_query(query)[0]
        self.create_info_box(frame, 0, 2, "Total Suppliers", query)

    # Add these new methods
    def open_sales(self):
        messagebox.showinfo("Sales", "Sales section not implemented yet.")

    def open_categories(self):
        messagebox.showinfo("Categories", "Categories section not implemented yet.")

    def open_billing(self):
        messagebox.showinfo("Billing", "Billing section not implemented yet.")

    def open_employees(self):
        messagebox.showinfo("Employees", "Employees section not implemented yet.")

    def open_products(self):
        messagebox.showinfo("Products", "Products section not implemented yet.")

    def open_suppliers(self):
        messagebox.showinfo("Suppliers", "Suppliers section not implemented yet.")

    def open_settings(self):
        messagebox.showinfo("Settings", "Settings section not implemented yet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryHomeMenuDashboard(root)
    root.mainloop()
