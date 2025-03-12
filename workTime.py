'''
 # @ Description:
 # @ Author: Aaron Shackelford
 # @ Create Time: 2025-03-08 20:50:21
 # @ Modified by: Aaron Shackelford
 # @ Modified time: 2025-03-08 20:50:30
 '''

import datetime
import decimal

# csv data example:                                                                         | Class relation:                       |
# ----------------------------------------------------------------------------------------- | ------------------------------------- |
# "10.010.0023 Automation Engineer - Overhead  total amount: $110.67  total time: 02:40:00" | WorkTime.name                         |
#                                                                                           |                                       |
# "","","Mar 3, 2025"                                                                       | WorkBlock.day | WorkTime.work_blocks  |
# "Start","End","Time","Amount","Note"                                                      |               |                       |
# "8:00:00 AM","8:30:00 AM","00:30:00","$20.75",""                                          | ClockLine     | WorkBlock.clock_times |
# "12:45:00 PM","1:00:00 PM","00:15:00","$10.38",""                                         | ClockLine     | WorkBlock.clock_times |
# "Total:     00:45:00               $31.13"                                                | FinalLine     | WorkBlock.final_line  |
#                                                                                           |                                       |
# "","","Mar 4, 2025"                                                                       | ...
# "Start","End","Time","Amount","Note"
# "8:00:00 AM","9:15:00 AM","01:15:00","$51.88",""
# "Total:     01:15:00               $51.88"
#
# ...                                                                                       | ...


class FinalLine:
    def __init__(self) -> None:
        self.line: str = str()
        self.total_time: datetime.timedelta = datetime.timedelta()
        self.total_money: decimal.Decimal = decimal.Decimal(0)


class ClockLine:
    def __init__(self) -> None:
        self.start_time: datetime.time = datetime.time()
        self.end_time: datetime.time = datetime.time()
        self.total_time: datetime.timedelta = datetime.timedelta()
        self.money: decimal.Decimal = decimal.Decimal(0)
        self.comment: str = str()


class WorkBlock:
    def __init__(self) -> None:
        self.day: datetime.date = datetime.date(year=2000, month=1, day=1)
        self.clock_times: list[ClockLine] = []
        self.final_line: FinalLine = FinalLine()


class WorkTime:
    def __init__(self) -> None:
        self.name: str = str()
        self.work_blocks: list[WorkBlock] = list[WorkBlock]()
