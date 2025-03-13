
import datetime
import os
from collections import defaultdict

import pandas

import workTime
from helper_functions import get_week_day, is_minutes_apart, time_to_12_string


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
    punch_idxs: list[str] = [i for i in index if (not "Break" in i) and (not "..." in i)] # time in
    breaks_idxs: list[str] = [i for i in index if ("Break" in i)] # rest breaks

    table_df = pandas.DataFrame(columns=header, index=index)
    # table_df.rename_axis(mapper="Day", axis="columns", inplace=True)

    dyn_df = pandas.DataFrame(columns=header)

    # loading times
    punches: defaultdict[str, list[datetime.datetime]] = defaultdict(list[datetime.datetime])
    for wt in work_list:
        for block in wt.work_blocks:
            day: str = get_week_day(date_obj=block.day)
            short_day: str = day[:3]
            for clock in block.clock_times:
                if clock.start_time != datetime.time():
                    punches[short_day].append(clock.start_time)
                if clock.end_time != datetime.time():
                    punches[short_day].append(clock.end_time)

    # set break cells to automatic yes
    for i in header:
        if len(punches[i])>0:
            for b_i in breaks_idxs:
                #  row, col
                table_df.loc[b_i, i] = "yes"

    # process times into dataframe
    for day, time_list in punches.items():
        if not time_list:
            continue
        time_list.sort()

        time_slot: dict[datetime.datetime,int] = {}
        for t in time_list:
            time_slot[t] = time_slot.get(t,0) + 1

        dyn_list = list(map(time_to_12_string,time_slot))
        if len(dyn_df) < len(dyn_list):
            dyn_df.reindex(range(len(dyn_list)))
        dyn_df[day] = dyn_list + [None] * (len(dyn_df) - len(dyn_list))

        dyn_list:list[str] = []
        for t, i in time_slot.items():
            if i > 1:
                pass
            else:
                dyn_list.append(time_to_12_string(t))


        dyn_list: list[str | None] = dyn_list + [None] * (len(punch_idxs) - len(dyn_list))

        values_series = pandas.Series(dyn_list, index=punch_idxs)

        # table_df.loc[punch_idxs,day]=dyn_list
        table_df[day].update(values_series)

    table_df.replace(pandas.NA,None,inplace=True)
    table_df.loc[" ... "] = " ... "
    dyn_df.replace(pandas.NA,None,inplace=True)

    md: str = table_df.to_markdown()
    print(md)
    print()

    md_file: str = ""
    if os.name == "nt":  # Windows
        md_file = r"./envHidden/export/time_table.md"
    elif os.name == "posix":  # Linux/macOS
        md_file = r"./envHidden/export/time_table.md"
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)

    md: str = dyn_df.to_markdown()
    print(md)
    print()

    md_file: str = ""
    if os.name == "nt":  # Windows
        md_file = r"./envHidden/export/dyn_time_table.md"
    elif os.name == "posix":  # Linux/macOS
        md_file = r"./envHidden/export/dyn_time_table.md"
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)
