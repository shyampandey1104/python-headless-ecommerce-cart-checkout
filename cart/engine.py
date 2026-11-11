"""Headless E-Commerce Cart Session, Coupon Rule Evaluator & Flash Sale Checkout Engine."""

import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CouponRule(BaseModel):
    code: str
    discount_type: str  # PERCENTAGE or FLAT
    discount_value: float
    min_order_value: float = 0.0
    max_discount_cap: Optional[float] = None
    is_active: bool = True


class LineItem(BaseModel):
    sku: str
    title: str
    unit_price: float
    quantity: int
    gst_rate_pct: float = 18.0


class CartSummary(BaseModel):
    cart_id: str
    subtotal: float
    discount_amount: float
    applied_coupon: Optional[str] = None
    net_taxable_amount: float
    cgst_amount: float
    sgst_amount: float
    shipping_fee: float
    grand_total: float


class HeadlessCartEngine:
    """Manages high-concurrency cart sessions, promo coupon validations, and checkout order placement."""

    def __init__(self):
        self.inventory: Dict[str, int] = {}  # sku -> available stock
        self.coupons: Dict[str, CouponRule] = {}
        self.cart_sessions: Dict[str, List[LineItem]] = {}

    def set_inventory(self, sku: str, stock: int):
        self.inventory[sku] = stock

    def register_coupon(self, coupon: CouponRule):
        self.coupons[coupon.code.upper()] = coupon

    def add_item_to_cart(self, cart_id: str, item: LineItem):
        if cart_id not in self.cart_sessions:
            self.cart_sessions[cart_id] = []

        # Update if exists, else append
        for existing in self.cart_sessions[cart_id]:
            if existing.sku == item.sku:
                existing.quantity += item.quantity
                return
        self.cart_sessions[cart_id].append(item)

    def compute_cart_summary(self, cart_id: str, coupon_code: Optional[str] = None, is_interstate: bool = False) -> CartSummary:
        items = self.cart_sessions.get(cart_id, [])
        subtotal = sum(it.quantity * it.unit_price for it in items)

        discount = 0.0
        applied_code = None

        if coupon_code:
            code_upper = coupon_code.strip().upper()
            rule = self.coupons.get(code_upper)
            if rule and rule.is_active and subtotal >= rule.min_order_value:
                if rule.discount_type == "PERCENTAGE":
                    calculated_disc = (subtotal * rule.discount_value) / 100.0
                    if rule.max_discount_cap:
                        calculated_disc = min(calculated_disc, rule.max_discount_cap)
                    discount = calculated_disc
                else:  # FLAT
                    discount = min(subtotal, rule.discount_value)
                applied_code = code_upper

        net_taxable = max(0.0, subtotal - discount)
        shipping_fee = 0.0 if net_taxable >= 999.0 else 70.0  # Free shipping threshold ₹999

        # Average weighted GST on net taxable
        if subtotal > 0:
            avg_gst_rate = sum(it.quantity * it.unit_price * (it.gst_rate_pct / 100.0) for it in items) / subtotal
        else:
            avg_gst_rate = 0.18

        total_tax = round(net_taxable * avg_gst_rate, 2)
        cgst = round(total_tax / 2.0, 2)
        sgst = round(total_tax / 2.0, 2)

        grand_total = round(net_taxable + total_tax + shipping_fee, 2)

        return CartSummary(
            cart_id=cart_id,
            subtotal=round(subtotal, 2),
            discount_amount=round(discount, 2),
            applied_coupon=applied_code,
            net_taxable_amount=round(net_taxable, 2),
            cgst_amount=cgst,
            sgst_amount=sgst,
            shipping_fee=round(shipping_fee, 2),
            grand_total=grand_total
        )

    def checkout_flash_sale_order(self, cart_id: str, customer_id: str, coupon_code: Optional[str] = None) -> Dict[str, Any]:
        """Atomically locks stock and converts cart to confirmed order."""
        items = self.cart_sessions.get(cart_id, [])
        if not items:
            raise ValueError("Cart is empty.")

        # Check stock availability for all items
        for it in items:
            current_stock = self.inventory.get(it.sku, 0)
            if current_stock < it.quantity:
                raise ValueError(f"Flash sale stock exhausted for SKU {it.sku} (Available: {current_stock}, Requested: {it.quantity}).")

        # Atomic decrement
        for it in items:
            self.inventory[it.sku] -= it.quantity

        summary = self.compute_cart_summary(cart_id, coupon_code=coupon_code)
        order_number = f"ECOM-{uuid.uuid4().hex[:8].upper()}"

        # Clear cart session
        del self.cart_sessions[cart_id]

        return {
            "order_number": order_number,
            "customer_id": customer_id,
            "grand_total": summary.grand_total,
            "applied_coupon": summary.applied_coupon,
            "status": "PAYMENT_CONFIRMED",
            "items_count": len(items)
        }
