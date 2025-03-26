"""
# @ Author: Aaron Shackelford
# @ Create Time: 2025-03-08 19:48:51
# @ Modified by: Aaron Shackelford
# @ Modified time: 2025-03-08 19:50:05
# @ Description: Processes data from WorkTime
"""

import concurrent.futures
import os
import copy

import concurrent
from concurrent.futures import ThreadPoolExecutor

import workTime
from helper_functions import process_csv_file
from table_process import proc_table
from phase_code_process import process_work_times


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


def process_time_card() -> None:
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

    futures: list[concurrent.futures.Future] = []
    with ThreadPoolExecutor() as executor:
        futures.append(executor.submit(process_work_times, copy.deepcopy(work_times)))
        futures.append(executor.submit(proc_table, copy.deepcopy(work_times)))

    for future in futures:
        print(future.result())


def main() -> None:
    process_time_card()
    return


if __name__ == "__main__":
    main()
