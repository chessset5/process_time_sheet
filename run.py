"""
# @ Author: Aaron Shackelford
# @ Create Time: 2025-03-08 19:48:51
# @ Modified by: Aaron Shackelford
# @ Modified time: 2025-03-08 19:50:05
# @ Description: Processes data from WorkTime
"""

import datetime
import csv
import re
import workTime
import decimal
import pandas
import functools

# pylint: disable=C0301
# '''
# The output formate will be like so:
# |               |                   |           | SAT   | sat   | SUN   | sun   | MON   | mon   | TUE   | tue   | WED   | wed   | THU   | thu   | FRI   | fri   | Total Hours   |
# | description   | Job No. Equip. No.| phase code| ST    | OT    | ST    | OT    | ST    | OT    | ST    | OT    | ST    | OT    | ST    | OT    | ST    | OT    | ST    | OT    |
# | ------------- | ----------------- | --------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
# | ...           | ...               | ...       | ...   | ...   | ...   | ...   | ...   | ...   | ...   | ...   | ...   | ...   | ...   | ...   | ...   | ...   | <SUM> | <SUM> |
# |               |                   |           |       |       |       |       |       |       |       |       |       |       |       |       |       |       |       |       |
# |               |                   |           | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> | <SUM> |

# | Day        | Sat      | Sun      | Mon      | Tue      | Wed      | Thu      | Fri      |
# | ---------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
# | Time In    | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M |
# | Lunch Out  | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M |
# | Lunch In   | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M |
# | Time Out   | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M |


# | 10hr+ OT   | Sat      | Sun      | Mon      | Tue      | Wed      | Thu      | Fri      |
# | ---------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
# | Time In    | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M |
# | Lunch Out  | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M |
# | Lunch In   | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M |
# | Time Out   | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M | 00:00 _M |
# '''

# '''
# csv data example
# "10.010.0023 Automation Engineer - Overhead  total amount: $110.67  total time: 02:40:00"

# "","","Mar 3, 2025"
# "Start","End","Time","Amount","Note"
# "8:00:00 AM","8:30:00 AM","00:30:00","$20.75",""
# "12:45:00 PM","1:00:00 PM","00:15:00","$10.38",""
# "Total:     00:45:00               $31.13"

# "","","Mar 4, 2025"
# "Start","End","Time","Amount","Note"
# "8:00:00 AM","9:15:00 AM","01:15:00","$51.88",""
# "Total:     01:15:00               $51.88"

# ...
# '''


def parse_date(date_str: str) -> datetime.datetime:
    """
    Convert a date string in the format "Mar 3, 2025" into a datetime object.

    Args:
        date_str (str): A date string in the format "%b %d, %Y" (e.g., "Mar 3, 2025").

    Returns:
        datetime: A datetime object representing the given date with time set to 00:00:00.
    """
    return datetime.datetime.strptime(date_str, "%b %d, %Y")


def parse_am_pm_time(time_str: str) -> datetime.time:
    """
    Convert a time string in the format "8:00:00 AM" or "12:15:00 PM" into a datetime.time object.

    Args:
        time_str (str): A time string in the format "%I:%M:%S %p" (e.g., "8:00:00 AM" or "12:15:00 PM") | "%I:%M:%S %p" (e.g., "8:00:00").

    Returns:
        datetime.time: A time object representing the given time.
    """
    try:
        # try with AM/PM
        return datetime.datetime.strptime(time_str, "%I:%M:%S %p").time()
    except Exception as e:
        raise e

def time_string_to_timedelta(time_str:str) -> datetime.timedelta:
    """
    Converts a time string (in the format "HH:MM:SS") into a datetime.timedelta object.

    Args:
        time_str (str): A time string in the format "HH:MM:SS", where hours can exceed 24.

    Returns:
        datetime.timedelta: A timedelta object representing the total time.

    Example:
        >>> time_string_to_timedelta("30:45:10")
        datetime.timedelta(days=1, hours=6, minutes=45, seconds=10)
    """
    # Split the time string into hours, minutes, and seconds
    hours, minutes, seconds = map(int, time_str.split(':'))
    # Return a timedelta object with the total time
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

def timedelta_to_decimal_hours(tdelta:datetime.timedelta) -> decimal.Decimal:
    """
    Converts a datetime.timedelta object to decimal hours with higher precision using the decimal library.

    Args:
        tdelta (datetime.timedelta): A timedelta object representing a duration.

    Returns:
        Decimal: The total time in decimal hours with improved precision.

    Example:
        >>> td = datetime.timedelta(hours=5, minutes=30)
        >>> timedelta_to_decimal_hours(td)
        Decimal('5.500000')
    """
    # Get total seconds from timedelta and convert to decimal hours
    total_seconds = decimal.Decimal(tdelta.total_seconds())
    return total_seconds / decimal.Decimal(3600)  # 3600 seconds in an hour

def days_ago(days: int = 5) -> datetime.date:
    """
    Get the datetime object representing the start of the day (00:00:00)
    for the date that is a given number of days ago.

    Args:
        days (int, optional): The number of days to go back from today. Defaults to 5.

    Returns:
        date: A date object set to 00:00:00 of the calculated date.
    """
    target_date: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=days)
    return target_date.date()


def get_week_day(date_obj: datetime.datetime) -> str:
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
                parsed_date: datetime.datetime = parse_date(date_str=row[-1])
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

                    time: list[str] = split[1].split(":")  # ["08","00","00"]
                    hour: int = int(time[0])
                    minute: int = int(time[1])
                    second: int = int(time[2])
                    work_block.final_line.total_time = datetime.timedelta(hours=hour, minutes=minute, seconds=second)  # 08:00:00

                    work_block.final_line.total_money = decimal.Decimal(split[2][1:])  # 498.00

                    work_time.work_blocks.append(work_block)
                    not_in_block = True
                    continue

                # row of a block
                # ["8:00:00 AM","12:00:00 PM","04:00:00","$249.00","comment"]
                line: workTime.ClockLine = workTime.ClockLine()
                line.start_time = parse_am_pm_time(row[0])  # "8:00:00 AM"
                line.end_time = parse_am_pm_time(row[1])  # "12:00:00 PM"
                line.total_time = time_string_to_timedelta(row[2])  # "04:00:00"
                line.money = decimal.Decimal(row[3][1:])  # 249.00
                line.comment = row[4]
    return work_time


def process_line(work: workTime.WorkTime) -> dict[str, int | str | decimal.Decimal]:
    line: dict[str, int | str] = {
        "description": remove_phase_code(work.name),
        "eqip. no.": "56.1077",
        "phase code": get_phase_code(work.name),
        "SAT ST": decimal.Decimal('0'), "sat ot": decimal.Decimal('0'),
        "SUN ST": decimal.Decimal('0'), "sun ot": decimal.Decimal('0'),
        "MON ST": decimal.Decimal('0'), "mon ot": decimal.Decimal('0'),
        "TUE ST": decimal.Decimal('0'), "tue ot": decimal.Decimal('0'),
        "WED ST": decimal.Decimal('0'), "wed ot": decimal.Decimal('0'),
        "THU ST": decimal.Decimal('0'), "thu ot": decimal.Decimal('0'),
        "FRI ST": decimal.Decimal('0'), "fri ot": decimal.Decimal('0'),
        "TOT ST": decimal.Decimal('0'), "tot ot": decimal.Decimal('0'),
    }
    to_st = decimal.Decimal('0') # total standard time
    to_ot = decimal.Decimal('0') # total over time
    for block in work.work_blocks:
        if block.day < days_ago(7):
            continue
        week_day: str = get_week_day(block.day)
        mx_hrs = decimal.Decimal("8") # max standard hours
        standard_word: str = week_day.upper()[:3] # short capital week day (standard time)
        overtime_word: str = standard_word.lower() # short lower week day
        standard_word += " ST"
        overtime_word += " ot"
        st: decimal.Decimal = timedelta_to_decimal_hours(tdelta=block.final_line.total_time) #standard time

        # process to closest 15 min (25% of 60 mins)
        fractional: decimal.Decimal = st % decimal.Decimal('1') # 00 . XX
        percent: decimal.Decimal = (fractional % decimal.Decimal('0.25'))/decimal.Decimal('0.25') # to next 25%
        if percent != decimal.Decimal("0.0"):
            if percent > decimal.Decimal("0.5"):
                # move to next 25
                to_move: decimal.Decimal = decimal.Decimal('1') - percent
                st += (to_move * decimal.Decimal('0.25'))
            else:
                # drop to last 25
                st -= (percent * decimal.Decimal('0.25'))

        ot: decimal.Decimal = decimal.Decimal("0") # overtime
        if st > mx_hrs:
            ot = st - mx_hrs
            st = mx_hrs
        for key in line:
            if key == standard_word:
                line[key] = st
                to_st += st
                continue
            if key == overtime_word:
                line[key] = ot
                to_ot += ot
    line["TOT ST"] = to_st
    line["tot ot"] = to_ot
    return line




def run_last_week() -> None:

    headers: list[str] = ["description", "eqip. no.", "phase code", "SAT ST", "sat ot", "SUN ST", "sun ot", "MON ST", "mon ot", "TUE ST", "tue ot", "WED ST", "wed ot", "THU ST", "thu ot", "FRI ST", "fri ot", "TOT ST", "tot ot"]
    phase_sheet: pandas.DataFrame = pandas.DataFrame(columns=headers)

    work_times: list[workTime.WorkTime] = list[workTime.WorkTime]()
    for csv_file in [r"hidden/data/to_process/10.010.0023 - Data Mar 3, 2025 - Mar 9, 2025.csv", r"hidden/data/to_process/10.010.0033 - Data Mar 3, 2025 - Mar 9, 2025.csv"]:
        work: workTime.WorkTime = process_csv_file(csv_file)
        work_times.append(work)

        line: dict[str, int | str | decimal.Decimal] = process_line(work)
        phase_sheet.loc[len(phase_sheet)] = line.copy()

    # sum line
    sum_line = pandas.Series(index=headers)

    for idx, head in enumerate(sum_line.index):
        if idx < 3:
            continue
        values:list[decimal.Decimal] = phase_sheet[head].to_list()
        sum_line[head] = functools.reduce(lambda x, y : x+y,values)

    # blank row
    phase_sheet.loc[len(phase_sheet)] = [None] * len(phase_sheet.columns)

    # adding sum row
    phase_sheet.loc[len(phase_sheet)] = sum_line

    md = phase_sheet.to_markdown()
    print(md)
    with open(r"hidden/export/phase_sheet.md",mode="w",encoding="utf-8") as f:
        f.write(md)

    time_table: pandas.DataFrame = pandas.DataFrame()

    return


def main() -> None:
    run_last_week()
    return


if __name__ == "__main__":
    main()
