from flask import Flask, request, jsonify
from db.models import db, PriceAlertResult
from trigger-alert-logic.alert_checker import should_trigger_alert

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

    return app

# Entry point
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
