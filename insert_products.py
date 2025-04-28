from db.models import db, Product
from app import create_app

app = create_app()

with app.app_context():
    products = [
        Product(id="0001", promo_price=1.59),
        Product(id="0002", promo_price=2.50),
        Product(id="0003", promo_price=0.99)
    ]

    db.session.bulk_save_objects(products)
    db.session.commit()

    print("✅ Products inserted into DB")
