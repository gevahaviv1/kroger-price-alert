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

    id = db.Column(db.String, primary_key=True)  # Using productId from Kroger
    promo_price = db.Column(db.Float, nullable=False)
