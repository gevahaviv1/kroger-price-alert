from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class PriceAlertResult(db.Model):
    __tablename__ = 'price_alert_results'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    triggered = db.Column(db.Boolean, default=False)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    brand = db.Column(db.String)
    category = db.Column(db.String)
    image_url = db.Column(db.String)
    product_url = db.Column(db.String)
    regular_price = db.Column(db.Float)
    promo_price = db.Column(db.Float)
    fulfillment = db.Column(db.JSON)
    stock_level = db.Column(db.String)
    size = db.Column(db.String)
    sold_by = db.Column(db.String)
    location = db.Column(db.JSON)
    dimensions = db.Column(db.JSON)
    temperature_sensitive = db.Column(db.Boolean)
