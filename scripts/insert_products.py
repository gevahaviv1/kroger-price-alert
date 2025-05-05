#!/usr/bin/env python3
import os
import sys
import json
from db.models import db, Product
from map_kroger_data.mapper import map_kroger_to_zenday
from app import create_app

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def upsert_products(data_list):
    """
    Upsert mapped products into the DB.
    If a product ID already exists, update its fields.
    """
    for raw in data_list:
        mapped = map_kroger_to_zenday(raw)
        prod = Product.query.get(mapped['id'])
        if prod:
            # Update existing
            prod.name = mapped['name']
            prod.brand = mapped['brand']
            prod.category = mapped['category']
            prod.image_url = mapped['image_url']
            prod.product_url = mapped['product_url']
            prod.regular_price = mapped['price']['regular']
            prod.promo_price   = mapped['price']['promo']
            prod.fulfillment   = mapped['fulfillment']
            prod.stock_level   = mapped['stock_level']
            prod.size          = mapped['size']
            prod.sold_by       = mapped['sold_by']
            prod.location      = mapped['location']
            prod.dimensions    = mapped['dimensions']
            prod.temperature_sensitive = mapped['temperature_sensitive']
        else:
            # Insert new
            prod = Product(
                id=mapped['id'],
                name=mapped['name'],
                brand=mapped['brand'],
                category=mapped['category'],
                image_url=mapped['image_url'],
                product_url=mapped['product_url'],
                regular_price=mapped['price']['regular'],
                promo_price=mapped['price']['promo'],
                fulfillment=mapped['fulfillment'],
                stock_level=mapped['stock_level'],
                size=mapped['size'],
                sold_by=mapped['sold_by'],
                location=mapped['location'],
                dimensions=mapped['dimensions'],
                temperature_sensitive=mapped['temperature_sensitive']
            )
            db.session.add(prod)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python insert_products.py <kroger_output.json>")
        sys.exit(1)

    json_path = sys.argv[1]
    if not os.path.isfile(json_path):
        print(f"❌ File not found: {json_path}")
        sys.exit(1)

    app = create_app()
    with app.app_context():
        raw_data = load_json(json_path)
        # raw_data may be either a list of items or wrap under 'data'
        items = raw_data.get('data') if isinstance(raw_data, dict) and 'data' in raw_data else raw_data
        upsert_products(items)
        db.session.commit()
        print(f"✅ Upserted {len(items)} products from {json_path}")

