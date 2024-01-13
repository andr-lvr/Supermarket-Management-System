import json  # Library for working with JSON data
from datetime import datetime  # Library for working with date and time
import sqlite3  # Library for working with SQLite database
import matplotlib.pyplot as plt  # Library for creating plots and charts
import tabulate  # Library for creating text-based tables
from termcolor import colored  # Library for adding colored text to console output
import tkinter as tk  # Standard GUI library for creating desktop applications
from tkinter import ttk, messagebox  # Additional modules from tkinter for GUI components
from enum import Enum, auto  # Enumerations and automatic value assignment for actions


class Action(Enum):
    DISPLAY_PRODUCTS, ADD_PRODUCT, UPDATE_PRODUCT_QUANTITY, SELL_PRODUCT, VIEW_TRANSACTION_LOG, \
        SAVE_PRODUCTS_JSON, GENERATE_QUANTITY_CHART, SAVE_AND_EXIT = auto(), auto(), auto(), auto(), auto(), auto(), auto(), auto()


class Constants:
    PRODUCTS_FILE = 'products.json'
    TRANSACTIONS_LOG_FILE = 'transactions.log'
    DATABASE_FILE = 'inventory.db'


class Product:
    def __init__(self, product_id, name, price, quantity, category):
        self.product_id, self.name, self.price, self.quantity, self.category = product_id, name, price, quantity, category

    def to_dict(self):
        return {'product_id': self.product_id, 'name': self.name, 'price': self.price, 'quantity': self.quantity,
                'category': self.category}


def log_transaction(product, quantity):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(Constants.TRANSACTIONS_LOG_FILE, 'a') as file:
        file.write(f"{timestamp} - Sold {quantity} units of '{product.name}' for ${quantity * product.price}\n")


def view_transaction_log():
    with open(Constants.TRANSACTIONS_LOG_FILE, 'r') as file:
        messagebox.showinfo("Transaction Log", colored("Transaction Log:", 'cyan') + "\n" + file.read())


def create_database():
    with sqlite3.connect(Constants.DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                quantity INTEGER,
                category TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY,
                product_id INTEGER,
                quantity INTEGER,
                timestamp TEXT,
                FOREIGN KEY(product_id) REFERENCES products(product_id)
            )
        ''')


def save_transactions(transactions):
    with sqlite3.connect(Constants.DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO transactions (product_id, quantity, timestamp)
            VALUES (?, ?, ?)
        ''', transactions)


def sort_transactions(key):
    with sqlite3.connect(Constants.DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM transactions ORDER BY {key}')
        transactions = cursor.fetchall()
        return transactions


def add_product_command(name, price, quantity, category, add_product_window):
    try:
        price, quantity = float(price), int(quantity)
        with sqlite3.connect(Constants.DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, price, quantity, category)
                VALUES (?, ?, ?, ?)
            ''', (name, price, quantity, category))
        print(colored(f"Product '{name}' added successfully.", 'green'))
        add_product_window.destroy()
    except (ValueError, sqlite3.Error) as e:
        print(colored(f"Error adding product: {e}", 'red'))


class InventoryManager:
    def __init__(self, root):
        self.root, self.products = root, []
        self.root.title("Supermarket Management System")
        self.root.geometry("300x600")
        create_database()
        self.load_products()
        self.create_gui()

    def load_products(self):
        try:
            with sqlite3.connect(Constants.DATABASE_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products')
                data = cursor.fetchall()
                self.products = [Product(*row) for row in data]
            print("Data loaded from the database.")
        except sqlite3.Error:
            print("Error loading data from the database. Starting with an empty inventory.")

    def save_products(self):
        with sqlite3.connect(Constants.DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM products')
            cursor.executemany('''
                INSERT INTO products (product_id, name, price, quantity, category)
                VALUES (?, ?, ?, ?, ?)
            ''', [(p.product_id, p.name, p.price, p.quantity, p.category) for p in self.products])
        print("Data saved in the database.")

    def sort_products(self, key):
        self.products.sort(key=lambda p: getattr(p, key))
        self.display_products()

    @staticmethod
    def display_sorted_transactions(key):
        transactions = sort_transactions(key)
        headers = ["Transaction ID", "Product ID", "Quantity", "Timestamp"]
        data = [(t[0], t[1], t[2], t[3]) for t in transactions]
        table = tabulate.tabulate(data, headers=headers, tablefmt="fancy_grid")
        messagebox.showinfo("Sorted Transactions", colored(table, 'cyan'))

    def display_products(self):
        headers = ["ID", "Name", "Price", "Quantity", "Category"]
        data = [[p.product_id, p.name, p.price, p.quantity, p.category] for p in self.products]
        table = tabulate.tabulate(data, headers=headers, tablefmt="fancy_grid")
        messagebox.showinfo("Display Products", colored(table, 'cyan'))

    def add_product(self):
        self.create_input_window("Add Product",
                                 ["Product Name:", "Product Price:", "Product Quantity:",
                                  "Product Category:"], add_product_command)

    def update_product_quantity(self):
        self.create_input_window("Update Product Quantity", ["Product ID:", "New Quantity:"],
                                 self.update_product_quantity_command)

    def update_product_quantity_command(self, product_id, new_quantity, update_product_window):
        try:
            product_id, new_quantity = int(product_id), int(new_quantity)
            product = next((p for p in self.products if p.product_id == product_id), None)
            if product:
                product.quantity = new_quantity
                print(colored(f"Quantity for product '{product.name}' updated to {new_quantity}.", 'yellow'))
                update_product_window.destroy()
            else:
                print(colored(f"Product with ID {product_id} not found.", 'red'))
        except ValueError:
            print(colored("Invalid input. Please enter valid values.", 'red'))

    def sell_product(self):
        self.create_input_window("Sell Product", ["Product ID:", "Quantity to Sell:"],
                                 self.sell_product_command)

    def sell_product_command(self, product_id, quantity, sell_product_window):
        try:
            product_id, quantity = int(product_id), int(quantity)
            product = next((p for p in self.products if p.product_id == product_id), None)
            if product:
                if product.quantity >= quantity:
                    product.quantity -= quantity
                    print(colored(f"Sold {quantity} units of '{product.name}'.", 'green'))
                    log_transaction(product, quantity)
                    sell_product_window.destroy()
                else:
                    print(colored(f"Insufficient quantity for product '{product.name}'.", 'red'))
            else:
                print(colored(f"Product with ID {product_id} not found.", 'red'))
        except ValueError:
            print(colored("Invalid input. Please enter valid values.", 'red'))

    def create_input_window(self, title, labels, command):
        input_window = tk.Toplevel(self.root)
        input_window.title(title)
        entries = [ttk.Entry(input_window) for _ in range(len(labels))]
        for i, (label, entry) in enumerate(zip(labels, entries)):
            ttk.Label(input_window, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry.grid(row=i, column=1, padx=10, pady=10)
        ttk.Button(input_window, text=title, command=lambda: command(*[e.get() for e in entries], input_window)).grid(
            row=len(entries), column=0, columnspan=2, pady=10)
        return input_window

    def find_product_by_id(self, product_id):
        return next((p for p in self.products if p.product_id == product_id), None)

    def generate_quantity_chart(self):
        categories, colors = set(p.category for p in self.products), ['blue', 'green', 'yellow', 'orange', 'red',
                                                                      'purple', 'brown']
        category_colors = dict(zip(categories, colors[:len(categories)]))
        for category in categories:
            product_data = [(p.name, p.quantity) for p in self.products if p.category == category]
            product_names, quantities = zip(*product_data)
            plt.bar(product_names, quantities, color=category_colors[category])
            plt.xlabel('Product Names')
            plt.ylabel('Quantity')
            plt.title(f'Product Quantity Chart - Category: {category}')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()

    def create_gui(self):
        buttons = [
            ("Display Products", self.display_products),
            ("Add Product", self.add_product),
            ("Update Product Quantity", self.update_product_quantity),
            ("Sell Product", self.sell_product),
            ("View Transaction Log", view_transaction_log),
            ("Save Products (JSON)", self.save_products),
            ("Generate Quantity Chart", self.generate_quantity_chart),
            ("Save and Exit", self.save_and_exit),
            ("Sort Transactions (By Timestamp)", lambda: self.display_sorted_transactions('timestamp')),
            ("Sort Transactions (By Quantity)", lambda: self.display_sorted_transactions('quantity')),
            ("Sort Products (By Name)", lambda: self.sort_products('name')),
            ("Sort Products (By Price)", lambda: self.sort_products('price')),
        ]
        for text, command in buttons:
            ttk.Button(self.root, text=text, command=command).pack(pady=10)

    def save_and_exit(self):
        self.save_products()
        print(colored("Data saved. Exiting.", 'green'))
        self.root.destroy()


def main():
    root = tk.Tk()
    InventoryManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
