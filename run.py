"""
# @ Author: Aaron Shackelford
# @ Create Time: 2025-03-08 19:48:51
# @ Modified by: Aaron Shackelford
# @ Modified time: 2025-03-08 19:50:05
# @ Description: Processes data from WorkTime
"""

import decimal
import functools
import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal as D

import pandas

import workTime
from helper_functions import process_csv_file, process_line
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


def run_phase_sheet(headers: list[str], phase_sheet: pandas.DataFrame) -> None:
    # sum line
    total_line = pandas.Series(index=headers)
    total_line["description"] = "TOTAL"

    for idx, col_name in enumerate(total_line.index):
        if idx < 3:
            continue
        values: list[decimal.Decimal] = phase_sheet[col_name].dropna().to_list()
        total_line[col_name] = functools.reduce(lambda x, y: x + y, values)

    # blank row
    # phase_sheet.loc[len(phase_sheet)] = [None] * len(phase_sheet.columns)

    # adding sum row
    phase_sheet.loc["Total"] = total_line
    phase_sheet.replace(to_replace=pandas.NA, value="", inplace=True)

    md = phase_sheet.to_markdown()
    print(md)
    print()

    md_file = r"./envHidden/export/phase_sheet.md"
    md_file = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)


def process_time_card() -> None:

    # Define the header
    headers: list[str] = [
        "description",
        "eqip. no.",
        "phase code",
        "SAT ST",
        "sat ot",
        "SUN ST",
        "sun ot",
        "MON ST",
        "mon ot",
        "TUE ST",
        "tue ot",
        "WED ST",
        "wed ot",
        "THU ST",
        "thu ot",
        "FRI ST",
        "fri ot",
        "TOT ST",
        "tot ot",
    ]

    # Define the index
    index: list[str | int] = list(range(23)) + [
        "PTO",
        "Holiday",
        "Jury",
        "Bereavement",
        "Sick",
        "Total",
    ]  # [0,...,22,"PTO",...,"Total"]

    # Create an empty DataFrame with the specified header and index
    phase_sheet: pandas.DataFrame = pandas.DataFrame(columns=headers, index=index)

    # Set the values for 'description', 'eqip. no.' and 'phase code' for rows 'PTO' to 'Bereavement'
    phase_sheet.loc["PTO":"Bereavement", ["eqip. no.", "phase code"]] = [
        "56.1077",
        "10.010.0023",
    ]
    phase_sheet.loc["PTO", "description"] = "PTO"
    phase_sheet.loc["Holiday", "description"] = "Holiday"
    phase_sheet.loc["Jury", "description"] = "Jury Duty"
    phase_sheet.loc["Bereavement", "description"] = "Bereavement"
    phase_sheet.loc["Sick", "description"] = "*Sick Reserve (Salaried)"

    work_times: list[workTime.WorkTime] = list[workTime.WorkTime]()
    line_no = 0

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

        line: dict[str, int | str | decimal.Decimal] = process_line(work)
        phase_sheet.loc[line_no] = line.copy()  # pyright: ignore
        line_no += 1

    # with ThreadPoolExecutor() as e:
    #     e.submit(run_phase_sheet(headers=headers, phase_sheet=phase_sheet))
    #     e.submit(proc_table(work_list=work_times))
    (run_phase_sheet(headers=headers, phase_sheet=phase_sheet))
    (proc_table(work_list=work_times))
    return


def main() -> None:
    process_time_card()
    return


if __name__ == "__main__":
    main()
