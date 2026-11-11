# Python Headless E-Commerce Cart & Checkout Engine 🛒⚡

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

A high-concurrency headless e-commerce cart session manager, promo coupon rule evaluator, GST tax engine, and atomic inventory decrement checkout processor built in Python. Designed for modern headless frontends (Next.js, Remix, Flutter mobile apps).

---

## 🚀 Key Features

- **Decoupled Cart State Engine**: Blazing fast cart item additions, quantity updates, and subtotal recalculations.
- **Dynamic Coupon & Promo Engine**: Handles flat cash discounts, percentage discounts, minimum order value gates, and maximum rupee discount caps.
- **Indian GST Breakdown**: Computes item-level tax distributions (split into CGST & SGST or IGST for interstate shipping).
- **Concurrency-Safe Flash Sale Stock Locks**: Atomically decrements warehouse stock upon payment confirmation to eliminate race conditions and overselling.

---

## 📦 Installation & Setup

```bash
git clone https://github.com/shyampandey1104/python-headless-ecommerce-cart-checkout.git
cd python-headless-ecommerce-cart-checkout
pip install -r requirements.txt
```

---

## 🛠️ Usage Example

```python
from cart.engine import HeadlessCartEngine, LineItem, CouponRule

engine = HeadlessCartEngine()
engine.set_inventory("WIRELESS-EARBUDS", 50)
engine.register_coupon(CouponRule(code="DIWALI500", discount_type="FLAT", discount_value=500.0, min_order_value=2000.0))

engine.add_item_to_cart("SESSION-1", LineItem(sku="WIRELESS-EARBUDS", title="True Wireless Buds", unit_price=1200.0, quantity=2))

order = engine.checkout_flash_sale_order("SESSION-1", customer_id="CUST-9921", coupon_code="DIWALI500")
print(f"Order {order['order_number']} Confirmed | Grand Total: ₹{order['grand_total']}")
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📄 License
MIT License. Created with ❤️ by [Shyam Pandey](https://github.com/shyampandey1104).
