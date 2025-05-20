import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
from db.models import db, Product, PriceHistory
from app import create_app


def plot_all():
    app = create_app()
    app.config["SCHEDULER_ENABLED"] = False  # ← 🛑 no scheduler
    with app.app_context():
        # load history for each product
        for prod in Product.query.all():
            times = [h.timestamp for h in prod.history]
            promos = [h.promo_price for h in prod.history]

            plt.figure()
            plt.plot(times, promos, marker="o")
            plt.title(f"Price History for {prod.id} — {prod.name}")
            plt.xlabel("Time")
            plt.ylabel("Promo Price ($)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"../plots/{prod.id}_price_history.png")
            plt.show()
            plt.close()


if __name__ == "__main__":
    plot_all()
