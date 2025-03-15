from datetime import datetime, timedelta



def epoc_convert(timestamp)  -> datetime:
    print(1742009763-timestamp)
    # Convert to a readable date
    readable_date = datetime.utcfromtimestamp(timestamp)

    # Print the result
    print("UTC Time:", readable_date.strftime('%Y-%m-%d %H:%M:%S'))
    return readable_date

dt0 = epoc_convert(759442500)
dt1 = epoc_convert(759459600)

dt2: timedelta = dt0-dt1
print(dt2)