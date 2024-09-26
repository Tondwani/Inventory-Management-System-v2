import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import json
import os
from PIL import Image, ImageTk

class SettingsManager:
    def __init__(self, parent):
        self.parent = parent
        self.database_path = 'db/inventory.db'
        self.settings_db_path = 'db/settings.db'
        self.initialize_settings_database()
        self.setup_window()
        self.create_widgets()

    def get_setting(self, key, default=None):
        conn = sqlite3.connect(self.settings_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM Settings WHERE key=?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default

    def set_setting(self, key, value):
        conn = sqlite3.connect(self.settings_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO Settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()

    def initialize_settings_database(self):
        conn = sqlite3.connect(self.settings_db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Settings
                          (key TEXT PRIMARY KEY, value TEXT)''')
        conn.commit()
        conn.close()

    def setup_window(self):
        self.parent.title("Inventory Management System")
        self.parent.geometry("800x600") 
        
        self.bg_frame = tk.Frame(self.parent)
        self.bg_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.main_frame = tk.Frame(self.parent, bg='light grey')
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)

    def create_widgets(self):
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Title
        title_label = tk.Label(self.main_frame, text="Settings", font=('Arial', 16, 'bold'), bg='light grey')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.datetime_label = tk.Label(self.main_frame, font=('Arial', 12), bg='light grey')
        self.datetime_label.grid(row=0, column=1, pady=5, sticky='e')
        self.update_datetime()

        # Search widget
        self.create_search_widget()

        # Notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=2, column=1, sticky='nsew', padx=10, pady=10)

        self.create_database_tab()
        self.create_ui_tab()
        self.create_module_settings_tab()
        self.create_system_info_tab()
        self.create_export_import_tab()
        self.create_privacy_policy_tab()
        self.create_help_tab()

        # Sidebar
        self.create_sidebar()

        # Status bar
        self.status_bar = tk.Label(self.main_frame, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky='ew')

    def create_footer(self):
        self.footer_frame = tk.Frame(self.parent, bg="light grey")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System. All rights reserved.", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=2)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=2)

    def update_datetime(self):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.config(text=current_datetime)
        self.parent.after(1000, self.update_datetime)

    def create_sidebar(self):
        sidebar = ttk.Frame(self.main_frame, width=150)
        sidebar.grid(row=1, column=0, rowspan=2, sticky='ns')
        sidebar.grid_propagate(False)

        tabs = self.notebook.tabs()
        for i, tab in enumerate(tabs):
            tab_name = self.notebook.tab(tab, "text")
            btn = ttk.Button(sidebar, text=tab_name, command=lambda i=i: self.notebook.select(i))
            btn.grid(row=i, column=0, pady=5, padx=5, sticky='ew')

    def create_search_widget(self):
        search_frame = ttk.Frame(self.main_frame)
        search_frame.grid(row=1, column=1, sticky='ew', padx=10, pady=5)

        self.search_var = tk.StringVar()
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=(0, 5))
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_settings).pack(side='left')

    def create_database_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Database')

        ttk.Button(tab, text="Backup Database", command=self.backup_database).pack(pady=10)
        ttk.Button(tab, text="Restore Database", command=self.restore_database).pack(pady=10)
        ttk.Button(tab, text="View Database Statistics", command=self.view_database_stats).pack(pady=10)

    def create_ui_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='User Interface')

        ttk.Label(tab, text="Theme:").pack(pady=10)
        self.theme_var = tk.StringVar(value=self.get_setting('theme', 'Light'))
        ttk.Radiobutton(tab, text="Light", variable=self.theme_var, value="Light", command=self.apply_theme).pack()
        ttk.Radiobutton(tab, text="Dark", variable=self.theme_var, value="Dark", command=self.apply_theme).pack()

        ttk.Label(tab, text="Font Size:").pack(pady=10)
        self.font_size_var = tk.StringVar(value=self.get_setting('font_size', 'Medium'))
        ttk.Combobox(tab, textvariable=self.font_size_var, values=["Small", "Medium", "Large"]).pack()
        ttk.Button(tab, text="Apply Font Size", command=self.apply_font_size).pack(pady=10)

    def create_module_settings_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Module Settings')

        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        modules = ['Sales', 'Category', 'Employee', 'Product', 'Supplier', 'Billing']
        for i, module in enumerate(modules):
            frame = ttk.LabelFrame(scrollable_frame, text=module)
            frame.grid(row=i, column=0, padx=10, pady=5, sticky='ew')
            self.create_module_specific_settings(frame, module)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_system_info_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='System Info')

        version = self.get_setting('version', '1.0')
        ttk.Label(tab, text=f"Version: {version}").pack(pady=10)

        last_backup = self.get_setting('last_backup', 'Never')
        ttk.Label(tab, text=f"Last Backup: {last_backup}").pack(pady=10)

        ttk.Button(tab, text="View Active Users", command=self.view_active_users).pack(pady=10)

    def create_export_import_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Export/Import')

        ttk.Button(tab, text="Export Settings", command=self.export_settings).pack(pady=10)
        ttk.Button(tab, text="Import Settings", command=self.import_settings).pack(pady=10)

    def create_privacy_policy_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Privacy Policy')

        privacy_policy_text = """
        Privacy Policy:
        Your privacy is important to us. This application collects and stores data necessary for its functionality.
        We do not share your data with third parties without your consent.
        All information entered into the system is securely stored and managed.
        """

        privacy_label = tk.Label(tab, text=privacy_policy_text, wraplength=750, justify='left', bg='light grey')
        privacy_label.pack(padx=10, pady=10, fill='both', expand=True)

    def create_help_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Help')

        help_text = """
        How to use the Inventory Management System:
        1. Navigate through different tabs to manage various aspects like Sales, Category, etc.
        2. Use the 'Database' tab to backup and restore your database.
        3. The 'User Interface' tab allows you to customize the look and feel of the app.
        4. The 'My Company' tab is where you enter your company details.
        5. For detailed stats, use the 'System Info' tab.
        6. Always backup your settings and data regularly.
        """

        help_label = tk.Label(tab, text=help_text, wraplength=750, justify='left', bg='light grey')
        help_label.pack(padx=10, pady=10, fill='both', expand=True)

    def backup_database(self):
        backup_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if backup_path:
            try:
                with open(self.database_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                self.set_setting('last_backup', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                messagebox.showinfo("Backup Successful", "Database backed up successfully")
                self.status_bar.config(text="Database backup completed")
            except Exception as e:
                messagebox.showerror("Backup Failed", str(e))
                self.status_bar.config(text="Database backup failed")

    def restore_database(self):
        restore_path = filedialog.askopenfilename(filetypes=[("Database files", "*.db")])
        if restore_path:
            try:
                with open(restore_path, 'rb') as src, open(self.database_path, 'wb') as dst:
                    dst.write(src.read())
                messagebox.showinfo("Restore Successful", "Database restored successfully")
                self.status_bar.config(text="Database restore completed")
            except Exception as e:
                messagebox.showerror("Restore Failed", str(e))
                self.status_bar.config(text="Database restore failed")

    def view_database_stats(self):
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        stats = []
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            stats.append(f"{table[0]}: {count} records")
        conn.close()
        messagebox.showinfo("Database Statistics", "\n".join(stats))
        self.status_bar.config(text="Database statistics viewed")

    def apply_theme(self):
        theme = self.theme_var.get()
        self.set_setting('theme', theme)
        if theme == "Light":
            self.main_frame.configure(bg="light grey")
            style = ttk.Style()
            style.theme_use('default')
        else:
            self.main_frame.configure(bg="dark grey")
            style = ttk.Style()
            style.theme_use('clam')
        self.status_bar.config(text=f"Theme changed to {theme}")

    def apply_font_size(self):
        font_size = self.font_size_var.get()
        self.set_setting('font_size', font_size)
        sizes = {"Small": 8, "Medium": 10, "Large": 12}
        font_size = sizes.get(font_size, 10)
        style = ttk.Style()
        style.configure('.', font=('TkDefaultFont', font_size))
        self.status_bar.config(text=f"Font size changed to {font_size}")

    def create_module_specific_settings(self, frame, module):
        if module == 'Sales':
            ttk.Label(frame, text="Default Tax Rate:").pack(side='left')
            tax_rate = ttk.Entry(frame, width=10)
            tax_rate.pack(side='left')
            tax_rate.insert(0, self.get_setting('sales_tax_rate', '0'))
            ttk.Button(frame, text="Save", command=lambda: self.set_setting('sales_tax_rate', tax_rate.get())).pack(side='left')
        elif module == 'Category':
            ttk.Label(frame, text="Default Category:").pack(side='left')
            default_category = ttk.Entry(frame, width=20)
            default_category.pack(side='left')
            default_category.insert(0, self.get_setting('default_category', 'Uncategorized'))
            ttk.Button(frame, text="Save", command=lambda: self.set_setting('default_category', default_category.get())).pack(side='left')
        elif module == 'Employee':
            ttk.Label(frame, text="Default Shift Hours:").pack(side='left')
            shift_hours = ttk.Entry(frame, width=10)
            shift_hours.pack(side='left')
            shift_hours.insert(0, self.get_setting('default_shift_hours', '8'))
            ttk.Button(frame, text="Save", command=lambda: self.set_setting('default_shift_hours', shift_hours.get())).pack(side='left')
        elif module == 'Product':
            ttk.Label(frame, text="Low Stock Threshold:").pack(side='left')
            low_stock = ttk.Entry(frame, width=10)
            low_stock.pack(side='left')
            low_stock.insert(0, self.get_setting('low_stock_threshold', '10'))
            ttk.Button(frame, text="Save", command=lambda: self.set_setting('low_stock_threshold', low_stock.get())).pack(side='left')
        elif module == 'Supplier':
            ttk.Label(frame, text="Default Payment Terms (days):").pack(side='left')
            payment_terms = ttk.Entry(frame, width=10)
            payment_terms.pack(side='left')
            payment_terms.insert(0, self.get_setting('default_payment_terms', '30'))
            ttk.Button(frame, text="Save", command=lambda: self.set_setting('default_payment_terms', payment_terms.get())).pack(side='left')
        elif module == 'Billing':
            ttk.Label(frame, text="Invoice Prefix:").pack(side='left')
            invoice_prefix = ttk.Entry(frame, width=10)
            invoice_prefix.pack(side='left')
            invoice_prefix.insert(0, self.get_setting('invoice_prefix', 'INV-'))
            ttk.Button(frame, text="Save", command=lambda: self.set_setting('invoice_prefix', invoice_prefix.get())).pack(side='left')

    def search_settings(self):
        search_term = self.search_var.get().lower()
        conn = sqlite3.connect(self.settings_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM Settings WHERE lower(key) LIKE ? OR lower(value) LIKE ?", 
                       (f'%{search_term}%', f'%{search_term}%'))
        results = cursor.fetchall()
        conn.close()

        if results:
            result_text = "\n".join([f"{key}: {value}" for key, value in results])
            messagebox.showinfo("Search Results", result_text)
            self.status_bar.config(text=f"Found {len(results)} matching settings")
        else:
            messagebox.showinfo("Search Results", "No matching settings found.")
            self.status_bar.config(text="No matching settings found")

    def export_settings(self):
        settings = {}
        conn = sqlite3.connect(self.settings_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM Settings")
        for key, value in cursor.fetchall():
            settings[key] = value
        conn.close()

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Export Successful", "Settings exported successfully")
            self.status_bar.config(text="Settings exported successfully")

    def import_settings(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                settings = json.load(f)
            
            conn = sqlite3.connect(self.settings_db_path)
            cursor = conn.cursor()
            for key, value in settings.items():
                cursor.execute("INSERT OR REPLACE INTO Settings (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
            messagebox.showinfo("Import Successful", "Settings imported successfully")
            self.status_bar.config(text="Settings imported successfully")

    def view_active_users(self):
        # This is a mock implementation. In a real-world scenario, you'd query a user sessions table.
        active_users = [
            {"username": "Tondwani", "last_active": "2024-08-03 10:30:00"},
            {"username": "Craig", "last_active": "2024-08-03 11:15:00"},
        ]
        user_info = "\n".join([f"{user['username']} - Last active: {user['last_active']}" for user in active_users])
        messagebox.showinfo("Active Users", user_info)
        self.status_bar.config(text=f"Viewing {len(active_users)} active users")

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsManager(root)
    root.mainloop()