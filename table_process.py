import datetime
from datetime import datetime as dt, time, date, timedelta
import os
from collections import defaultdict

import pandas

import workTime
from helper_functions import get_week_day, is_minutes_apart, time_to_12_string, days_ago, DAYS_AGO, valid_date, time_diff


def proc_table_refactored(work_list: list[workTime.WorkTime]) -> None:
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
        " ... ",
        "2nd Lunch Out",
        "2nd Lunch In",
        "2nd PM Rest Break (yes)",
        "Time Out (10hr)",
    ]
    time_sheet: dict[str, list[str]] = {}
    for day in header:
        time_sheet.update({day: []})

    # process time sheet
    for day, punch_list in punch_week.items():
        punch_index = 2
        cur_punch: workTime.ClockLine = punch_list[0]
        next_punch: workTime.ClockLine = punch_list[1]
        time_in: str = time_to_12_string(cur_punch.start_time)
        lunch_out: str = ""
        lunch_in: str = ""
        time_out: str = ""
        second_lunch_out: str = ""
        second_lunch_in: str = ""
        # second time out is just the first time out

        seen_blocks: set[workTime.ClockLine] = set()
        total_hours: timedelta = timedelta(0)

        while True:
            # something is wrong with this loop
            if time_diff(cur_punch.end_time, next_punch.start_time) > timedelta(minutes=30):
                # lunch time
                if not lunch_out:
                    lunch_out = time_to_12_string(cur_punch.end_time)
                    lunch_in = time_to_12_string(next_punch.start_time)
                elif lunch_out and (not second_lunch_out):
                    second_lunch_out = time_to_12_string(cur_punch.end_time)
                    second_lunch_in = time_to_12_string(next_punch.start_time)

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
        time_out = time_to_12_string(cur_punch.end_time)

        time_card: list[str | time] = []
        time_card.append(time_in)  # time in
        time_card.append("Yes")  # first break
        time_card.append(lunch_out)  # first lunch out
        time_card.append(lunch_in)  # first lunch in
        time_card.append("Yes")  # second break

        # if punched more than 10 hours:
        if total_hours >= timedelta(hours=10):
            time_card.append("")  # <10hr punch out
            time_card.append("...")  # spacer
            time_card.append(second_lunch_out)  # second lunch out
            time_card.append(second_lunch_in)  # second lunch in
            time_card.append("Yes")  # third break
            time_card.append(time_out)  # >10hr punch out
        else:
            time_card.append(time_out)  # <10hr punch out
            time_card.append("...")  # spacer
            time_card.append("")  # second lunch out
            time_card.append("")  # second lunch in
            time_card.append("")  # third break
            time_card.append("")  # >10hr punch out

        time_sheet.update({day: time_card})

    table_df: pandas.DataFrame = pandas.DataFrame(data=time_sheet, columns=header, index=index)

    md: str = table_df.to_markdown()
    print(md)
    print()

    md_file = r"./envHidden/export/time_table.md"
    md_file: str = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)

    md_file = r"./envHidden/export/dyn_time_table.md"
    md_file: str = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)

    return


def proc_table(work_list: list[workTime.WorkTime]) -> None:

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
        " ... ",
        "2nd Lunch Out",
        "2nd Lunch In",
        "2nd PM Rest Break (yes)",
        "Time Out (10hr)",
    ]

    # only punch ins
    punch_idxs: list[str] = [i for i in index if (not "Break" in i) and (not "..." in i)]  # time in
    breaks_idxs: list[str] = [i for i in index if ("Break" in i)]  # rest breaks

    table_df = pandas.DataFrame(columns=header, index=index)
    # table_df.rename_axis(mapper="Day", axis="columns", inplace=True)

    dyn_df = pandas.DataFrame(columns=header)

    # loading times
    punches: defaultdict[str, list[time]] = defaultdict(list[time])
    for wt in work_list:
        for block in wt.work_blocks:
            if DAYS_AGO:
                if valid_date(block.day):
                    continue
            day: str = get_week_day(date_obj=block.day)
            short_day: str = day[:3]
            for clock in block.clock_times:
                punches[short_day].append(clock.start_time)
                punches[short_day].append(clock.end_time)

    for day in punches:
        t = punches[day]
        t = set(t)
        t = list(t)
        t.sort()
        t = list(map(time_to_12_string, t))
        print(f"{day} : {t}")

    # process times into dataframe
    for day, time_list in punches.items():
        if not time_list:
            continue
        time_list.sort()

        time_slot: dict[time, int] = {}
        for t in time_list:
            # get t, if no t, t = 0, t = t + 1
            time_slot[t] = time_slot.get(t, 0) + 1

        dyn_list: list[str] = list(map(time_to_12_string, time_slot))
        if len(dyn_df) < len(dyn_list):
            dyn_df.reindex(range(len(dyn_list)))
        dyn_df[day] = dyn_list + [None] * (len(dyn_df) - len(dyn_list))

        dyn_list: list[str] = []
        for t, i in time_slot.items():
            if i > 1:
                pass
            else:
                dyn_list.append(time_to_12_string(t))

        # updating the day's breaks
        break_list: list[str] = ["yes"] * (len(dyn_list) // 2)  # number of breaks is punches // 2
        break_packed_list: list[str | None] = break_list + [None] * (len(breaks_idxs) - len(break_list))
        breaks_series = pandas.Series(break_packed_list, index=breaks_idxs)
        table_df[day].update(breaks_series)

        # updating the day's punch in time
        dyn_packed_list: list[str | None] = dyn_list + [None] * (len(punch_idxs) - len(dyn_list))
        dyn_series = pandas.Series(dyn_packed_list, index=punch_idxs)
        table_df[day].update(dyn_series)

    table_df.replace(pandas.NA, None, inplace=True)
    table_df.loc[" ... "] = " ... "
    dyn_df.replace(pandas.NA, None, inplace=True)

    md: str = table_df.to_markdown()
    print(md)
    print()

    md_file = r"./envHidden/export/time_table.md"
    md_file: str = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)

    md: str = dyn_df.to_markdown()
    print(md)
    print()

    md_file = r"./envHidden/export/dyn_time_table.md"
    md_file: str = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)
