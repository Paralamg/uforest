from datetime import datetime

def get_color_by_date(date_str):
    try:
        last = datetime.strptime(date_str, "%d-%m-%Y")
    except:
        return "gray"
    days = (datetime.now() - last).days
    if days < 180:
        return "green"
    elif days < 365:
        return "orange"
    else:
        return "red"