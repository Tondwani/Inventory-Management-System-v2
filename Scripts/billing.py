import os
import sqlite3
import sys
import tkinter as tk
import tkinter.simpledialog as simpledialog
from datetime import datetime
from tkinter import messagebox, ttk

from fpdf import FPDF
from PIL import Image, ImageTk


class BillingManager:
    def __init__(self, parent, main_menu_callback=None):
        self.main_menu_callback = main_menu_callback
        self.parent = parent 
        self.database_path = 'db/inventory.db'
        self.check_and_update_database_schema()
        self.setup_window()
        self.create_header_frame()
        self.create_content_frame()
        self.create_billing_widgets()
        self.add_image()
        self.create_bill_table()
        self.create_calculator()
        self.create_footer()
        self.update_time_date()

    def setup_window(self):
        self.parent.title("Inventory Management System")
        self.parent.geometry("1200x700")
        self.parent.configure(bg="light grey")

    def create_header_frame(self):
        self.header_frame = tk.Frame(self.parent, bg="Light green")
        self.header_frame.pack(fill=tk.X)
        
        self.header_label = tk.Label(self.header_frame, text="Billing", bg="Light green", fg="white", font=("Arial", 18))
        self.header_label.pack(pady=10)
        
        self.date_label = tk.Label(self.header_frame, text="", bg="Light green", fg="white", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = tk.Label(self.header_frame, text="", bg="Light green", fg="white", font=("Arial", 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        self.back_button = tk.Button(self.header_frame, text="Back", bg="red", command=self.go_back)
        self.back_button.pack(side=tk.RIGHT, padx=10)

    def update_time_date(self):
        now = datetime.now()
        current_date = now.strftime("%d-%m-%Y")
        current_time = now.strftime("%H:%M:%S")
        self.date_label.config(text=f"Date: {current_date}")
        self.time_label.config(text=f"Time: {current_time}")
        self.parent.after(1000, self.update_time_date)

    def create_content_frame(self):
        self.content_frame = tk.Frame(self.parent, bg="light grey")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)


    def create_billing_widgets(self):
        self.billing_frame = tk.Frame(self.content_frame, bg="light grey")
        self.billing_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        labels = ["Product ID", "Quantity", "Customer Name", "Customer Contact","Company", "Search"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.billing_frame, text=label, bg="light grey").grid(row=i, column=0, pady=5, sticky='e')
            self.entries[label] = tk.Entry(self.billing_frame)
            self.entries[label].grid(row=i, column=1, pady=5)

        button_frame = tk.Frame(self.billing_frame, bg="light grey")
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=5)

        buttons = [
            ("Add Bill", self.add_to_bill, "orange"),
            ("Generate Invoice", self.generate_invoice, "light blue"),
            ("View", self.view_invoices, "light green"),
            ("Search", self.search_invoices, "red")
        ]

        for i, (text, command, color) in enumerate(buttons):
            tk.Button(button_frame, text=text, bg=color, command=command).grid(row=0, column=i, padx=5)

    def add_image(self):
        image_path = r"C:\Users\Craig\Desktop\Projects\assets\images\Billing.jpeg" 
        try:
            image = Image.open(image_path)
            image = image.resize((400, 200)) 
            photo = ImageTk.PhotoImage(image)

            image_label = tk.Label(self.content_frame, image=photo, bg="light grey")
            image_label.image = photo  
            image_label.grid(row=0, column=1, padx=20, pady=20, sticky="ne")
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
        except IOError:
            print(f"Error: Unable to open image file at {image_path}")


    def create_bill_table(self):
        self.tree_frame = tk.Frame(self.content_frame)
        self.tree_frame.grid(row=1, column=1, padx=10, pady=10, sticky="se")

        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.bill_tree = ttk.Treeview(self.tree_frame, columns=("ID", "Quantity", "Price", "Total"), 
                                      show='headings', height=10, 
                                      yscrollcommand=v_scrollbar.set, 
                                      xscrollcommand=h_scrollbar.set)
        self.bill_tree.heading("ID", text="Product ID")
        self.bill_tree.heading("Quantity", text="Quantity")
        self.bill_tree.heading("Price", text="Price")
        self.bill_tree.heading("Total", text="Total")
        self.bill_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.bill_tree.yview)
        h_scrollbar.config(command=self.bill_tree.xview)

        self.bill_items = []


    def create_calculator(self):
        self.calc_frame = tk.Frame(self.content_frame, bg="light grey")
        self.calc_frame.grid(row=1, column=0, padx=10, pady=10, sticky="sw")

        self.calc_display = tk.Entry(self.calc_frame, width=20, font=("Arial", 14))
        self.calc_display.grid(row=0, column=0, columnspan=4, pady=5)

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        colors = ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA']  # Light bright colors

        row = 1
        col = 0
        for i, button in enumerate(buttons):
            command = lambda x=button: self.click_calculator(x)
            btn = tk.Button(self.calc_frame, text=button, width=5, command=command, bg=colors[i % len(colors)])
            btn.grid(row=row, column=col, pady=2)
            col += 1
            if col > 3:
                col = 0
                row += 1
                
    def click_calculator(self, key):
        if key == '=':
            try:
                result = eval(self.calc_display.get())
                self.calc_display.delete(0, tk.END)
                self.calc_display.insert(tk.END, str(result))
                # Update quantity or price in billing form
                if self.entries["Quantity"].get() == "":
                    self.entries["Quantity"].delete(0, tk.END)
                    self.entries["Quantity"].insert(0, str(result))
                else:
                    product_id = self.entries["Product ID"].get()
                    if product_id:
                        self.update_price(product_id, result)
            except:
                self.calc_display.delete(0, tk.END)
                self.calc_display.insert(tk.END, "Error")
        else:
            self.calc_display.insert(tk.END, key)

    def update_price(self, product_id, new_price):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''UPDATE Products SET Price = ? WHERE ID = ?''', (new_price, product_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Price updated for product ID {product_id}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while updating the price: {e}")

    def create_footer(self):
        self.footer_frame = tk.Frame(self.parent, bg="light grey")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System. All rights reserved.", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=2)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=2)

    def check_and_update_database_schema(self):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            print(f"Connected to database: {self.database_path}")

            # List all tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Tables in the database:", tables)

            # Retrieve schema for the Invoices table
            cursor.execute('''PRAGMA table_info(Invoices)''')
            invoices_schema = cursor.fetchall()
            print("Invoices table schema:", invoices_schema)

            # Required columns to check in the Invoices table
            required_columns = ['InvoiceID', 'CustomerName', 'CustomerContact', 'CompanyName', 'Date']
            existing_columns = [row[1] for row in invoices_schema]
            print("Existing columns:", existing_columns)
            print("Required columns:", required_columns)

            # Check if all required columns are present and add missing ones
            missing_columns = [col for col in required_columns if col not in existing_columns]
            for col in missing_columns:
                cursor.execute(f"ALTER TABLE Invoices ADD COLUMN {col} TEXT")
                print(f"Added {col} column to Invoices table")

            conn.commit()
            print("Database schema check and update completed successfully.")

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            messagebox.showerror("Database Error", f"An error occurred while checking/updating the database schema: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

        finally:
            if conn:
                conn.close()

    def add_to_bill(self):
        product_id = self.entries["Product ID"].get()
        quantity = self.entries["Quantity"].get()

        if not product_id or not quantity:
            messagebox.showwarning("Input Error", "Please enter both Product ID and Quantity.")
            return

        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT Price FROM Products WHERE ID = ?", (product_id,))
            result = cursor.fetchone()

            if not result:
                messagebox.showwarning("Product Not Found", f"No product found with ID: {product_id}")
                conn.close()
                return

            price = result[0]
            total = float(price) * int(quantity)

            self.bill_items.append((product_id, quantity, price, total))
            self.update_bill_table()

            self.entries["Product ID"].delete(0, tk.END)
            self.entries["Quantity"].delete(0, tk.END)
            conn.close()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while adding to the bill: {e}")

    def get_product_name(self, product_id):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT product_name FROM Products WHERE ID=?", (product_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "Unknown Product"
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return "Error fetching product"
    
    def generate_invoice(self):
        customer_name = self.entries["Customer Name"].get()
        customer_contact = self.entries["Customer Contact"].get()
        company_name = self.entries["Company"].get()

        if not customer_name or not customer_contact or not company_name:
            messagebox.showwarning("Input Error", "Please enter Customer Name, Contact, and Company.")
            return

        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            cursor.execute('''INSERT INTO Invoices (CustomerName, CustomerContact, CompanyName) 
                              VALUES (?, ?, ?)''', (customer_name, customer_contact, company_name))
            invoice_id = cursor.lastrowid

            for item in self.bill_items:
                product_id = item[0]
                quantity = item[1]
                price = item[2]
                total = item[3]
                cursor.execute('''INSERT INTO InvoiceItems (InvoiceID, ProductID, Quantity, Price, Total) 
                                  VALUES (?, ?, ?, ?, ?)''', (invoice_id, product_id, quantity, price, total))

            conn.commit()
            conn.close()

            self.show_invoice_window(customer_name, customer_contact, invoice_id, company_name)
            self.bill_items = []
            self.update_bill_table()

            self.entries["Customer Name"].delete(0, tk.END)
            self.entries["Customer Contact"].delete(0, tk.END)
            self.entries["Company"].delete(0, tk.END)

            messagebox.showinfo("Invoice Generated", f"Invoice ID {invoice_id} has been generated.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while generating the invoice: {e}")
    
    def show_invoice_window(self, customer_name, customer_contact, invoice_id, company_name):
        view_window = tk.Toplevel(self.parent)
        view_window.title("Invoice Details")
        view_window.geometry("400x600")  
        view_window.resizable(False, False) 

        # Main frame
        main_frame = tk.Frame(view_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        tk.Label(main_frame, text="INVOICE", font=("Arial", 16, "bold")).pack()

        # Company and invoice details
        details_frame = tk.Frame(main_frame)
        details_frame.pack(fill=tk.X, pady=5)

        tk.Label(details_frame, text=f"Invoice ID: {invoice_id}", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(details_frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(details_frame, text=f"Company: {company_name}", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(details_frame, text=f"Customer: {customer_name}", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(details_frame, text=f"Contact: {customer_contact}", font=("Arial", 10)).pack(fill=tk.X)

        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        # Items frame with scrollbar
        items_frame = tk.Frame(main_frame)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        canvas = tk.Canvas(items_frame)
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Headers for bill items
        headers = ["Product", "Qty", "Price", "Total"]
        for col, header in enumerate(headers):
            tk.Label(scrollable_frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=col, sticky="w", padx=5)

        # Add bill items
        for idx, item in enumerate(self.bill_items, start=1):
            product_id, quantity, price, item_total = item
            product_name = self.get_product_name(product_id)
            tk.Label(scrollable_frame, text=f"{product_name[:15]}...", font=("Arial", 9)).grid(row=idx, column=0, sticky="w", padx=5)
            tk.Label(scrollable_frame, text=f"{quantity}", font=("Arial", 9)).grid(row=idx, column=1, sticky="e", padx=5)
            tk.Label(scrollable_frame, text=f"R{price:.2f}", font=("Arial", 9)).grid(row=idx, column=2, sticky="e", padx=5)
            tk.Label(scrollable_frame, text=f"R{item_total:.2f}", font=("Arial", 9)).grid(row=idx, column=3, sticky="e", padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        # Totals
        total = sum(item[3] for item in self.bill_items)
        vat = total * 0.15
        grand_total = total + vat

        totals_frame = tk.Frame(main_frame)
        totals_frame.pack(fill=tk.X, pady=5)

        tk.Label(totals_frame, text=f"Subtotal: R{total:.2f}", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(totals_frame, text=f"VAT (15%): R{vat:.2f}", font=("Arial", 10)).pack(fill=tk.X)
        tk.Label(totals_frame, text=f"Grand Total: R{grand_total:.2f}", font=("Arial", 12, "bold")).pack(fill=tk.X)

        tk.Label(main_frame, text="Thank you for your business!", font=("Arial", 10, "italic")).pack(pady=(10, 5))

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Print", command=lambda: self.print_invoice(invoice_id)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save PDF", command=lambda: self.save_pdf(invoice_id, customer_name, customer_contact, company_name)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=view_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_pdf(self, invoice_id, customer_name, customer_contact, company_name):
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Error", "FPDF library is not installed. Please install it using 'pip install fpdf'")
            return

        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, txt="*****INVOICE*****", ln=True, align='C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, txt=f"Invoice ID: {invoice_id}", ln=True)
        pdf.cell(200, 10, txt=f"Date/Time: {date_time}", ln=True)
        pdf.cell(200, 10, txt=f"my Company: {company_name}", ln=True)
        pdf.cell(200, 10, txt=f"Customer Name: {customer_name}", ln=True)
        pdf.cell(200, 10, txt=f"Customer Contact: {customer_contact}", ln=True)

        pdf.ln(5)
        for item in self.bill_items:
            pdf.cell(200, 10, txt=f"Product: {item[0]}, Quantity: {item[1]}, Price: R{item[2]:.2f}, Total: R{item[3]:.2f}", ln=True)

        pdf.cell(200, 10, txt="***", ln=True, align='C')

        total = sum(item[3] for item in self.bill_items)
        vat = total * 0.15
        grand_total = total + vat

        pdf.cell(200, 10, txt=f"Subtotal: R{total:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"VAT (15%): R{vat:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Grand Total: R{grand_total:.2f}", ln=True)

        pdf.ln(5)
        pdf.cell(200, 10, txt="Thank you for shopping with us!", ln=True, align='C')

        filename = f"Invoice_{invoice_id}.pdf"
        pdf.output(filename)
        messagebox.showinfo("Save PDF", f"Invoice has been saved as '{filename}'")

    def update_bill_table(self):
        for i in self.bill_tree.get_children():
            self.bill_tree.delete(i)
        for item in self.bill_items:
            self.bill_tree.insert("", tk.END, values=item)


    def view_invoices(self):
        try:
            invoice_files = [f for f in os.listdir('invoices') if f.endswith('.pdf')]
            if not invoice_files:
                messagebox.showinfo("Info", "No invoices found.")
                return
            
            invoices = "\n".join(invoice_files)
            messagebox.showinfo("Invoices", f"Available invoices:\n{invoices}")

        except FileNotFoundError:
            messagebox.showerror("Error", "The 'invoices' directory does not exist.")

    def search_invoices(self):
        search_term = simpledialog.askstring("Search", "Enter invoice number:")
        if search_term:
            pdf_files = [f for f in os.listdir('invoices') if search_term in f]
            if pdf_files:
                files = "\n".join(pdf_files)
                messagebox.showinfo("Search Results", f"Found invoices:\n{files}")
            else:
                messagebox.showinfo("Search Results", "No invoices found.")

    def go_back(self):
        self.parent.destroy()  
        if self.main_menu_callback:
            self.main_menu_callback()
        else:
            print("Warning: No main menu callback provided. Unable to return to main menu.")
            sys.exit()


