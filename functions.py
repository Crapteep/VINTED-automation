from datetime import datetime

def date_extract(notification_time):
    try:
        new_date, new_time = notification_time.split(',')
    except:
        new_date, new_time = notification_time.split(' ')

    dd, mm, rrrr = new_date.strip().split('.')
    final_date = f'{rrrr}-{mm}-{dd} {new_time.strip()}'
    return final_date


def calc_percent_of_price(price, percent):
    return round(price - price * (percent / 100), 1)


def calc_price_before_discount(discounted_price, discount_percent):
    return int(discounted_price / ((100 - discount_percent) / 100))


def get_today_date():
    time_now = datetime.now()
    return time_now.strftime("%Y-%m-%d %H:%M:%S")