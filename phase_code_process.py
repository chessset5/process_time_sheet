import decimal
import functools
import os

import pandas
import workTime

from helper_functions import process_line


def process_work_times(work_list:list[workTime.WorkTime]) -> str:
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
    
    
    line_no = 0
    for work in work_list:
        line: dict[str, int | str | decimal.Decimal] = process_line(work=work)
        if line["TOT ST"] or line["tot ot"]:
            phase_sheet.loc[line_no] = line.copy()  # pyright: ignore
            line_no += 1
        
    return run_phase_sheet(headers=headers,phase_sheet=phase_sheet)
    

def run_phase_sheet(headers: list[str], phase_sheet: pandas.DataFrame) -> str:
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

    md:str = phase_sheet.to_markdown()

    md_file = r"./envHidden/export/phase_sheet.md"
    md_file = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)
        
    return md