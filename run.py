"""
# @ Author: Aaron Shackelford
# @ Create Time: 2025-03-08 19:48:51
# @ Modified by: Aaron Shackelford
# @ Modified time: 2025-03-08 19:50:05
# @ Description: Processes data from WorkTime
"""

import copy
import csv
import os
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime as dt
from datetime import timedelta
from decimal import Decimal

import pandas

import workTime
from build_pdf import build_out_pdf
from envHidden.envSecret import EMPLOYEE_NAME, EMPLOYEE_NUMBER
from helper_functions import is_valid_date, parse_am_pm_time, parse_date, this_friday, time_string_to_timedelta
from phase_code_process import process_work_times
from table_process import proc_table

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


def process_csv_file(csv_file: str) -> workTime.WorkTime:
    """
    process the csv file
    """
    work_time: workTime.WorkTime = workTime.WorkTime()
    not_in_block: bool = True
    with open(file=csv_file, mode="r", encoding="utf-8") as file:
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


def process_time_card() -> None:
    """
    make time card
    """

    work_times: list[workTime.WorkTime] = list[workTime.WorkTime]()

    folder_path = r"envHidden/data/to_process"
    csv_files: list[str] = []
    for f in os.listdir(folder_path):
        if f.endswith(".csv"):
            path: str = os.path.normpath(os.path.join(folder_path, f))
            path: str = os.path.abspath(path)
            csv_files.append(path)
    for csv_file in csv_files:
        work: workTime.WorkTime = process_csv_file(csv_file)
        work_times.append(work)

    table_future: Future = Future()
    work_future: Future = Future()
    with ThreadPoolExecutor() as executor:
        table_future = executor.submit(proc_table, copy.deepcopy(work_times))
        work_future = executor.submit(process_work_times, copy.deepcopy(work_times))

    table_df: pandas.DataFrame | None = table_future.result()
    work_df: pandas.DataFrame | None = work_future.result()
    if table_df is not None and work_df is not None:
        print(table_df.to_markdown())
        print(work_df.to_markdown())
        print()

        card_info: dict[str, str] = {
            "Employee Name": EMPLOYEE_NAME,
            "Vehicle Number": "",
            "Employee Number": EMPLOYEE_NUMBER,
            "Payroll Period Ending": this_friday().strftime(format="%m/%d/%Y"),
        }
        build_out_pdf(phase_sheet=work_df, time_card=table_df, card_info=card_info)


def main() -> None:
    """
    main
    """
    process_time_card()
    return


if __name__ == "__main__":
    main()
