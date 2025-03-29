import datetime
from datetime import datetime as dt, time, date, timedelta
import os
from collections import defaultdict
from decimal import Decimal

import pandas

import workTime
from helper_functions import (
    get_week_day,
    is_minutes_apart,
    time_to_12_string,
    days_ago,
    DAYS_AGO,
    valid_date,
    time_diff,
    timedelta_to_decimal_hours
)


def proc_table(work_list: list[workTime.WorkTime]) -> pandas.DataFrame:
    """
    Takes in a WorkTime object and creates its punch card.

    Assumes that the WorkTime has already been processed to 7 days only.
    No cleaning is done in this function

    Args:
        work_list (list[workTime.WorkTime]): input time to process.
    """

    if not work_list:
        return

    # loading times into respective days
    punch_week: defaultdict[str, list[workTime.ClockLine]] = defaultdict(list[workTime.ClockLine])
    for wt in work_list:
        for block in wt.work_blocks:
            if DAYS_AGO:
                # if day is more than 7 days ago, skip it
                if valid_date(block.day):
                    continue
            day: str = get_week_day(date_obj=block.day)
            short_day: str = day[:3]  # get the first 3 letters
            for clock in block.clock_times:
                punch_week[short_day].append(clock)

    # setting up data block
    header: list[str] = [
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
        ".......................",
        "2nd Lunch Out",
        "2nd Lunch In",
        "2nd PM Rest Break (yes)",
        "Time Out (10hr)",
        "",
        "hours punched:",
    ]
    time_sheet: dict[str, list[str]] = {}
    for day in header:
        time_sheet.update({day: [""] * len(index)})

    # process time sheet
    for day, punch_list in punch_week.items():
        # sort the days
        punch_list.sort(key=lambda x: x.start_time)

        # process the days
        punch_index = 2
        cur_punch: workTime.ClockLine = punch_list[0]
        next_punch: workTime.ClockLine = punch_list[1]
        time_in: time | str = cur_punch.start_time
        lunch_out: time| str = ""
        lunch_in: time| str = ""
        time_out: time| str = ""
        second_lunch_out: time| str = ""
        second_lunch_in: time| str = ""
        # second time out is just the first time out

        seen_blocks: set[workTime.ClockLine] = set()
        total_hours: timedelta = timedelta(0)

        while True:
            # something is wrong with this loop
            if time_diff(cur_punch.end_time, next_punch.start_time) > timedelta(minutes=30):
                # lunch time
                if not lunch_out:
                    lunch_out = (cur_punch.end_time)
                    lunch_in = (next_punch.start_time)
                elif lunch_out and (not second_lunch_out):
                    second_lunch_out = (cur_punch.end_time)
                    second_lunch_in = (next_punch.start_time)

            # redundancy due to my stupidity.
            if not cur_punch in seen_blocks:
                total_hours += cur_punch.total_time
                seen_blocks.add(cur_punch)
            cur_punch = next_punch

            # stupid but works ... is this how python do while works??
            if punch_index < len(punch_list):
                next_punch = punch_list[punch_index]
                punch_index += 1
            else:
                break
        # redundancy due to my stupidity.
        if not cur_punch in seen_blocks:
            total_hours += cur_punch.total_time
            seen_blocks.add(cur_punch)
        time_out = (cur_punch.end_time)

        # processing work hours more accurately
        hours_worked = timedelta(0)
        # calculating total hours
        if time_in and lunch_out:
            hours_worked += time_diff(time_in, lunch_out)
        if total_hours >= timedelta(hours=10):
            if lunch_in and second_lunch_out:
                hours_worked += time_diff(lunch_in,second_lunch_out)
            if second_lunch_in and time_out:
                hours_worked += time_diff(second_lunch_in,time_out)
        else:
            if lunch_in and time_out:
                hours_worked += time_diff(lunch_in,time_out)



        time_card: list[str | time] = []
        spacer = "."*len("----------")
        time_card.append(time_to_12_string(time_in))  # time in
        time_card.append("Yes")  # first break
        time_card.append(time_to_12_string(lunch_out))  # first lunch out
        time_card.append(time_to_12_string(lunch_in))  # first lunch in
        time_card.append("Yes")  # second break

        # if punched more than 10 hours:
        if total_hours >= timedelta(hours=10):
            time_card.append("")  # <10hr punch out
            time_card.append(spacer)  # spacer
            time_card.append(time_to_12_string(second_lunch_out))  # second lunch out
            time_card.append(time_to_12_string(second_lunch_in))  # second lunch in
            time_card.append("Yes")  # third break
            time_card.append(time_out)  # >10hr punch out
        else:
            time_card.append(time_out)  # <10hr punch out
            time_card.append(spacer)  # spacer
            time_card.append("")  # second lunch out
            time_card.append("")  # second lunch in
            time_card.append("")  # third break
            time_card.append("")  # >10hr punch out
        time_card.append("")
        time_card.append(f"{timedelta_to_decimal_hours(hours_worked).quantize(Decimal('0.00'))} hrs")  # num hours

        time_sheet.update({day: time_card})

    table_df: pandas.DataFrame = pandas.DataFrame(data=time_sheet, columns=header, index=index)

    md: str = table_df.to_markdown()

    md_file = r"./envHidden/export/time_table.md"
    md_file: str = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)

    md_file = r"./envHidden/export/dyn_time_table.md"
    md_file: str = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)

    return table_df