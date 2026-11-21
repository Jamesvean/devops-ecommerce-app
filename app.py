import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for

PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones", "price_pence": 4999, "emoji": "🎧"},
    {"id": 2, "name": "Laptop Stand", "price_pence": 2599, "emoji": "💻"},
    {"id": 3, "name": "Mechanical Keyboard", "price_pence": 7999, "emoji": "⌨️"},
    {"id": 4, "name": "USB-C Hub", "price_pence": 3499, "emoji": "🔌"},
]

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-before-deployment"),
        DATABASE=os.environ.get("DATABASE_PATH", str(Path(__file__).parent / "data" / "orders.db")),
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    def connect_db():
        path = Path(app.config["DATABASE"])
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        return connection

    with app.app_context():
        with connect_db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                items TEXT NOT NULL,
                total_pence INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )""")
            db.commit()

    @app.template_filter("gbp")
    def gbp(pence):
        return f"£{pence / 100:.2f}"

    @app.get("/")
    def home():
        return render_template("index.html", products=PRODUCTS)

    @app.post("/cart/add/<int:product_id>")
    def add_to_cart(product_id):
        if not any(p["id"] == product_id for p in PRODUCTS):
            abort(404)
        cart = dict(session.get("cart", {}))
        key = str(product_id)
        cart[key] = min(int(cart.get(key, 0)) + 1, 20)
        session["cart"] = cart
        flash("Product added to cart.")
        return redirect(url_for("home"))

    @app.get("/cart")
    def view_cart():
        cart = session.get("cart", {})
        items = []
        for p in PRODUCTS:
            quantity = int(cart.get(str(p["id"]), 0))
            if quantity > 0:
                items.append({**p, "quantity": quantity, "subtotal": p["price_pence"] * quantity})
        total = sum(item["subtotal"] for item in items)
        return render_template("cart.html", items=items, total=total)

    @app.post("/checkout")
    def checkout():
        cart = session.get("cart", {})
        lines = []
        total = 0
        for p in PRODUCTS:
            quantity = max(0, min(int(cart.get(str(p["id"]), 0)), 20))
            if quantity:
                lines.append(f"{p['name']} x{quantity}")
                total += p["price_pence"] * quantity
        if not lines:
            flash("Your cart is empty.")
            return redirect(url_for("view_cart"))
        with connect_db() as db:
            cursor = db.execute(
                "INSERT INTO orders (items, total_pence, created_at) VALUES (?, ?, ?)",
                (", ".join(lines), total, datetime.now(timezone.utc).isoformat()),
            )
            db.commit()
            order_id = cursor.lastrowid
        session.pop("cart", None)
        return render_template("success.html", order_id=order_id, total=total)

    @app.get("/health")
    def health():
        try:
            with connect_db() as db:
                db.execute("SELECT 1").fetchone()
            return jsonify(status="ok", database="ok"), 200
        except sqlite3.Error:
            return jsonify(status="error", database="error"), 503

    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
