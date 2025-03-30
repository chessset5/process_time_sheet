

import json
import re
import string
from datetime import date
from datetime import datetime as dt
from datetime import time, timedelta
from decimal import Decimal


VALIDATE_DATE = True


def is_minutes_apart(time1: time, time2: time, minutes: int = 30) -> bool:
    """
    Checks if the difference between two time objects is exactly 30 minutes.

    Args:
        time1 (time): The first time object.
        time2 (time): The second time object.

    Returns:
        bool: True if the difference is exactly 30 minutes, False otherwise.

    Example:
        >>> from datetime import time
        >>> is_30_minutes_apart(time(14, 0), time(14, 30))
        True
        >>> is_30_minutes_apart(time(9, 0), time(9, 45))
        False
    """
    dummy_date: date = dt.today().date()  # Use the same arbitrary date
    dt1: dt = dt.combine(dummy_date, time1)
    dt2: dt = dt.combine(dummy_date, time2)

    # 29 minuets for a 1 minute delta
    return abs(dt1 - dt2) == timedelta(minutes=minutes)


def time_to_12_string(time_obj: time | dt) -> str:
    """
    Converts a time or dt object to a 12-hour formatted string.

    Args:
        time (time | dt): The time or datetime object to format.

    Returns:
        str: The formatted time string in "HH:MM AM/PM" format.

    Example:
        >>> from datetime import datetime, time
        >>> time_to_12_string(datetime(2024, 3, 11, 14, 30))
        '02:30 PM'
        >>> time_to_12_string(time(9, 15))
        '09:15 AM'
    """
    return time_obj.strftime(format="%I:%M %p")


def parse_date(date_str: str) -> dt:
    """
    Convert a date string in the format "Mar 3, 2025" into a datetime object.

    Args:
        date_str (str): A date string in the format "%b %d, %Y" (e.g., "Mar 3, 2025").

    Returns:
        datetime: A datetime object representing the given date with time set to 00:00:00.
    """
    return dt.strptime(date_str, "%b %d, %Y")


def parse_am_pm_time(time_str: str) -> time:
    """
    Convert a time string in the format "8:00:00 AM" or "12:15:00 PM" into a time object.

    Args:
        time_str (str): A time string in the format "%I:%M:%S %p" (e.g., "8:00:00 AM" or "12:15:00 PM") | "%I:%M:%S %p" (e.g., "8:00:00").

    Returns:
        time: A time object representing the given time.
    """
    try:
        # try with AM/PM
        return dt.strptime(time_str, "%I:%M:%S %p").time()
    except Exception as e:
        raise e


def time_string_to_timedelta(time_str: str) -> timedelta:
    """
    Converts a time string (in the format "HH:MM:SS") into a timedelta object.

    Args:
        time_str (str): A time string in the format "HH:MM:SS", where hours can exceed 24.

    Returns:
        timedelta: A timedelta object representing the total time.

    Example:
        >>> time_string_to_timedelta("30:45:10")
        timedelta(days=1, hours=6, minutes=45, seconds=10)
    """
    # Split the time string into hours, minutes, and seconds
    hours, minutes, seconds = map(int, time_str.split(':'))
    # Return a timedelta object with the total time
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def timedelta_to_decimal_hours(time_delta: timedelta) -> Decimal:
    """
    Converts a timedelta object to decimal hours with higher precision using the decimal library.

    Args:
        tdelta (timedelta): A timedelta object representing a duration.

    Returns:
        Decimal: The total time in decimal hours with improved precision.

    Example:
        >>> td = timedelta(hours=5, minutes=30)
        >>> timedelta_to_decimal_hours(td)
        Decimal('5.500000')
    """
    # Get total seconds from timedelta and convert to decimal hours
    total_seconds = Decimal(value=str(time_delta.total_seconds()))
    return total_seconds / Decimal(value='3600.00')  # 3600 seconds in an hour


def days_ago(days: int = 5) -> date:
    """
    Get the datetime object representing the start of the day (00:00:00)
    for the date that is a given number of days ago.

    Args:
        days (int, optional): The number of days to go back from today. Defaults to 5.

    Returns:
        date: A date object set to 00:00:00 of the calculated date.
    """
    target_date: dt = dt.now() - timedelta(days=days)
    return target_date.date()


def time_diff(lhs: time, rhs: time) -> timedelta:
    """
    time_diff returns the timedelta between two times.
    The timedelta will always be positive

    Args:
        lhs (time): left hand side
        rhs (time): right hand side

    Returns:
        timedelta: time difference
    """
    lhs_dt: timedelta = dt.combine(date=date.min, time=lhs) - dt.min
    rhs_dt: timedelta = dt.combine(date=date.min, time=rhs) - dt.min
    # diff, keep it positive.
    diff: timedelta = timedelta(0)
    if lhs_dt > rhs_dt:
        diff = lhs_dt - rhs_dt
    else:
        diff = rhs_dt - lhs_dt
    return diff


def get_week_day(date_obj: dt | date) -> str:
    """
    Get the name of the day of the week from a datetime object.

    Args:
        date_obj (datetime): The datetime object to determine the day of the week from.

    Returns:
        str: The name of the day of the week (e.g., "Monday", "Tuesday").
    """
    day_names: list[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week_name: str = day_names[date_obj.weekday()]
    return day_of_week_name


def is_valid_date(date_str: str) -> bool:
    """
    Check if the given string matches the date format "Mar 3, 2025" or "March 3, 2025" using a regular expression.

    Args:
        date_str (str): The date string to validate.

    Returns:
        bool: True if the string matches the expected format, False otherwise.
    """
    pattern = r"^[A-Z][a-z]+ \d{1,2}, \d{4}$"
    return bool(re.fullmatch(pattern=pattern, string=date_str))


def get_phase_code(input_string) -> str:
    """
    Extracts the first matched string from the input string that follows the format
    of two digits, followed by a dot, three digits, another dot, and four digits.

    Args:
        input_string (str): The input string in which the pattern will be searched for.

    Returns:
        str : The matched string if a match is found, otherwise "".

    Example:
        >>> get_phase_code("Here is a number 10.010.0023 that I want to match.")
        '10.010.0023'

        >>> get_phase_code("No valid number here.")
        None
    """
    # Define the pattern for the string you want to match
    pattern = r"\d{2}\.\d{3}\.\d{4}"

    # Search for the first match in the input string
    match: re.Match[str] | None = re.search(pattern=pattern, string=input_string)

    # If a match is found, return the matched string
    if match:
        return match.group()
    else:
        return ""  # Return None if no match is found


def name_from_phase_code(phase_code: str) -> str:
    """
    Returns phase code name if it exists.
    If no code exists, "" is returned

    Args:
        phase_code (str): phase code to look for

    Returns:
        str: phase code name
    """
    # ...
    # Process Phase code xlsx into a dictionary for speed
    # make them strings instead of multiple cells
    phase_code = phase_code.strip()
    codes: dict[str, str] = {}
    try:
        from envHidden.data.file_locations import PHASECODE_PATH
        with open(file=PHASECODE_PATH, mode="r", encoding="utf-8") as f:
            codes = json.load(fp=f)
        if phase_code in codes:
            return codes[phase_code]
    except:
        print("No Phase Codes present")
    finally:
        return ""


def remove_phase_code(input_string) -> str:
    """
    Removes the first matched string from the input string that follows the format
    of two digits, followed by a dot, three digits, another dot, and four digits.

    Args:
        input_string (str): The input string from which the matched pattern will be removed.

    Returns:
        str: A new string with the matched substring removed. If no match is found,
             the original input string is returned unchanged.

    Example:
        >>> remove_phase_code("Here is a number 10.010.0023 that I want to remove.")
        'Here is a number  that I want to remove.'

        >>> remove_phase_code("No valid number here.")
        'No valid number here.'
    """
    # Define the pattern for the string you want to match and remove
    pattern = r"\d{2}\.\d{3}\.\d{4}"

    # Remove the first occurrence of the matched string
    result: str = re.sub(pattern=pattern, repl='', string=input_string, count=1)

    return result


def sanitized_first_three_words(name: str) -> str:
    '''
    sanitizes the name and removes invalid characters and returns the first 3 words
    '''
    name = name.encode(encoding='ascii', errors='ignore').decode(encoding='ascii')
    words: list[str] = name.split()
    first_three: list[str] = list[str]()
    good_chars: set[str] = set(string.ascii_letters + string.digits + "-.")
    only_digits: set[str] = set(string.digits + "-.")  # including digit separators
    for word in words:
        word_set = set(word)
        if word_set.issubset(only_digits):
            continue
        if word_set.issubset(good_chars):
            first_three.append(word)
            if len(first_three) >= 3:
                break

    return " ".join(first_three)

def this_friday() -> date:
    '''
    returns this friday. This is inclusive, if today is friday, it will return today.
    '''
    today: date = date.today()
    day_offset_lookup: dict[str, int] = {"Friday": 0, "Saturday": 6, "Sunday": 5, "Monday": 5, "Tuesday": 3, "Wednesday": 2, "Thursday": 1}
    offset: int = day_offset_lookup[get_week_day(date_obj=today)]
    return today + timedelta(days=offset)

def next_friday() -> date:
    '''
    returns the next friday
    '''
    today: date = date.today()
    day_offset_lookup: dict[str, int] = {"Friday": 7, "Saturday": 6, "Sunday": 5, "Monday": 5, "Tuesday": 3, "Wednesday": 2, "Thursday": 1}
    offset: int = day_offset_lookup[get_week_day(date_obj=today)]
    return today + timedelta(days=offset)


def last_friday() -> date:
    '''
    returns the date of last friday
    '''
    today: date = date.today()
    day_offset_lookup: dict[str, int] = {"Saturday": -1, "Sunday": -2, "Monday": -3, "Tuesday": -4, "Wednesday": -5, "Thursday": -6, "Friday": -7}
    offset: int = day_offset_lookup[get_week_day(date_obj=today)]
    return today + timedelta(days=offset)


def invalid_date(day: date) -> bool:
    '''
    Returns True if the date is invalid, else returns false
    '''
    return day <= last_friday() if VALIDATE_DATE else False
