import hashlib
import os
import sqlite3
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk


class LoginManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Login System")
        self.root.geometry("500x650")
        self.create_welcome_message()
        self.add_image()
        self.create_main_frame()
        self.show_login_widgets()
        self.create_footer()

    def create_welcome_message(self):
        welcome_frame = tk.Frame(self.root, bg="light blue")
        welcome_frame.pack(fill=tk.X, pady=10)

        self.welcome_label = tk.Label(welcome_frame, text="", font=("Gabriola", 12, "bold"), fg="dark red", bg="light grey")
        self.welcome_label.pack()

        self.message = "Welcome!! Streamline your Inventory & Elevate your Efficiency"
        self.index = 0
        self.typing_effect()

    def typing_effect(self):
        if self.index < len(self.message):
            self.welcome_label.config(text=self.message[:self.index+1])
            self.index += 1
            self.root.after(100, self.typing_effect)

    def add_image(self):
        image_path = r"C:\Users\Craig\Desktop\Projects\assets\logo\lock 2.jpeg"
        try:
            image = Image.open(image_path)
            image = image.resize((400, 200))
            photo = ImageTk.PhotoImage(image)
            image_label = tk.Label(self.root, image=photo, bg="light grey")
            image_label.image = photo
            image_label.pack(pady=20)
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
        except IOError:
            print(f"Error: Unable to open image file at {image_path}")

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=20)

    def show_login_widgets(self):
        self.clear_main_frame()

        tk.Label(self.main_frame, text="Username").grid(row=0, column=0, pady=5)
        self.username_entry = tk.Entry(self.main_frame)
        self.username_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.main_frame, text="Password").grid(row=1, column=0, pady=5)
        self.password_entry = tk.Entry(self.main_frame, show='*')
        self.password_entry.grid(row=1, column=1, pady=5)

        self.show_password_var = tk.BooleanVar()
        self.show_password_checkbox = tk.Checkbutton(self.main_frame, text="Show Password", 
                                                     variable=self.show_password_var, 
                                                     command=self.toggle_password_visibility)
        self.show_password_checkbox.grid(row=2, column=0, columnspan=2, sticky='w')

        tk.Button(self.main_frame, text="Login", bg="yellow", command=self.login).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(self.main_frame, text="Forgot Password", bg="red", command=self.show_forgot_password).grid(row=4, column=0, columnspan=2)
        tk.Button(self.main_frame, text="New User? Register", bg="dark blue", fg="white", command=self.show_register_widgets).grid(row=5, column=0, columnspan=2, pady=10)

    def show_register_widgets(self):
        self.clear_main_frame()

        tk.Label(self.main_frame, text="Username").grid(row=0, column=0, pady=5)
        self.reg_username_entry = tk.Entry(self.main_frame)
        self.reg_username_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.main_frame, text="Password").grid(row=1, column=0, pady=5)
        self.reg_password_entry = tk.Entry(self.main_frame, show='*')
        self.reg_password_entry.grid(row=1, column=1, pady=5)

        tk.Label(self.main_frame, text="Email").grid(row=2, column=0, pady=5)
        self.reg_email_entry = tk.Entry(self.main_frame)
        self.reg_email_entry.grid(row=2, column=1, pady=5)

        self.reg_show_password_var = tk.BooleanVar()
        self.reg_show_password_checkbox = tk.Checkbutton(self.main_frame, text="Show Password", 
                                                         variable=self.reg_show_password_var, 
                                                         command=lambda: self.toggle_password_visibility_register(self.reg_password_entry, self.reg_show_password_var))
        self.reg_show_password_checkbox.grid(row=3, column=0, columnspan=2, sticky='w')

        tk.Button(self.main_frame, text="Register", command=self.register).grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(self.main_frame, text="Back to Login", command=self.show_login_widgets).grid(row=5, column=0, columnspan=2)

    def show_forgot_password(self):
        self.clear_main_frame()

        tk.Label(self.main_frame, text="Email").grid(row=0, column=0, pady=5)
        self.forgot_email_entry = tk.Entry(self.main_frame)
        self.forgot_email_entry.grid(row=0, column=1, pady=5)

        tk.Button(self.main_frame, text="Reset Password", bg="dark green", command=self.reset_password).grid(row=1, column=0, columnspan=2, pady=10)
        tk.Button(self.main_frame, text="Back to Login", bg="light blue", command=self.show_login_widgets).grid(row=2, column=0, columnspan=2)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')

    def toggle_password_visibility_register(self, password_entry, show_password_var):
        if show_password_var.get():
            password_entry.config(show='')
        else:
            password_entry.config(show='*')

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('db/inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username=? AND Password=?", (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login", "Login successful")
            self.root.destroy()  
            self.open_menu() 
        else:
            messagebox.showerror("Login", "Invalid username or password")

    def open_menu(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        menu_path = os.path.join(current_dir, 'Menu.py')
        
        if not os.path.exists(menu_path):
            menu_path = os.path.join(os.path.dirname(current_dir), 'Menu.py')
        
        if os.path.exists(menu_path):
             threading.Thread(target=self.run_menu_script, args=(menu_path,), daemon=True).start()
        else:
            messagebox.showerror("Error", f"Cannot find Menu.py. Looked in:\n{os.path.dirname(menu_path)}")

    def run_menu_script(self, menu_path):
        try:
            subprocess.Popen([sys.executable, menu_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Menu.py: {e}")

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        email = self.reg_email_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = sqlite3.connect('db/inventory.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Users (Username, Password, Email) VALUES (?, ?, ?)", 
                           (username, hashed_password, email))
            conn.commit()
            messagebox.showinfo("Registration", "Registration successful!")
            self.show_login_widgets()
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration Error", "Username already exists. Please choose a different username.")
        finally:
            conn.close()

    def reset_password(self):
        email = self.forgot_email_entry.get()
        new_password = self.generate_random_password()
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        conn = sqlite3.connect('db/inventory.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Users SET Password=? WHERE Email=?", (hashed_password, email))
        if cursor.rowcount > 0:
            conn.commit()
            messagebox.showinfo("Forgot Password", f"Your new password is: {new_password}")
            self.show_login_widgets()
        else:
            messagebox.showerror("Forgot Password", "Email not found")
        conn.close()

    def generate_random_password(self, length=12):
        import random
        import string
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

    def create_footer(self):
        self.footer_frame = tk.Frame(self.root, bg="light blue")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.title_label = tk.Label(self.footer_frame, text="©2024 Inventory Management System. All rights reserved.", fg="black", bg="light grey", font=("Arial", 10))
        self.title_label.pack(pady=2)
        self.developer_info = tk.Label(self.footer_frame, text="Developed by Tondwani Craig", bg="light grey", font=("Arial", 10))
        self.developer_info.pack(pady=2)

            
if __name__ == "__main__":
    root = tk.Tk()
    login_manager = LoginManager(root)
    root.mainloop()