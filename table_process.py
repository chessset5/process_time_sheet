import datetime
import os
from collections import defaultdict

import pandas

import workTime
from helper_functions import get_week_day, is_minutes_apart, time_to_12_string, days_ago, DAYS_AGO

def proc_table_refactored(work_list:list[workTime.WorkTime])->None:
        
    # TODO:
    # [ ] refactor this
    # [ ] line up all the punches for the day
    # [ ]   if the start of one punch is 30m+ the end of another punch, assume it is lunch.
    #           else ignore the previous punch
    # [ ] implement sudo code:
    # [ ]      punch_list
    # [ ]      punch_index = 2
    # [ ]      cur_punch = punch_list[0] # first punch
    # [ ]      next_punch = punch_list[1] # second punch
    # [ ]      punch_in = cur_punch.start
    # [ ]      lunch_in
    # [ ]      lunch_out
    # [ ]      punch_out
    # [ ]      lunch_ot_in
    # [ ]      lunch_ot_out
    # [ ]      punch_ot_out
    # [ ]      while next_punch != punch_list[-1] # next punch is not last punch
    # [ ]          if diff(cur_punch.last, next_punch.start) > 30:
    # [ ]              # assume this is lunch
    # [ ]              lunch_out = cur_punch.last
    # [ ]              lunch_in = next_punch.start
    # [ ]              break
    # [ ]          else:
    # [ ]              cur_punch = next_punch
    # [ ]              next_punch = punch_list[punch_index]
    # [ ]              punch_index += 1
    #
    # [ ]      # figure out the OT stuff
    #       
    #   [ ] if total work > 10hrs calculate OT lunches and OT time
    #       [ ] make OT calculations
    
    # loading times
    punch_week: defaultdict[str, list[workTime.ClockLine]] = defaultdict(list[workTime.ClockLine])
    for wt in work_list:
        for block in wt.work_blocks:
            if DAYS_AGO:
                # if day is more than 7 days ago, skip it
                if block.day >= days_ago(days=7):
                    continue
            day: str = get_week_day(date_obj=block.day)
            short_day: str = day[:3] # get the first 3 letters
            for clock in block.clock_times:
                punch_week[short_day].append(clock)
    
    for day, punch_list in punch_week.items():
        punch_index = 2
        cur_punch: workTime.ClockLine = punch_list.pop(0)
        
        
    
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
    punches: defaultdict[str, list[datetime.time]] = defaultdict(list[datetime.time])
    for wt in work_list:
        for block in wt.work_blocks:
            if DAYS_AGO:
                if block.day < days_ago(days=7):
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

        time_slot: dict[datetime.time, int] = {}
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
