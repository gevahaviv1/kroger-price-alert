# Zenday - Kroger Price Alert System

This project is part of the Zenday platform.  
It allows users to receive alerts when their favorite Kroger grocery items drop in price.

Built with **Python**, **Flask**, **SQLAlchemy**, and **APScheduler**.

---

## 🚀 Features

- Map Kroger product data to Zenday internal structure.
- Check for significant price changes based on user preferences.
- Store and retrieve alert results.
- Background scheduler for periodic batch checks.
- Clean REST API endpoints.

---

## 📂 Project Structure

<!-- STRUCTURE_START -->

<!-- STRUCTURE_END -->

---

## ⚙️ Installation

1. Clone the repository:

         bash
         git clone https://github.com/<your-username>/kroger-price-alert.git
         cd kroger-price-alert

2. Create and activate a virtual environment:

         python3 -m venv venv
         source venv/bin/activate

3. Install the dependencies:

         pip install -r requirements.txt

## 🛠️ Running the App

1. Initialize the database (optional for fresh install):

         python3 scripts/insert_products.py

2. Start the Flask app:

         python3 app.py

## 📡 API Endpoints

- **POST /trigger-alert**

  - Trigger a price check manually for a product.

  - **Request:** JSON with product data

  - **Response:** Triggered or not.

- **GET /get-alerts**

  - Retrieve past price alert results.

  - **Optional:** ?user_id=xxx to filter alerts by user.

## 🧪 Testing

Run test scripts manually:

      python3 scripts/read_alerts.py
      python3 map_kroger_data/test_mapper.py
      python3 trigger_alert_logic/test_alert_checker.py

## 👨‍💻 Technologies

 - Flask

 - Flask-SQLAlchemy

 - APScheduler

 - SQLite
