import json
from datetime import datetime
import matplotlib.pyplot as plt
import tabulate
from termcolor import colored
from enum import Enum, auto
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class Action(Enum):
    DISPLAY_PRODUCTS = auto()
    ADD_PRODUCT = auto()
    UPDATE_PRODUCT_QUANTITY = auto()
    SELL_PRODUCT = auto()
    VIEW_TRANSACTION_LOG = auto()
    SAVE_PRODUCTS_JSON = auto()
    GENERATE_QUANTITY_CHART = auto()
    SAVE_AND_EXIT = auto()

class Constants:
    PRODUCTS_FILE = 'products.json'
    TRANSACTIONS_LOG_FILE = 'transactions.log'

class Product:
    def __init__(self, product_id, name, price, quantity, category):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.category = category

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'category': self.category
        }

class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Supermarket Management System")
        self.root.geometry("800x400")  # Double the width

        self.products = []
        self.load_products()

        self.create_gui()

    def load_products(self):
        try:
            with open(Constants.PRODUCTS_FILE, 'r') as file:
                product_data = json.load(file)
                self.products = [Product(**data) for data in product_data]
            print("Data loaded from JSON.")
        except FileNotFoundError:
            print("No existing JSON data. Starting with an empty inventory.")

    def save_products(self):
        with open(Constants.PRODUCTS_FILE, 'w') as file:
            product_data = [product.to_dict() for product in self.products]
            json.dump(product_data, file, indent=2)
        print("Data saved in JSON format.")

    def display_products(self):
        headers = ["ID", "Name", "Price", "Quantity", "Category"]
        data = [[product.product_id, product.name, product.price, product.quantity, product.category] for product in self.products]
        table = tabulate.tabulate(data, headers=headers, tablefmt="fancy_grid")
        messagebox.showinfo("Display Products", colored(table, 'cyan'))

    def add_product(self):
        add_product_window = tk.Toplevel(self.root)
        add_product_window.title("Add Product")

        name_label = ttk.Label(add_product_window, text="Product Name:")
        name_label.grid(row=0, column=0, padx=10, pady=10)
        name_entry = ttk.Entry(add_product_window)
        name_entry.grid(row=0, column=1, padx=10, pady=10)

        price_label = ttk.Label(add_product_window, text="Product Price:")
        price_label.grid(row=1, column=0, padx=10, pady=10)
        price_entry = ttk.Entry(add_product_window)
        price_entry.grid(row=1, column=1, padx=10, pady=10)

        quantity_label = ttk.Label(add_product_window, text="Product Quantity:")
        quantity_label.grid(row=2, column=0, padx=10, pady=10)
        quantity_entry = ttk.Entry(add_product_window)
        quantity_entry.grid(row=2, column=1, padx=10, pady=10)

        category_label = ttk.Label(add_product_window, text="Product Category:")
        category_label.grid(row=3, column=0, padx=10, pady=10)
        category_entry = ttk.Combobox(add_product_window, values=list(set(product.category for product in self.products)))
        category_entry.grid(row=3, column=1, padx=10, pady=10)
        category_entry.set("Select Category")

        add_button = ttk.Button(add_product_window, text="Add Product", command=lambda: self.add_product_command(
            name_entry.get(),
            price_entry.get(),
            quantity_entry.get(),
            category_entry.get(),
            add_product_window
        ))
        add_button.grid(row=4, column=0, columnspan=2, pady=10)

    def add_product_command(self, name, price, quantity, category, add_product_window):
        try:
            price = float(price)
            quantity = int(quantity)
            product_id = len(self.products) + 1
            product = Product(product_id, name, price, quantity, category)
            self.products.append(product)
            print(colored(f"Product '{name}' added successfully.", 'green'))
            add_product_window.destroy()
        except ValueError:
            print(colored("Invalid input. Please enter valid values.", 'red'))

    def update_product_quantity(self):
        update_product_window = tk.Toplevel(self.root)
        update_product_window.title("Update Product Quantity")

        product_id_label = ttk.Label(update_product_window, text="Product ID:")
        product_id_label.grid(row=0, column=0, padx=10, pady=10)
        product_id_entry = ttk.Combobox(update_product_window, values=[str(product.product_id) for product in self.products])
        product_id_entry.grid(row=0, column=1, padx=10, pady=10)
        product_id_entry.set("Select Product ID")

        quantity_label = ttk.Label(update_product_window, text="New Quantity:")
        quantity_label.grid(row=1, column=0, padx=10, pady=10)
        quantity_entry = ttk.Entry(update_product_window)
        quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        update_button = ttk.Button(update_product_window, text="Update Quantity", command=lambda: self.update_product_quantity_command(
            product_id_entry.get(),
            quantity_entry.get(),
            update_product_window
        ))
        update_button.grid(row=2, column=0, columnspan=2, pady=10)

    def update_product_quantity_command(self, product_id, new_quantity, update_product_window):
        try:
            product_id = int(product_id)
            new_quantity = int(new_quantity)
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

        product_id_label = ttk.Label(sell_product_window, text="Product ID:")
        product_id_label.grid(row=0, column=0, padx=10, pady=10)
        product_id_entry = ttk.Combobox(sell_product_window, values=[str(product.product_id) for product in self.products])
        product_id_entry.grid(row=0, column=1, padx=10, pady=10)
        product_id_entry.set("Select Product ID")

        quantity_label = ttk.Label(sell_product_window, text="Quantity to Sell:")
        quantity_label.grid(row=1, column=0, padx=10, pady=10)
        quantity_entry = ttk.Entry(sell_product_window)
        quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        sell_button = ttk.Button(sell_product_window, text="Sell Product", command=lambda: self.sell_product_command(
            product_id_entry.get(),
            quantity_entry.get(),
            sell_product_window
        ))
        sell_button.grid(row=2, column=0, columnspan=2, pady=10)

    def sell_product_command(self, product_id, quantity, sell_product_window):
        try:
            product_id = int(product_id)
            quantity = int(quantity)
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
        return next((product for product in self.products if product.product_id == product_id), None)

    def log_transaction(self, product, quantity):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(Constants.TRANSACTIONS_LOG_FILE, 'a') as file:
            file.write(f"{timestamp} - Sold {quantity} units of '{product.name}' for ${quantity * product.price}\n")

    def generate_quantity_chart(self):
        categories = set(product.category for product in self.products)
        colors = ['blue', 'green', 'yellow', 'orange', 'red', 'purple', 'brown']
        category_colors = dict(zip(categories, colors[:len(categories)]))

        for category in categories:
            product_names = [product.name for product in self.products if product.category == category]
            quantities = [product.quantity for product in self.products if product.category == category]

            plt.bar(product_names, quantities, color=category_colors[category])
            plt.xlabel('Product Names')
            plt.ylabel('Quantity')
            plt.title(f'Product Quantity Chart - Category: {category}')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()

    def create_gui(self):
        ttk.Button(self.root, text="Display Products", command=self.display_products).pack(pady=10)
        ttk.Button(self.root, text="Add Product", command=self.add_product).pack(pady=10)
        ttk.Button(self.root, text="Update Product Quantity", command=self.update_product_quantity).pack(pady=10)
        ttk.Button(self.root, text="Sell Product", command=self.sell_product).pack(pady=10)
        ttk.Button(self.root, text="View Transaction Log", command=self.view_transaction_log).pack(pady=10)
        ttk.Button(self.root, text="Save Products (JSON)", command=self.save_products).pack(pady=10)
        ttk.Button(self.root, text="Generate Quantity Chart", command=self.generate_quantity_chart).pack(pady=10)
        ttk.Button(self.root, text="Save and Exit", command=self.save_and_exit).pack(pady=10)

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
