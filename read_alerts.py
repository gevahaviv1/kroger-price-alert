from db.models import db, PriceAlertResult
from app import create_app

# Initialize Flask app (for DB access)
app = create_app()

with app.app_context():
    results = PriceAlertResult.query.order_by(PriceAlertResult.checked_at.desc()).all()

    if not results:
        print("No alert checks found.")
    else:
        for result in results:
            print(f"ID: {result.id}")
            print(f"Product ID: {result.product_id}")
            print(f"User ID: {result.user_id}")
            print(f"Triggered: {'✅ YES' if result.triggered else '❌ NO'}")
            print(f"Checked At: {result.checked_at}")
            print("-" * 40)
