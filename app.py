from flask import Flask, request, jsonify
from db.models import db, PriceAlertResult
from trigger_alert_logic.alert_checker import should_trigger_alert
from apscheduler.schedulers.background import BackgroundScheduler

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
        db.session.add(result)
        db.session.commit()

        return jsonify({"triggered": triggered})

    def batch_alert_check():
        with app.app_context():
            products = Product.query.all()
            
            sample_user_thresholds = {
                "0001": 1.80,
                "0002": 1.80,
                "0003": 1.00
            }
            user_id = "batch_user"

            for product in products:
                triggered = False
                if product.id in sample_user_thresholds:
                    threshold = sample_user_thresholds[product.id]
                    # Build a fake product dict to reuse the same logic
                    product_data = {
                        "id": product.id,
                        "price": {
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

    # Initialize and start scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=batch_alert_check, trigger="interval", minutes=0.5)  # Runs every 2 minutes
    scheduler.start()


    return app

# Entry point
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
