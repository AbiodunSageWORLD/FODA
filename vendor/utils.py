from datetime import datetime
import pytz
import bcrypt

def get_current_day_and_time(timezone_name="Africa/lagos"):
    """
    Returns the current day of th week
    """
    tz = pytz.timezone(timezone_name)
    now =datetime.now(tz)

    day_mapping = {
        0:"MON", 1:"TUE", 2:"WED", 3:"THU", 
        4:"FRI", 5:"SAT", 6:"SUN"
    }

    current_day = day_mapping.get(now.weekday())
    current_time = now.time()

    return current_day, current_time
# creating password


def hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

def check_password(raw_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(raw_password.encode(), hashed_password.encode())
