import datetime
import workTime
import pandas

def run_time_table(header:list, time_table:pandas.DataFrame, work_list:list[workTime.WorkTime])->None:
    days:dict[str,list[datetime.time]] = {
        "Saturday":[], 
        "Sunday":[],
        "Monday":[], 
        "Tuesday":[], 
        "Wednesday":[], 
        "Thursday":[], 
        "Friday":[], 
    }
    
    for i in work_list:
        pass