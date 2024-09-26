import sqlite3

def initialize_db():
    conn = sqlite3.connect('db/inventory.db')
    cursor = conn.cursor()
    

    cursor.execute('''CREATE TABLE IF NOT EXISTS Suppliers (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT NOT NULL,
                        ContactPerson TEXT,  -- Added column
                        PhoneNumber TEXT,
                        Description TEXT)''')

    # Other table definitions remain unchanged
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Username TEXT UNIQUE NOT NULL,
                        Password TEXT NOT NULL,
                        Email TEXT UNIQUE NOT NULL)''')
                       
    cursor.execute('''CREATE TABLE IF NOT EXISTS Employees (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT NOT NULL,
                        Position TEXT,
                        ContactInfo TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Categories (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Products (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Name TEXT NOT NULL,
                        CategoryID INTEGER,
                        SupplierID INTEGER,
                        Price REAL,
                        Quantity INTEGER,
                        FOREIGN KEY (CategoryID) REFERENCES Categories(ID),
                        FOREIGN KEY (SupplierID) REFERENCES Suppliers(ID))''')

    # Drop the Sales table if it exists
    cursor.execute('DROP TABLE IF EXISTS Sales')

    # Recreate the Sales table with the corrected schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS Sales (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ProductID INTEGER,
                        EmployeeID INTEGER,
                        Quantity INTEGER,
                        SaleDate TEXT,
                        FOREIGN KEY (ProductID) REFERENCES Products(ID),
                        FOREIGN KEY (EmployeeID) REFERENCES Employees(ID))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Billing (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        SaleID INTEGER,
                        TotalAmount REAL,
                        FOREIGN KEY (SaleID) REFERENCES Sales(ID))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Invoices (
                        InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
                        CustomerName TEXT NOT NULL,
                        CustomerContact TEXT NOT NULL,
                        CompanyName TEXT NOT NULL,
                        Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS InvoiceItems (
                        InvoiceItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                        InvoiceID INTEGER,
                        ProductID INTEGER,
                        Quantity INTEGER,
                        Price REAL,
                        Total REAL,
                        FOREIGN KEY (InvoiceID) REFERENCES Invoices (InvoiceID),
                        FOREIGN KEY (ProductID) REFERENCES Products (ID))''')

    conn.commit()
    conn.close()

initialize_db()
