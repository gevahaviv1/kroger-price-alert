from alert_checker import should_trigger_alert

def test_should_trigger_alert():
    product = {
        "id": "0001111041700",
        "price": {
            "promo": 1.59
        }
    }

    user_thresholds = {
        "0001111041700": 1.80  # ALERT: promo is cheaper than threshold
    }

    assert should_trigger_alert(product, user_thresholds) == True

def test_should_not_trigger_alert():
    product = {
        "id": "0001111041700",
        "price": {
            "promo": 2.00
        }
    }

    user_thresholds = {
        "0001111041700": 1.80  # NO ALERT: promo is higher
    }

    assert should_trigger_alert(product, user_thresholds) == False
