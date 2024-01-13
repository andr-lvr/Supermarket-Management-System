import json
from datetime import datetime
import matplotlib.pyplot as plt
import tabulate
from termcolor import colored
from enum import Enum, auto

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
    def __init__(self):
        self.products = []

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
        print(colored(table, 'cyan'))

    def add_product(self):
        name = input("Enter product name: ")
        price = self.get_float_input("Enter product price: ")
        quantity = self.get_int_input("Enter product quantity: ")
        category = input("Enter product category: ")
        product_id = len(self.products) + 1
        product = Product(product_id, name, price, quantity, category)
        self.products.append(product)
        print(colored(f"Product '{name}' added successfully.", 'green'))

    def update_product_quantity(self):
        product_id = self.get_int_input("Enter product ID: ")
        new_quantity = self.get_int_input("Enter new quantity: ")
        product = self.find_product_by_id(product_id)
        if product:
            product.quantity = new_quantity
            print(colored(f"Quantity for product '{product.name}' updated to {new_quantity}.", 'yellow'))
        else:
            print(colored(f"Product with ID {product_id} not found.", 'red'))

    def sell_product(self):
        product_id = self.get_int_input("Enter product ID: ")
        quantity = self.get_int_input("Enter quantity to sell: ")
        product = self.find_product_by_id(product_id)
        if product:
            if product.quantity >= quantity:
                product.quantity -= quantity
                print(colored(f"Sold {quantity} units of '{product.name}'.", 'green'))
                self.log_transaction(product, quantity)
            else:
                print(colored(f"Insufficient quantity for product '{product.name}'.", 'red'))
        else:
            print(colored(f"Product with ID {product_id} not found.", 'red'))

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

    def display_invalid_choice(self):
        print(colored("Invalid choice. Please enter a number between 1 and 8.", 'red'))

    @staticmethod
    def get_int_input(prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print(colored("Invalid input. Please enter a valid integer.", 'red'))

    @staticmethod
    def get_float_input(prompt):
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print(colored("Invalid input. Please enter a valid floating-point number.", 'red'))

def handle_choice(choice, inventory_manager):
    try:
        action = Action(int(choice))
        switch = {
            Action.DISPLAY_PRODUCTS: inventory_manager.display_products,
            Action.ADD_PRODUCT: inventory_manager.add_product,
            Action.UPDATE_PRODUCT_QUANTITY: inventory_manager.update_product_quantity,
            Action.SELL_PRODUCT: inventory_manager.sell_product,
            Action.VIEW_TRANSACTION_LOG: lambda: print_transaction_log(),
            Action.SAVE_PRODUCTS_JSON: inventory_manager.save_products,
            Action.GENERATE_QUANTITY_CHART: inventory_manager.generate_quantity_chart,
            Action.SAVE_AND_EXIT: lambda: (inventory_manager.save_products(), print(colored("Data saved. Exiting.", 'green')), exit())
        }
        switch.get(action, inventory_manager.display_invalid_choice)()
    except ValueError:
        print(colored("Invalid input. Please enter a valid number.", 'red'))

def print_transaction_log():
    with open(Constants.TRANSACTIONS_LOG_FILE, 'r') as file:
        print(colored("Transaction Log:", 'cyan'), file.read())

def main():
    inventory_manager = InventoryManager()
    inventory_manager.load_products()

    while True:
        print(colored("\nSupermarket Management System", 'magenta'))
        print(colored("1. Display Products", 'cyan'))
        print(colored("2. Add Product", 'cyan'))
        print(colored("3. Update Product Quantity", 'cyan'))
        print(colored("4. Sell Product", 'cyan'))
        print(colored("5. View Transaction Log", 'cyan'))
        print(colored("6. Save Products (JSON)", 'cyan'))
        print(colored("7. Generate Quantity Chart", 'cyan'))
        print(colored("8. Save and Exit", 'cyan'))

        choice = input(colored("Enter your choice (1-8): ", 'yellow'))
        handle_choice(choice, inventory_manager)

if __name__ == "__main__":
    main()
