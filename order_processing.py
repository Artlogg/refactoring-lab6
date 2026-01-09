DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21

SAVE10_RATE = 0.10
SAVE20_HIGH_RATE = 0.20
SAVE20_LOW_RATE = 0.05
SAVE20_THRESHOLD = 200

VIP_HIGH_DISCOUNT = 50
VIP_LOW_DISCOUNT = 10
VIP_THRESHOLD = 100

def calculate_subtotal(items):
    return sum(it["price"] * it["qty"] for it in items)

def calculate_tax(amount):
    return int(amount * TAX_RATE)

def calculate_discount(subtotal, coupon):
    if not coupon:
        return 0

    if coupon == "SAVE10":
        return int(subtotal * SAVE10_RATE)

    if coupon == "SAVE20":
        if subtotal >= SAVE20_THRESHOLD:
            return int(subtotal * SAVE20_HIGH_RATE)
        return int(subtotal * SAVE20_LOW_RATE)

    if coupon == "VIP":
        return VIP_HIGH_DISCOUNT if subtotal >= VIP_THRESHOLD else VIP_LOW_DISCOUNT

    raise ValueError("unknown coupon")

def parse_request(request: dict):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency

def validate_request(user_id, items):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    for it in items:
        if "price" not in it or "qty" not in it:
            raise ValueError("item must have price and qty")
        if it["price"] <= 0:
            raise ValueError("price must be positive")
        if it["qty"] <= 0:
            raise ValueError("qty must be positive")

def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)

    if currency is None:
        currency = DEFAULT_CURRENCY

    validate_request(user_id, items)

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, coupon)

    total_after_discount = max(subtotal - discount, 0)
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    order_id = f"{user_id}-{len(items)}-X"

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }

