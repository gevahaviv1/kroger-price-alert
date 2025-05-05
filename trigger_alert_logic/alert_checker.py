def should_trigger_alert(product_data: dict, user_thresholds: dict) -> bool:
    product_id = product_data.get("id")
    promo_price = product_data.get("price", {}).get("promo")

    if promo_price is None or product_id is None:
        return False

    user_price_limit = user_thresholds.get(product_id)
    if user_price_limit is None:
        return False

    return promo_price < user_price_limit
