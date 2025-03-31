#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
 # @ Author: Aaron Shackelford
 # @ Create Time: 2025-03-29 13:34:40
 # @ Modified by: Aaron Shackelford
 # @ Modified time: 2025-03-30 12:36:56
 # @ Description:

 Processes the phase code sheet
 '''


import decimal
import functools
import os
from decimal import Decimal

import pandas

import workTime
from helper_functions import (get_phase_code, get_week_day, invalid_date,
                              name_from_phase_code,
                              sanitized_first_three_words,
                              timedelta_to_decimal_hours)

# TODO:
# [ ] Refactor this into more defined functions


def process_line(work: workTime.WorkTime) -> dict[str, int | str | Decimal]:
    """
    Processes work into a phase code line

    Args:
        work (workTime.WorkTime): work to process

    Returns:
        dict[str, int | str | Decimal]: line of work for the phase code sheet
    """
    name: str = name_from_phase_code(phase_code=get_phase_code(input_string=work.name))
    dec_default = "0"
    line: dict[str, int | str | Decimal] = {
        "description": sanitized_first_three_words(name=name),
        "eqip. no.": "56.1077",
        "phase code": get_phase_code(work.name),
        "SAT ST": Decimal(value=dec_default), "sat ot": Decimal(value=dec_default),
        "SUN ST": Decimal(value=dec_default), "sun ot": Decimal(value=dec_default),
        "MON ST": Decimal(value=dec_default), "mon ot": Decimal(value=dec_default),
        "TUE ST": Decimal(value=dec_default), "tue ot": Decimal(value=dec_default),
        "WED ST": Decimal(value=dec_default), "wed ot": Decimal(value=dec_default),
        "THU ST": Decimal(value=dec_default), "thu ot": Decimal(value=dec_default),
        "FRI ST": Decimal(value=dec_default), "fri ot": Decimal(value=dec_default),
        "TOT ST": Decimal(value=dec_default), "tot ot": Decimal(value=dec_default),
    }
    to_st = Decimal(value='0')  # total standard time
    to_ot = Decimal(value='0')  # total over time
    for block in work.work_blocks:
        if invalid_date(block.day):
            continue
        week_day: str = get_week_day(date_obj=block.day)
        mx_hrs = Decimal("8")  # max standard hours
        standard_word: str = week_day.upper()[:3]  # short capital week day (standard time) "MON"
        overtime_word: str = standard_word.lower()  # short lower week day "mon"
        standard_word += " ST"  # "MON ST"
        overtime_word += " ot"  # "mon ot"
        st: Decimal = timedelta_to_decimal_hours(time_delta=block.final_line.total_time)  # standard time

        # process to closest 15 min (25% of 60 mins)
        fractional: Decimal = st % Decimal(value='1')  # 00 . XX
        percent: Decimal = (fractional % Decimal(value='0.25')) / Decimal(value='0.25')  # to next 25%
        if percent != Decimal(value="0.0"):
            if percent > Decimal(value="0.5"):
                # move to next 25
                to_move: Decimal = Decimal(value='1') - percent
                st += (to_move * Decimal(value='0.25'))
            else:
                # drop to last 25
                st -= (percent * Decimal(value='0.25'))

        st = st.normalize()
        ot: Decimal = Decimal(value="0")  # overtime
        if st > mx_hrs:
            ot = st - mx_hrs
            st = mx_hrs
        ot = ot.normalize()

        line[standard_word] = st
        to_st += st
        line[overtime_word] = ot
        to_ot += ot
    line["TOT ST"] = to_st.normalize()
    line["tot ot"] = to_ot.normalize()
    return line


def process_work_times(work_list: list[workTime.WorkTime]) -> pandas.DataFrame:
    """
    Processes work into phase code sheet

    Args:
        work_list (list[workTime.WorkTime]): work to process

    Returns:
        pandas.DataFrame: pandas dataframe of work in the shape of the phase code sheet
    """
    if not work_list:
        return

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

    return run_phase_sheet(headers=headers, phase_sheet=phase_sheet)


def run_phase_sheet(headers: list[str], phase_sheet: pandas.DataFrame) -> pandas.DataFrame:
    """
    calculates totals line and generates markdown line

    Args:
        headers (list[str]): headers to use in dataframe
        phase_sheet (pandas.DataFrame): dataframe to fill data

    Returns:
        pandas.DataFrame: filled out dataframe
    """
    # sum line
    # TODO:
    # [ ] refactor this line to just use index=phase_sheet.headers or something
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

    md: str = phase_sheet.to_markdown()

    md_file = r"./envHidden/export/phase_sheet.md"
    md_file = os.path.normpath(md_file)
    with open(file=md_file, mode="w", encoding="utf-8") as f:
        f.write(md)

    return phase_sheet
