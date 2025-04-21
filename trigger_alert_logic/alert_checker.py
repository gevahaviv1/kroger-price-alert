def should_trigger_alert(product_data: dict, user_thresholds: dict) -> bool:
    """
    Compares the product's current promo price to the user's desired price threshold.

    Args:
        product_data: dict containing 'id' and 'price' -> {'promo': float}
        user_thresholds: dict containing 'id' and 'max_price' -> float

    Returns:
        bool: True if promo price is lower than user's threshold
    """
    product_id = product_data.get("id")
    promo_price = product_data.get("price", {}).get("promo")

    if not promo_price or not product_id:
        return False

    user_price_limit = user_thresholds.get(product_id)
    if user_price_limit is None:
        return False

    return promo_price < user_price_limit
