import unittest
from cart.engine import HeadlessCartEngine, LineItem, CouponRule


class TestHeadlessCartEngine(unittest.TestCase):
    def setUp(self):
        self.engine = HeadlessCartEngine()
        self.engine.set_inventory("SMARTWATCH-01", 10)
        self.engine.register_coupon(CouponRule(
            code="SALE20",
            discount_type="PERCENTAGE",
            discount_value=20.0,
            min_order_value=1000.0,
            max_discount_cap=500.0
        ))

    def test_cart_summary_and_coupon_discount(self):
        self.engine.add_item_to_cart("CART-101", LineItem(
            sku="SMARTWATCH-01", title="Smartwatch Pro", unit_price=2000.0, quantity=1, gst_rate_pct=18.0
        ))
        summary = self.engine.compute_cart_summary("CART-101", coupon_code="SALE20")
        self.assertEqual(summary.subtotal, 2000.0)
        # 20% of 2000 = 400 (under 500 cap)
        self.assertEqual(summary.discount_amount, 400.0)
        self.assertEqual(summary.net_taxable_amount, 1600.0)
        self.assertEqual(summary.shipping_fee, 0.0)  # > 999 free shipping

    def test_flash_sale_atomic_checkout(self):
        self.engine.add_item_to_cart("CART-102", LineItem(
            sku="SMARTWATCH-01", title="Smartwatch Pro", unit_price=2000.0, quantity=3
        ))
        res = self.engine.checkout_flash_sale_order("CART-102", customer_id="CUST-77")
        self.assertEqual(res["status"], "PAYMENT_CONFIRMED")
        self.assertEqual(self.engine.inventory["SMARTWATCH-01"], 7)  # 10 - 3


if __name__ == "__main__":
    unittest.main()
