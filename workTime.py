'''
 # @ Description:
 # @ Author: Aaron Shackelford
 # @ Create Time: 2025-03-08 20:50:21
 # @ Modified by: Aaron Shackelford
 # @ Modified time: 2025-03-08 20:50:30
 '''

import datetime
import decimal

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
        self.day: datetime.date = datetime.date(year=2000,month=1,day=1)
        self.clock_times: list[ClockLine] = []
        self.final_line: FinalLine = FinalLine()

class WorkTime:
    def __init__(self) -> None:
        self.name: str = str()
        self.work_blocks: list[WorkBlock] = list[WorkBlock]()

