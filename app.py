from flask import Flask, request, jsonify
from db.models import db, PriceAlertResult, Product
from trigger_alert_logic.alert_checker import should_trigger_alert
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
        data = request.json
        product = data.get("product")
        thresholds = data.get("thresholds")
        user_id = data.get("user_id", "anonymous")

        if not product or not thresholds:
            return jsonify({"error": "Missing product or thresholds"}), 400

        triggered = should_trigger_alert(product, thresholds)

        result = PriceAlertResult(
            product_id=product["id"],
            user_id=user_id,
            triggered=triggered
        )

        try:
            db.session.add(result)
            db.session.commit()
            return jsonify({"tirggered": triggered}), 200
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving PriceAlertResult: {e}")
            return jsonify({"error": "Internal server error"}), 500

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

