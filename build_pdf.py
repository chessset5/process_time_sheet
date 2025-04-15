#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
# -*- coding: utf-8 -*-
# @ Author: Aaron Shackelford
# @ Create Time: 2025-03-30 12:47:16
# @ Modified by: Aaron Shackelford
# @ Modified time: 2025-03-30 18:27:20
# @ Description:

builds out timecard pdf for user
'''
# @chessset5
# @Loki-waterAIC

import io
import os
from typing import Any

import pandas
import pypdf
import pypdf.generic
from pandas import DataFrame

from helper_functions import this_friday

# pylint: disable=C0301
# '''
# The PDF will have the following value targets:

# Employee value targets
# | Employee Name | Employee Number | Vehicle Number | Payroll Period Ending |

# Phase code table targets, A.<col>.row
# The headers are not target-able, they are just here for demonstration purposes
# NOTE in col 0,1,2 at the end of these columns, there are some values that are not target-able.
# |             |                    |            | SAT    | sat    | SUN    | sun    | MON    | mon    | TUE    | tue     | WED     | wed     | THU     | thu     | FRI     | fri     | Total Hours       |
# | description | Job No. Equip. No. | phase code | ST     | OT     | ST     | OT     | ST     | OT     | ST     | OT      | ST      | OT      | ST      | OT      | ST      | OT      | ST      | OT      |
# | ----------- | ------------------ | ---------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
# | A.0.0       | A.1.0              | A.2.0      | A.3.0  | A.4.0  | A.5.0  | A.6.0  | A.7.0  | A.8.0  | A.9.0  | A.10.0  | A.11.0  | A.12.0  | A.13.0  | A.14.0  | A.15.0  | A.16.0  | A.17.0  | A.18.0  |
# | A.0.1       | A.1.1              | A.2.1      | A.3.1  | A.4.1  | A.5.1  | A.6.1  | A.7.1  | A.8.1  | A.9.1  | A.10.1  | A.11.1  | A.12.1  | A.13.1  | A.14.1  | A.15.1  | A.16.1  | A.17.1  | A.18.1  |
# | A.0.2       | A.1.2              | A.2.2      | A.3.2  | A.4.2  | A.5.2  | A.6.2  | A.7.2  | A.8.2  | A.9.2  | A.10.2  | A.11.2  | A.12.2  | A.13.2  | A.14.2  | A.15.2  | A.16.2  | A.17.2  | A.18.2  |
# | A.0.3       | A.1.3              | A.2.3      | A.3.3  | A.4.3  | A.5.3  | A.6.3  | A.7.3  | A.8.3  | A.9.3  | A.10.3  | A.11.3  | A.12.3  | A.13.3  | A.14.3  | A.15.3  | A.16.3  | A.17.3  | A.18.3  |
# | A.0.4       | A.1.4              | A.2.4      | A.3.4  | A.4.4  | A.5.4  | A.6.4  | A.7.4  | A.8.4  | A.9.4  | A.10.4  | A.11.4  | A.12.4  | A.13.4  | A.14.4  | A.15.4  | A.16.4  | A.17.4  | A.18.4  |
# | A.0.5       | A.1.5              | A.2.5      | A.3.5  | A.4.5  | A.5.5  | A.6.5  | A.7.5  | A.8.5  | A.9.5  | A.10.5  | A.11.5  | A.12.5  | A.13.5  | A.14.5  | A.15.5  | A.16.5  | A.17.5  | A.18.5  |
# | A.0.6       | A.1.6              | A.2.6      | A.3.6  | A.4.6  | A.5.6  | A.6.6  | A.7.6  | A.8.6  | A.9.6  | A.10.6  | A.11.6  | A.12.6  | A.13.6  | A.14.6  | A.15.6  | A.16.6  | A.17.6  | A.18.6  |
# | A.0.7       | A.1.7              | A.2.7      | A.3.7  | A.4.7  | A.5.7  | A.6.7  | A.7.7  | A.8.7  | A.9.7  | A.10.7  | A.11.7  | A.12.7  | A.13.7  | A.14.7  | A.15.7  | A.16.7  | A.17.7  | A.18.7  |
# | A.0.8       | A.1.8              | A.2.8      | A.3.8  | A.4.8  | A.5.8  | A.6.8  | A.7.8  | A.8.8  | A.9.8  | A.10.8  | A.11.8  | A.12.8  | A.13.8  | A.14.8  | A.15.8  | A.16.8  | A.17.8  | A.18.8  |
# | A.0.9       | A.1.9              | A.2.9      | A.3.9  | A.4.9  | A.5.9  | A.6.9  | A.7.9  | A.8.9  | A.9.9  | A.10.9  | A.11.9  | A.12.9  | A.13.9  | A.14.9  | A.15.9  | A.16.9  | A.17.9  | A.18.9  |
# | A.0.10      | A.1.10             | A.2.10     | A.3.10 | A.4.10 | A.5.10 | A.6.10 | A.7.10 | A.8.10 | A.9.10 | A.10.10 | A.11.10 | A.12.10 | A.13.10 | A.14.10 | A.15.10 | A.16.10 | A.17.10 | A.18.10 |
# | A.0.11      | A.1.11             | A.2.11     | A.3.11 | A.4.11 | A.5.11 | A.6.11 | A.7.11 | A.8.11 | A.9.11 | A.10.11 | A.11.11 | A.12.11 | A.13.11 | A.14.11 | A.15.11 | A.16.11 | A.17.11 | A.18.11 |
# | A.0.12      | A.1.12             | A.2.12     | A.3.12 | A.4.12 | A.5.12 | A.6.12 | A.7.12 | A.8.12 | A.9.12 | A.10.12 | A.11.12 | A.12.12 | A.13.12 | A.14.12 | A.15.12 | A.16.12 | A.17.12 | A.18.12 |
# | A.0.13      | A.1.13             | A.2.13     | A.3.13 | A.4.13 | A.5.13 | A.6.13 | A.7.13 | A.8.13 | A.9.13 | A.10.13 | A.11.13 | A.12.13 | A.13.13 | A.14.13 | A.15.13 | A.16.13 | A.17.13 | A.18.13 |
# | A.0.14      | A.1.14             | A.2.14     | A.3.14 | A.4.14 | A.5.14 | A.6.14 | A.7.14 | A.8.14 | A.9.14 | A.10.14 | A.11.14 | A.12.14 | A.13.14 | A.14.14 | A.15.14 | A.16.14 | A.17.14 | A.18.14 |
# | A.0.15      | A.1.15             | A.2.15     | A.3.15 | A.4.15 | A.5.15 | A.6.15 | A.7.15 | A.8.15 | A.9.15 | A.10.15 | A.11.15 | A.12.15 | A.13.15 | A.14.15 | A.15.15 | A.16.15 | A.17.15 | A.18.15 |
# | A.0.16      | A.1.16             | A.2.16     | A.3.16 | A.4.16 | A.5.16 | A.6.16 | A.7.16 | A.8.16 | A.9.16 | A.10.16 | A.11.16 | A.12.16 | A.13.16 | A.14.16 | A.15.16 | A.16.16 | A.17.16 | A.18.16 |
# | A.0.17      | A.1.17             | A.2.17     | A.3.17 | A.4.17 | A.5.17 | A.6.17 | A.7.17 | A.8.17 | A.9.17 | A.10.17 | A.11.17 | A.12.17 | A.13.17 | A.14.17 | A.15.17 | A.16.17 | A.17.17 | A.18.17 |
# | A.0.18      | A.1.18             | A.2.18     | A.3.18 | A.4.18 | A.5.18 | A.6.18 | A.7.18 | A.8.18 | A.9.18 | A.10.18 | A.11.18 | A.12.18 | A.13.18 | A.14.18 | A.15.18 | A.16.18 | A.17.18 | A.18.18 |
# | A.0.19      | A.1.19             | A.2.19     | A.3.19 | A.4.19 | A.5.19 | A.6.19 | A.7.19 | A.8.19 | A.9.19 | A.10.19 | A.11.19 | A.12.19 | A.13.19 | A.14.19 | A.15.19 | A.16.19 | A.17.19 | A.18.19 |
# | A.0.20      | A.1.20             | A.2.20     | A.3.20 | A.4.20 | A.5.20 | A.6.20 | A.7.20 | A.8.20 | A.9.20 | A.10.20 | A.11.20 | A.12.20 | A.13.20 | A.14.20 | A.15.20 | A.16.20 | A.17.20 | A.18.20 |
# | A.0.21      | A.1.21             | A.2.21     | A.3.21 | A.4.21 | A.5.21 | A.6.21 | A.7.21 | A.8.21 | A.9.21 | A.10.21 | A.11.21 | A.12.21 | A.13.21 | A.14.21 | A.15.21 | A.16.21 | A.17.21 | A.18.21 |
# | A.0.22      | A.1.22             | A.2.22     | A.3.22 | A.4.22 | A.5.22 | A.6.22 | A.7.22 | A.8.22 | A.9.22 | A.10.22 | A.11.22 | A.12.22 | A.13.22 | A.14.22 | A.15.22 | A.16.22 | A.17.22 | A.18.22 |
# | ...         | A.1.23             | A.2.23     | A.3.23 | A.4.23 | A.5.23 | A.6.23 | A.7.23 | A.8.23 | A.9.23 | A.10.23 | A.11.23 | A.12.23 | A.13.23 | A.14.23 | A.15.23 | A.16.23 | A.17.23 | A.18.23 |
# | ...         | A.1.24             | A.2.24     | A.3.24 | A.4.24 | A.5.24 | A.6.24 | A.7.24 | A.8.24 | A.9.24 | A.10.24 | A.11.24 | A.12.24 | A.13.24 | A.14.24 | A.15.24 | A.16.24 | A.17.24 | A.18.24 |
# | ...         | A.1.25             | A.2.25     | A.3.25 | A.4.25 | A.5.25 | A.6.25 | A.7.25 | A.8.25 | A.9.25 | A.10.25 | A.11.25 | A.12.25 | A.13.25 | A.14.25 | A.15.25 | A.16.25 | A.17.25 | A.18.25 |
# | ...         | A.1.26             | A.2.26     | A.3.26 | A.4.26 | A.5.26 | A.6.26 | A.7.26 | A.8.26 | A.9.26 | A.10.26 | A.11.26 | A.12.26 | A.13.26 | A.14.26 | A.15.26 | A.16.26 | A.17.26 | A.18.26 |
# | ...         | A.1.27             | A.2.27     | A.3.27 | A.4.27 | A.5.27 | A.6.27 | A.7.27 | A.8.27 | A.9.27 | A.10.27 | A.11.27 | A.12.27 | A.13.27 | A.14.27 | A.15.27 | A.16.27 | A.17.27 | A.18.27 |
# | ...         | ...                | ...        | A.3.28 | A.4.28 | A.5.28 | A.6.28 | A.7.28 | A.8.28 | A.9.28 | A.10.28 | A.11.28 | A.12.28 | A.13.28 | A.14.28 | A.15.28 | A.16.28 | A.17.28 | A.18.28 |


# Time card table targets, B.<col>.<row>
# The headers are not target-able, they are just here for demonstration purposes
# | Day           | Sat    | Sun    | Mon    | Tue    | Wed    | Thu    | Fri    |
# | ------------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
# | Time In       | B.0.0  | B.1.0  | B.2.0  | B.3.0  | B.4.0  | B.5.0  | B.6.0  |
# | break one     | B.0.1  | B.1.1  | B.2.1  | B.3.1  | B.4.1  | B.5.1  | B.6.1  |
# | Lunch Out     | B.0.2  | B.1.2  | B.2.2  | B.3.2  | B.4.2  | B.5.2  | B.6.2  |
# | Lunch In      | B.0.3  | B.1.3  | B.2.3  | B.3.3  | B.4.3  | B.5.3  | B.6.3  |
# | break two     | B.0.4  | B.1.4  | B.2.4  | B.3.4  | B.4.4  | B.5.4  | B.6.4  |
# | Time Out      | B.0.5  | B.1.5  | B.2.5  | B.3.5  | B.4.5  | B.5.5  | B.6.5  |

# | 10hr+ OT      | Sat    | Sun    | Mon    | Tue    | Wed    | Thu    | Fri    |
# | ------------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
# | Lunch two Out | B.0.6  | B.1.6  | B.2.6  | B.3.6  | B.4.6  | B.5.6  | B.6.6  |
# | Lunch two In  | B.0.7  | B.1.7  | B.2.7  | B.3.7  | B.4.7  | B.5.7  | B.6.7  |
# | break three   | B.0.8  | B.1.8  | B.2.8  | B.3.8  | B.4.8  | B.5.8  | B.6.8  |
# | Time Out      | B.0.9  | B.1.9  | B.2.9  | B.3.9  | B.4.9  | B.5.9  | B.6.9  |
# | notes         | B.0.10 | B.1.10 | B.2.10 | B.3.10 | B.4.10 | B.5.10 | B.6.10 |
# '''

def __build_reference_time_sheet_data_frame() -> DataFrame:
    """
    returns reference time sheet dataframe
    """    # setting up data block
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
        "2nd Lunch Out",
        "2nd Lunch In",
        "2nd PM Rest Break (yes)",
        "Time Out (10hr)",
        "Make up hours"
    ]

    # data
    data: dict[str | int, list[str]] = {}

    for row in range(11):
        col_list: list[str] = []
        for col in range(7):
            col_list.append(f"B.{col}.{row}")

        data.update({index[row]: col_list})

    # Create an empty DataFrame with the specified header and index
    time_card: pandas.DataFrame = pandas.DataFrame(index=header, data=data)

    # cause I am an idiot and set this up sideways
    transposed: DataFrame = time_card.transpose()

    return transposed


def __build_reference_phase_code_data_frame() -> DataFrame:
    """
    returns reference phase code dataframe
    """
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
    ]  # ['0', ... ,'22',"PTO",...,"Total"]

    # data
    data: dict[str | int, list[str]] = {}

    for row in range(29):
        col_list: list[str] = []
        for col in range(19):
            col_list.append(f"A.{col}.{row}")

        data.update({index[row]: col_list})

    # Create an empty DataFrame with the specified header and index
    # cause I am an idiot and set this up sideways (index = headers).transpose()
    phase_sheet: pandas.DataFrame = pandas.DataFrame(index=headers, data=data)
    phase_sheet = phase_sheet.transpose()

    # Set the values for 'description', 'eqip. no.' and 'phase code' for rows 'PTO' to 'Bereavement'
    phase_sheet.loc["Bereavement":"PTO", ["eqip. no.", "phase code"]] = [
        "56.1077",
        "10.010.0023",
    ]
    phase_sheet.loc["PTO", "description"] = "PTO"
    phase_sheet.loc["Holiday", "description"] = "Holiday"
    phase_sheet.loc["Jury", "description"] = "Jury Duty"
    phase_sheet.loc["Bereavement", "description"] = "Bereavement"
    phase_sheet.loc["Sick", "description"] = "*Sick Reserve (Salaried)"
    phase_sheet.loc["Total", "description"] = "TOTAL"
    phase_sheet.loc["Total", "eqip. no."] = " ... "
    phase_sheet.loc["Total", "phase code"] = " ... "

    return phase_sheet


def find_df_location(df: pandas.DataFrame, find_value: Any) -> tuple[Any, Any]:
    '''
    Find Data Frame Location, returns where a find value is

    Args:
        df (pandas.DataFrame): data frame to look through
        find_value (Any): value to find in the data frame

    Returns:
        tuple[Any,Any]: tuple of locations where the value occurs
    '''
    locations: list[tuple[Any, Any]] = (df == find_value).stack().loc[lambda x: x].index.tolist()
    return locations[0]


def get_new_value(pdf_value: str, time_card: DataFrame, reference_time_card: DataFrame, phase_sheet: DataFrame, reference_phase_sheet: DataFrame, card_info: dict) -> str:
    '''returns the value based off the reference value

    Args:
        pdf_value (str): target value
        time_card (DataFrame): dataframe to get timecard data from
        reference_time_card (DataFrame): dataframe to get target location from
        phase_sheet (DataFrame): dataframe to get phase sheet data from
        reference_phase_sheet (DataFrame): dataframe to get target location from
        card_info (dict): dictionary with misc data

    Returns:
        str: replacement string
    '''
    if pdf_value in card_info:
        return card_info[pdf_value]

    if pdf_value in reference_phase_sheet.values:
        if pdf_value == "A.1.0":
            pause = True
        location: tuple[Any, Any] = find_df_location(df=reference_phase_sheet, find_value=pdf_value)
        if not (phase_sheet.loc[location] is pandas.NA):
            return str(object=phase_sheet.loc[location])

    if pdf_value in reference_time_card.values:
        location: tuple[Any, Any] = find_df_location(df=reference_time_card, find_value=pdf_value)
        if not (time_card.loc[location] is pandas.NA):
            return str(object=time_card.loc[location])
    return ""


def build_out_pdf(phase_sheet: DataFrame, time_card: DataFrame, card_info: dict[str, str]) -> None:
    '''
    Creates pdf for user

    Args:
        phase_sheet (DataFrame): phase sheet dataframe
        time_card (DataFrame): time card dataframe
        card_info (dict[str, str]): information for the pdf >>>
        ```
        {
            Employee Name : "",
            Employee Number: "",
            Vehicle Number: "",
            Payroll Period Ending: ""
        }
        ```
    '''

    reference_phase_sheet: DataFrame = __build_reference_phase_code_data_frame()
    reference_time_card: DataFrame = __build_reference_time_sheet_data_frame()

    # try to write pdf
    try:
        from envHidden.data.file_locations import PDF_PATH  # pylint: disable=C0415
        from envHidden.envSecret import PDF_FILE_NAME  # pylint: disable=C0415

        input_pdf_path: str = os.path.normpath(PDF_PATH)

        out_file_name: str = PDF_FILE_NAME.replace("YYYYMMDD", this_friday().strftime("%Y%m%d"))
        off_set: int = len(PDF_PATH.removesuffix(os.path.basename(PDF_FILE_NAME)))
        output_pdf_path: str = os.path.normpath(PDF_PATH[:off_set] + out_file_name)

        pdf_in_memory: io.BytesIO = io.BytesIO()

        # load file into memory
        with open(file=input_pdf_path, mode="rb") as key:
            key.seek(0)
            pdf_in_memory.write(key.read())

        # create the output file
        with open(file=output_pdf_path, mode='wb') as output_pdf:
            reader = pypdf.PdfReader(stream=pdf_in_memory)
            writer = pypdf.PdfWriter()

            # clone attributes
            writer.clone_reader_document_root(reader)

            # Loop through pages and look for fields
            fields: dict[str, Any] | None = reader.get_fields()
            updates: dict[str, str] = {}
            if fields:
                for key in fields:
                    field: pypdf.generic.Field = fields[key]
                    field_val: str = ""
                    if field.value is not None:
                        field_val = str(object=field.value)
                        updates[key] = get_new_value(pdf_value=field_val, time_card=time_card, reference_time_card=reference_time_card, phase_sheet=phase_sheet, reference_phase_sheet=reference_phase_sheet, card_info=card_info)

            writer.update_page_form_field_values(page=writer.pages[0], fields=updates, auto_regenerate=False)

            writer.write(stream=output_pdf)

        print(f"Updated PDF saved to {output_pdf_path}")

    except:  # pylint: disable=W0702
        pass
    return None


if __name__ == "__main__":
    build_out_pdf(phase_sheet=pandas.DataFrame(), time_card=pandas.DataFrame(), card_info={})
