import csv
import re

from collections import OrderedDict
from datetime import date

from peewee import *

db = SqliteDatabase("inventory.db")


class Product(Model):
    product_id = AutoField()
    product_name = CharField(max_length=255, unique=True)
    product_price = IntegerField(default=0)
    product_quantity = IntegerField(default=0)
    date_updated = DateField()

    class Meta:
        database = db


def fill_inventory():
    with open("store-inventory/inventory.csv", newline="") as file:
        fill = csv.DictReader(file)
        for i in fill:
            clean = clean_product(
                i["product_name"],
                i["product_price"],
                i["product_quantity"],
                i["date_updated"])

            add_to_inventory(
                clean["name"],
                clean["price"],
                clean["quantity"],
                clean["updated"])


def clean_product(name="", price="", quantity="", updated="01/01/01"):
    clean = {"name": name.strip(), "quantity": int(quantity)}
    price = price.replace("$", "").split(".")
    clean["price"] = int(price[0]) * 100 + int(price[1])
    update = updated.split("/")
    clean["updated"] = date(int(update[2]), int(update[0]), int(update[1]))
    return clean


def view_product():
    """View each product by ID"""

    while True:
        min_id = Product.select().order_by(Product.product_id.asc()).get().product_id
        max_id = Product.select().order_by(Product.product_id.desc()).get().product_id
        user_input = input("Please enter an ID or 'r' to return. ID ranges ({} - {}): ".format(min_id, max_id))
        if user_input.lower().strip() == "r":
            break
        else:
            try:
                prod = Product.select().where(Product.product_id == int(user_input)).get()
                print("\nID: {}\nName: {}".format(prod.product_id, prod.product_name))
                print("------" + "-" * len(prod.product_name))
                print("Price: {}\nQuantity: {}\nDate Updated: {}\n".format(prod.product_price, prod.product_quantity,
                                                                           prod.date_updated))
            except ValueError:
                print("Please enter a valid ID or 'r'.")
            except:
                print("The ID must be between {} and {}".format(min_id, max_id))


def add_product():
    """Add a product to the database"""

    new_product = input("Please add a new product: ")
    price = None
    while not price:
        price = re.match(r'^[$]\d+[.]+\d{2}$', input("Please enter a price (ex: $5.99): "))
        if price is None:
            print("Enter the price in the correct format please.")
        else:
            price = price.group()

    quantity = int(input("Please enter the quantity: "))
    if quantity > 0:
        pass
    else:
        raise ValueError("Please enter a valid number.")

    updated = date.today()

    clean = clean_product(new_product, price, quantity)
    add_to_inventory(clean["name"], clean["price"], clean["quantity"], updated)


def add_to_inventory(name="", price=0, quantity=0, updated="01-01-01"):
    try:
        Product.create(
            product_name=name,
            product_price=price,
            product_quantity=quantity,
            date_updated=updated)
    except IntegrityError:
        product_update = Product.select().where(Product.product_name == name).get().date_updated
        if product_update <= updated:
            upd = Product.update(
                product_price=price,
                product_quantity=quantity,
                date_updated=updated).where(Product.product_name == name)
            upd.execute()


def backup():
    """Backup the database"""
    with open("store-inventory/backup.csv", "w") as backups:
        stuff_to_backup = ["product_name", "product_price", "product_quantity", "date_updated"]
        write = csv.DictWriter(backups, fieldnames=stuff_to_backup)
        write.writeheader()
        for i in Product:
            write.writerow({
                "product_name": i.product_name, "product_price": i.product_price,
                "product_quantity": i.product_quantity,
                "date_updated": str(i.date_updated.month) + "/" + str(i.date_updated.day) + "/" + str(
                    i.date_updated.year)
            })
        print("Backup complete.")


def menu_loop():
    menu_input = None
    while menu_input != "q":
        print("Enter 'q' to quit.")
        for key, value in menu.items():
            print("{}) {}".format(key, value.__doc__))
        menu_input = input("Choose an option: \n").lower().strip()
        if menu_input in menu:
            menu[menu_input]()
        elif menu_input != "q":
            print("You must choose a valid option.")


menu = OrderedDict([
    ("a", add_product),
    ("b", backup),
    ("v", view_product)
])

if __name__ == '__main__':
    db.connect()
    db.create_tables([Product], safe=True)
    fill_inventory()
    menu_loop()
