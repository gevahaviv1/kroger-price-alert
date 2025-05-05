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

    @app.route("/get-alerts", methods=["GET"])
    def get_alerts():
        try:
            user_id = request.args.get('user_id')

            query = PriceAlertResult.query
            if user_id:
                query = query.filter_by(user_id=user_id)

            alerts = query.order_by(PriceAlertResult.checked_at.desc()).all()

            response = [
                {
                    "product_id": alert.product_id,
                    "user_id": alert.user_id,
                    "triggered": alert.triggered,
                    "checked_at": alert.checked_at.isoformat()  # Format timestamp nicely
                }
                for alert in alerts
            ]

            return jsonify(response)
        except Exception as e:
            print(f"❌ Error retrieving alerts: {e}")
            return jsonify({"error": "Internal server error"}), 500

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
            products = Product.query.all()
            
            sample_user_thresholds = {
                "0001": 1.80,
                "0002": 1.80,
                "0003": 1.00
            }
            user_id = "batch_user"
            try:
                for product in products:
                    triggered = False
                    if product.id in sample_user_thresholds:
                        threshold = sample_user_thresholds[product.id]
                        # Build a fake product dict to reuse the same logic
                        product_data = {
                            "id": product.id,
                            "price": {
                                "regular": product.regular_price,
                                "promo": product.promo_price
                            }
                        }
                        triggered = should_trigger_alert(product_data, sample_user_thresholds)

                        result = PriceAlertResult(
                            product_id=product.id,
                            user_id=user_id,
                            triggered=triggered
                        )
                        db.session.add(result)

                db.session.commit()
                print("✅ [Scheduler] Batch alert check completed (real products from DB)!")
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

