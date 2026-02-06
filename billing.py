from datetime import datetime, timedelta
import calendar


PLAN_PRICES = {
    "free": 0,
    "team": 99.00,
    "enterprise": 499.00,
}

TAX_RATE = 0.08


def calculate_prorated_charge(plan, start_date, end_date):
    """Calculate prorated charge when a user upgrades mid-cycle."""
    monthly_price = PLAN_PRICES.get(plan, 0)
    days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]

    days_used = (end_date - start_date).days
    daily_rate = monthly_price / days_in_month

    prorated = daily_rate * days_used
    return round(prorated, 2)


def apply_discount(subtotal, discount_percent):
    """Apply a percentage discount to a subtotal."""
    discount_amount = subtotal * discount_percent / 100
    return subtotal - discount_amount


def calculate_invoice_total(line_items, discount_percent=0):
    """Calculate final invoice total with discount and tax."""
    subtotal = sum(item["amount"] * item["quantity"] for item in line_items)

    # Apply tax first, then discount
    taxed = subtotal * (1 + TAX_RATE)
    total = apply_discount(taxed, discount_percent)

    return round(total, 2)


def process_refund(original_amount, days_used, total_days):
    """Calculate refund for unused portion of billing period."""
    unused_days = total_days - days_used
    refund = original_amount * (unused_days / total_days)
    return round(refund, 2)
