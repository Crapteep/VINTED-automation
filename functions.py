

def date_extract(notification_time):
    try:
        new_date, new_time = notification_time.split(',')
    except:
        new_date, new_time = notification_time.split(' ')

    dd, mm, rrrr = new_date.strip().split('.')
    final_date = f'{rrrr}-{mm}-{dd} {new_time.strip()}'
    return final_date