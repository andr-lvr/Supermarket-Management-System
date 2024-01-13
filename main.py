import json
from datetime import datetime
import matplotlib.pyplot as plt
import tabulate
from termcolor import colored
import tkinter as tk
from tkinter import ttk, messagebox
from enum import Enum, auto

class Action(Enum):
    DISPLAY_PRODUCTS, ADD_PRODUCT, UPDATE_PRODUCT_QUANTITY, SELL_PRODUCT, VIEW_TRANSACTION_LOG, \
    SAVE_PRODUCTS_JSON, GENERATE_QUANTITY_CHART, SAVE_AND_EXIT = auto(), auto(), auto(), auto(), auto(), auto(), auto(), auto()

class Constants:
    PRODUCTS_FILE = 'products.json'
    TRANSACTIONS_LOG_FILE = 'transactions.log'

class Product:
    def __init__(self, product_id, name, price, quantity, category):
        self.product_id, self.name, self.price, self.quantity, self.category = product_id, name, price, quantity, category

    def to_dict(self):
        return {'product_id': self.product_id, 'name': self.name, 'price': self.price, 'quantity': self.quantity, 'category': self.category}

class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Supermarket Management System")
        self.root.geometry("800x400")
        self.products = []
        self.load_products()
        self.create_gui()

    def load_products(self):
        try:
            with open(Constants.PRODUCTS_FILE, 'r') as file:
                self.products = [Product(**data) for data in json.load(file)]
            print("Data loaded from JSON.")
        except FileNotFoundError:
            print("No existing JSON data. Starting with an empty inventory.")

    def save_products(self):
        with open(Constants.PRODUCTS_FILE, 'w') as file:
            json.dump([product.to_dict() for product in self.products], file, indent=2)
        print("Data saved in JSON format.")

    def display_products(self):
        headers = ["ID", "Name", "Price", "Quantity", "Category"]
        data = [[p.product_id, p.name, p.price, p.quantity, p.category] for p in self.products]
        table = tabulate.tabulate(data, headers=headers, tablefmt="fancy_grid")
        messagebox.showinfo("Display Products", colored(table, 'cyan'))

    def add_product(self):
        add_product_window = tk.Toplevel(self.root)
        add_product_window.title("Add Product")
        entries = [ttk.Entry(add_product_window) for _ in range(4)]
        labels = ["Product Name:", "Product Price:", "Product Quantity:", "Product Category:"]
        for i, (label, entry) in enumerate(zip(labels, entries)):
            ttk.Label(add_product_window, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry.grid(row=i, column=1, padx=10, pady=10)
        category_entry = entries[-1]
        category_entry['values'] = list(set(product.category for product in self.products))
        category_entry.set("Select Category")
        ttk.Button(add_product_window, text="Add Product", command=lambda: self.add_product_command(*[e.get() for e in entries], add_product_window)).grid(row=len(entries), column=0, columnspan=2, pady=10)

    def add_product_command(self, name, price, quantity, category, add_product_window):
        try:
            price, quantity = float(price), int(quantity)
            product_id = len(self.products) + 1
            self.products.append(Product(product_id, name, price, quantity, category))
            print(colored(f"Product '{name}' added successfully.", 'green'))
            add_product_window.destroy()
        except ValueError:
            print(colored("Invalid input. Please enter valid values.", 'red'))

    def update_product_quantity(self):
        update_product_window = tk.Toplevel(self.root)
        update_product_window.title("Update Product Quantity")
        product_id_entry = ttk.Combobox(update_product_window, values=[str(p.product_id) for p in self.products])
        quantity_entry = ttk.Entry(update_product_window)
        for i, (label, entry) in enumerate([("Product ID:", product_id_entry), ("New Quantity:", quantity_entry)]):
            ttk.Label(update_product_window, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry.grid(row=i, column=1, padx=10, pady=10)
        ttk.Button(update_product_window, text="Update Quantity", command=lambda: self.update_product_quantity_command(product_id_entry.get(), quantity_entry.get(), update_product_window)).grid(row=2, column=0, columnspan=2, pady=10)

    def update_product_quantity_command(self, product_id, new_quantity, update_product_window):
        try:
            product_id, new_quantity = int(product_id), int(new_quantity)
            product = self.find_product_by_id(product_id)
            if product:
                product.quantity = new_quantity
                print(colored(f"Quantity for product '{product.name}' updated to {new_quantity}.", 'yellow'))
                update_product_window.destroy()
            else:
                print(colored(f"Product with ID {product_id} not found.", 'red'))
        except ValueError:
            print(colored("Invalid input. Please enter valid values.", 'red'))

    def sell_product(self):
        sell_product_window = tk.Toplevel(self.root)
        sell_product_window.title("Sell Product")
        product_id_entry = ttk.Combobox(sell_product_window, values=[str(p.product_id) for p in self.products])
        quantity_entry = ttk.Entry(sell_product_window)
        for i, (label, entry) in enumerate([("Product ID:", product_id_entry), ("Quantity to Sell:", quantity_entry)]):
            ttk.Label(sell_product_window, text=label).grid(row=i, column=0, padx=10, pady=10)
            entry.grid(row=i, column=1, padx=10, pady=10)
        ttk.Button(sell_product_window, text="Sell Product", command=lambda: self.sell_product_command(product_id_entry.get(), quantity_entry.get(), sell_product_window)).grid(row=2, column=0, columnspan=2, pady=10)

    def sell_product_command(self, product_id, quantity, sell_product_window):
        try:
            product_id, quantity = int(product_id), int(quantity)
            product = self.find_product_by_id(product_id)
            if product:
                if product.quantity >= quantity:
                    product.quantity -= quantity
                    print(colored(f"Sold {quantity} units of '{product.name}'.", 'green'))
                    self.log_transaction(product, quantity)
                    sell_product_window.destroy()
                else:
                    print(colored(f"Insufficient quantity for product '{product.name}'.", 'red'))
            else:
                print(colored(f"Product with ID {product_id} not found.", 'red'))
        except ValueError:
            print(colored("Invalid input. Please enter valid values.", 'red'))

    def find_product_by_id(self, product_id):
        return next((p for p in self.products if p.product_id == product_id), None)

    def log_transaction(self, product, quantity):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(Constants.TRANSACTIONS_LOG_FILE, 'a') as file:
            file.write(f"{timestamp} - Sold {quantity} units of '{product.name}' for ${quantity * product.price}\n")

    def generate_quantity_chart(self):
        categories, colors = set(p.category for p in self.products), ['blue', 'green', 'yellow', 'orange', 'red', 'purple', 'brown']
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
            ("View Transaction Log", self.view_transaction_log),
            ("Save Products (JSON)", self.save_products),
            ("Generate Quantity Chart", self.generate_quantity_chart),
            ("Save and Exit", self.save_and_exit)
        ]
        for text, command in buttons:
            ttk.Button(self.root, text=text, command=command).pack(pady=10)

    def view_transaction_log(self):
        with open(Constants.TRANSACTIONS_LOG_FILE, 'r') as file:
            messagebox.showinfo("Transaction Log", colored("Transaction Log:", 'cyan') + "\n" + file.read())

    def save_and_exit(self):
        self.save_products()
        print(colored("Data saved. Exiting.", 'green'))
        self.root.destroy()

def main():
    root = tk.Tk()
    app = InventoryManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
