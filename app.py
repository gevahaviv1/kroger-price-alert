from flask import Flask, request, jsonify
from db.models import db, Product
from apscheduler.schedulers.background import BackgroundScheduler
from scripts.fetch_kroger_data import get_access_token, fetch_products
from map_kroger_data.mapper import map_kroger_to_zenday

# Define your watch-list IDs and polling interval
WATCHED_IDS = ["0001", "0002", "0003"]
POLL_MINUTES = 5

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
    def upsert_product_and_alert():
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

    def monitor_watched_products():
        with app.app_context():
            token = get_access_token()                         # OAuth2 token for Kroger
            for pid in WATCHED_IDS:
                # 2️⃣ Fetch the latest data for this single product
                items = fetch_products(token, term=pid, limit=5)
                # find exact match by productId
                raw = next((i for i in items if i.get("productId") == pid), None)
                if not raw:
                    print(f"⚠️  Couldn’t find Kroger data for {pid}")
                    continue

                # 3️⃣ Map to your DB format
                prod_data = map_kroger_to_zenday(raw)

                # 4️⃣ Compare vs stored record
                existing = Product.query.get(pid)
                new_pr  = prod_data["price"]["promo"]
                old_pr  = (existing.promo_price or 0) if existing else None

                if existing:
                    # only update if price dropped
                    if new_pr is not None and old_pr is not None and new_pr < old_pr:
                        existing.regular_price = prod_data["price"]["regular"]
                        existing.promo_price   = new_pr
                        db.session.add(existing)
                        print(f"🔔 Price drop for {pid}: {old_pr} → {new_pr}")
                else:
                    # first time seeing it → insert + alert
                    new_p = Product(id=pid, **{k: prod_data[k] for k in (
                        "name","brand","category","image_url","product_url",
                        "fulfillment","stock_level","size","sold_by","location",
                        "dimensions","temperature_sensitive"
                    )},
                    regular_price=prod_data["price"]["regular"],
                    promo_price=prod_data["price"]["promo"])
                    db.session.add(new_p)
                    print(f"🔔 New product added: {pid} @ promo {new_pr}")

            db.session.commit()
            print(f"✅ [Scheduler] Checked {len(WATCHED_IDS)} products")

    # 5️⃣ Reschedule at your chosen interval
    scheduler.add_job(
        func=batch_alert_check,
        trigger="interval",
        minutes=POLL_MINUTES,
        id="kroger_watchlist_job",
        replace_existing=True
    )

    return app

if __name__ == '__main__':
    app = create_app()

    # Only start the scheduler if this is the main process (not the reloader)
    from werkzeug.serving import is_running_from_reloader
    if not is_running_from_reloader():
        print("Starting background scheduler...")
        scheduler.start()

    app.run(debug=True)

