
import datetime
import csv
import re
import workTime
import decimal
import pandas
import functools

from helper_funs import (
    parse_am_pm_time, 
    parse_date, 
    get_phase_code, 
    remove_phase_code, 
    time_string_to_timedelta, 
    timedelta_to_decimal_hours, 
    get_week_day,
                         )


from workTime import WorkTime as WT
from pandas import DataFrame as DF


def proc_table(work_times: list[workTime.WorkTime]) -> None:
    header: list[str] = [
        "Day",
        "Sat",
        "Sun",
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
    ]

    index: list[str] = [
        "Time In",
        "AM Rest Break ( yes)",
        "Lunch Out",
        "Lunch In",
        "PM Rest Break (yes)",
        "Time Out",
    ]

    table_df = DF(columns=header, index=index)
    data = dict[str, list[datetime.datetime]]()

    for wt in work_times:
        for block in wt.work_blocks:
            # if get
            get_week_day(block.day)

    md = table_df.to_markdown()
    print(md)
    with open(r"hidden/export/time_table.md", mode="w", encoding="utf-8") as f:
        f.write(md)
