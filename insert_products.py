from db.models import db, Product
from app import create_app

app = create_app()

with app.app_context():
    products = [
        Product(
            id="0001",
            name="Milk 2%",
            brand="Kroger",
            category="Dairy",
            image_url="https://example.com/milk.jpg",
            product_url="https://www.kroger.com/p/milk/0001",
            regular_price=2.00,
            promo_price=1.50,
            fulfillment={"curbside": True, "delivery": True, "instore": True, "shiptohome": False},
            stock_level="HIGH",
            size="1 gal",
            sold_by="unit",
            location={"aisle": "12", "shelf": "2", "bay": "5", "side": "L"},
            dimensions={"width": 4.5, "height": 2.0, "depth": 3.2},
            temperature_sensitive=True
        ),
        # Add more products similarly
    ]

    db.session.bulk_save_objects(products)
    db.session.commit()

    print("✅ Products inserted into DB (new format)")
