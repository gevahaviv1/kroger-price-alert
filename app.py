from flask import Flask, request, jsonify
from db.models import db, PriceAlertResult, Product
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zenday.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return "Zenday Alert Service Running"

    @app.route('/trigger-alert', methods=['POST'])
    def trigger_alert():
        data = request.get_json() or {}
        product_data = data.get("product")
        if not product_data or not product_data.get("id"):
            return jsonify({"error": "Missing product data"}), 400

        pid     = product_data["id"]
        new_reg = product_data.get("price", {}).get("regular")
        new_pr  = product_data.get("price", {}).get("promo")

        # Try to load existing product
        existing = Product.query.get(pid)

        if existing:
            # If exists, compare old promo_price → new promo_price
            old_pr = existing.promo_price
            if old_pr is not None and new_pr is not None and old_pr > new_pr:
                # Price dropped → update and alert
                existing.regular_price = new_reg
                existing.promo_price   = new_pr
                db.session.commit()
                print(f"🔔 Price drop for {pid}: {old_pr} → {new_pr}")
                return jsonify({"alert": True, "old_price": old_pr, "new_price": new_pr}), 200

            # No drop → nothing to do
            return jsonify({"alert": False}), 200

        else:
            # Product doesn’t exist → create and alert
            new_p = Product(
                id=pid,
                name=product_data.get("name"),
                brand=product_data.get("brand"),
                category=product_data.get("category"),
                image_url=product_data.get("image_url"),
                product_url=product_data.get("product_url"),
                regular_price=new_reg,
                promo_price=new_pr,
                fulfillment=product_data.get("fulfillment"),
                stock_level=product_data.get("stock_level"),
                size=product_data.get("size"),
                sold_by=product_data.get("sold_by"),
                location=product_data.get("location"),
                dimensions=product_data.get("dimensions"),
                temperature_sensitive=product_data.get("temperature_sensitive")
            )
            db.session.add(new_p)
            db.session.commit()
            print(f"🔔 New product added: {pid} @ promo {new_pr}")
            return jsonify({"alert": True}), 201

    def batch_alert_check():
        with app.app_context():
            products = Product.query.all() # Need to set only for cart.

            try:
                for product in products:
                    # Fetch fresh data for this product.
                    # You need to implement this function to pull current prices
                    fresh = None # fetch_current_product(product.id)
                    new_reg = fresh["price"]["regular"]
                    new_pr  = fresh["price"]["promo"]

                    old_pr = product.promo_price or 0

                    # If price dropped, update & alert:
                    if new_pr is not None and new_pr < old_pr:
                        product.regular_price = new_reg
                        product.promo_price   = new_pr
                        db.session.add(product)
                        print(f"🔔 [Scheduler] Price drop for {product.id}: {old_pr} → {new_pr}")

                # Commit all updates at once
                db.session.commit()
                print("✅ [Scheduler] Batch alert check completed!")

            except Exception as e:
                db.session.rollback()
                print(f"❌ Error during batch alert check: {e}")

    # Initialize and start scheduler
    scheduler.add_job(func=batch_alert_check, trigger="interval", seconds=30)  # every 30 seconds

    return app

if __name__ == '__main__':
    app = create_app()

    # Only start the scheduler if this is the main process (not the reloader)
    from werkzeug.serving import is_running_from_reloader
    if not is_running_from_reloader():
        print("Starting background scheduler...")
        scheduler.start()

    app.run(debug=True)

