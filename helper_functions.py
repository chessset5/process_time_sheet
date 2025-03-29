
import csv
import datetime
from datetime import datetime as dt, time, date, timedelta
import decimal
from decimal import Decimal
import re
import string

import workTime

DAYS_AGO = True


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
    total_seconds = Decimal(value=time_delta.total_seconds())
    return total_seconds / Decimal(value=3600)  # 3600 seconds in an hour


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
    diff : timedelta = timedelta(0)
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


def process_csv_file(csv_file: str) -> workTime.WorkTime:

    work_time: workTime.WorkTime = workTime.WorkTime()
    not_in_block: bool = True
    with open(file=csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        work_block: workTime.WorkBlock = workTime.WorkBlock()
        for index, row in enumerate(csv_reader):
            # first row
            if index == 0:
                work_time.name = row[0]
                continue

            # indication of the start of a block
            # ["","","Feb 5, 2025"]
            if row and not_in_block and is_valid_date(date_str=row[-1]):
                not_in_block = False
                work_block = workTime.WorkBlock()
                parsed_date: dt = parse_date(date_str=row[-1])
                work_block.day = parsed_date.date()
                continue

            # in a block
            if not not_in_block:
                # misc row in a block
                if row[0] == r"Start":
                    continue
                # indication of the end of a block
                if row[0].startswith(r"Total:"):
                    work_block.final_line.line = row[0]  # "Total:     08:00:00               $498.00"
                    split: list[str] = work_block.final_line.line.split()  # ["Total:","08:00:00","$498.00"]

                    time_: list[str] = split[1].split(":")  # ["08","00","00"]
                    hour: int = int(time_[0])
                    minute: int = int(time_[1])
                    second: int = int(time_[2])
                    work_block.final_line.total_time = timedelta(hours=hour, minutes=minute, seconds=second)  # 08:00:00

                    work_block.final_line.total_money = Decimal(value=split[2][1:])  # 498.00

                    work_time.work_blocks.append(work_block)
                    not_in_block = True
                    continue

                # row of a block
                # ["8:00:00 AM","12:00:00 PM","04:00:00","$249.00","comment"]
                line: workTime.ClockLine = workTime.ClockLine()
                line.start_time = parse_am_pm_time(time_str=row[0])  # "8:00:00 AM"
                line.end_time = parse_am_pm_time(time_str=row[1])  # "12:00:00 PM"
                line.total_time = time_string_to_timedelta(time_str=row[2])  # "04:00:00"
                line.money = Decimal(value=row[3][1:])  # 249.00
                line.comment = row[4]
                work_block.clock_times.append(line)
    return work_time


def clean_name(name: str) -> str:
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


def valid_date(day: date) -> bool:
    return day <= days_ago(days=7)


def process_line(work: workTime.WorkTime) -> dict[str, int | str | Decimal]:
    dec_default = "0"
    line: dict[str, int | str | Decimal] = {
        "description": clean_name(name=remove_phase_code(input_string=work.name)),
        "eqip. no.": "56.1077",
        "phase code": get_phase_code(work.name),
        "SAT ST": Decimal(value=dec_default), "sat ot": Decimal(value=dec_default),
        "SUN ST": Decimal(value=dec_default), "sun ot": Decimal(value=dec_default),
        "MON ST": Decimal(value=dec_default), "mon ot": Decimal(value=dec_default),
        "TUE ST": Decimal(value=dec_default), "tue ot": Decimal(value=dec_default),
        "WED ST": Decimal(value=dec_default), "wed ot": Decimal(value=dec_default),
        "THU ST": Decimal(value=dec_default), "thu ot": Decimal(value=dec_default),
        "FRI ST": Decimal(value=dec_default), "fri ot": Decimal(value=dec_default),
        "TOT ST": Decimal(value=dec_default), "tot ot": Decimal(value=dec_default),
    }
    to_st = Decimal(value='0')  # total standard time
    to_ot = Decimal(value='0')  # total over time
    for block in work.work_blocks:
        if DAYS_AGO:
            if valid_date(block.day):
                continue
        week_day: str = get_week_day(date_obj=block.day)
        mx_hrs = Decimal("8")  # max standard hours
        standard_word: str = week_day.upper()[:3]  # short capital week day (standard time) "MON"
        overtime_word: str = standard_word.lower()  # short lower week day "mon"
        standard_word += " ST"  # "MON ST"
        overtime_word += " ot"  # "mon ot"
        st: Decimal = timedelta_to_decimal_hours(time_delta=block.final_line.total_time)  # standard time

        # process to closest 15 min (25% of 60 mins)
        fractional: Decimal = st % Decimal(value='1')  # 00 . XX
        percent: Decimal = (fractional % Decimal(value='0.25')) / Decimal(value='0.25')  # to next 25%
        if percent != Decimal(value="0.0"):
            if percent > Decimal(value="0.5"):
                # move to next 25
                to_move: Decimal = Decimal(value='1') - percent
                st += (to_move * Decimal(value='0.25'))
            else:
                # drop to last 25
                st -= (percent * Decimal(value='0.25'))

        st = st.normalize()
        ot: Decimal = Decimal(value="0")  # overtime
        if st > mx_hrs:
            ot = st - mx_hrs
            st = mx_hrs
        ot = ot.normalize()

        line[standard_word] = st
        to_st += st
        line[overtime_word] = ot
        to_ot += ot
    line["TOT ST"] = to_st.normalize()
    line["tot ot"] = to_ot.normalize()
    return line
