from db.models import db, PriceAlertResult
from trigger_alert_logic.alert_checker import should_trigger_alert
from app import create_app

# Initialize Flask app (needed for DB access)
app = create_app()

# Sample products (normally you would pull from API or DB)
sample_products = [
    {
        "id": "0001",
        "price": {
            "promo": 1.59
        }
    },
    {
        "id": "0002",
        "price": {
            "promo": 2.50
        }
    },
    {
        "id": "0003",
        "price": {
            "promo": 0.99
        }
    }
]

# Sample user thresholds (user's max desired price per product)
sample_user_thresholds = {
    "0001": 1.80,  # Alert expected (1.59 < 1.80)
    "0002": 1.80,  # No alert (2.50 > 1.80)
    "0003": 1.00   # Alert expected (0.99 < 1.00)
}

# Hardcoded user ID for now
user_id = "batch_user"

with app.app_context():
    for product in sample_products:
        product_id = product["id"]
        triggered = should_trigger_alert(product, sample_user_thresholds)

        # Save the result to DB
        result = PriceAlertResult(
            product_id=product_id,
            user_id=user_id,
            triggered=triggered
        )
        db.session.add(result)

    db.session.commit()
    print("✅ Batch alert check completed and results saved to DB!")
