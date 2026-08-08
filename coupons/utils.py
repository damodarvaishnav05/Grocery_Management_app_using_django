from datetime import date
import hashlib

def get_daily_coupon():
    today = date.today().strftime("%Y-%m-%d")

    code = "FM" + hashlib.md5(today.encode()).hexdigest()[:6].upper()

    return {
        "code": code,
        "discount": 10
    }