from database import SessionLocal, engine, Base
import models
from models import Product, Store

PRODUCTS = [
    # name, category, price, stock
    ("Phone Pro 256GB", "Phones", 999.00, 25),
    ("Phone Standard 128GB", "Phones", 699.00, 40),
    ("Phone Mini 128GB", "Phones", 549.00, 3),
    ("Phone Case Clear", "Accessories", 29.00, 100),
    ("Phone Case Leather", "Accessories", 49.00, 60),
    ("Wireless Charger", "Accessories", 39.00, 0),
    ("USB-C Cable 1m", "Accessories", 19.00, 200),
    ("Laptop Air 13", "Laptops", 1099.00, 15),
    ("Laptop Pro 14", "Laptops", 1999.00, 8),
    ("Laptop Pro 16", "Laptops", 2499.00, 1),
    ("Tablet 10.9", "Tablets", 449.00, 30),
    ("Tablet Pro 12.9", "Tablets", 1099.00, 12),
    ("Wireless Earbuds", "Audio", 129.00, 75),
    ("Over-Ear Headphones", "Audio", 349.00, 20),
    ("Smart Watch 41mm", "Wearables", 399.00, 18),
    ("Smart Watch Ultra", "Wearables", 799.00, 0),
]

STORES = [
    ("StoreQ Indiranagar", "Bengaluru"),
    ("StoreQ Koramangala", "Bengaluru"),
    ("StoreQ Phoenix Mall", "Mumbai"),
]


def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.query(Product).count() > 0:
            print("Already seeded, skipping.")
            return
        for name, category, price, stock in PRODUCTS:
            db.add(Product(name=name, category=category,
                           price=price, stock=stock))
        for name, city in STORES:
            db.add(Store(name=name, city=city))
        db.commit()
        print(f"Seeded {len(PRODUCTS)} products and {len(STORES)} stores.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()