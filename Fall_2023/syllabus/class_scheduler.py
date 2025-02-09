from datetime import datetime, timedelta
import pandas as pd

from datetime import datetime, timedelta


def next_tuesdays_thursdays(start_date, end_date):
    weekdays = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    
    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Initialize a current date variable
    current_date = start_date
    
    print("Next Tuesdays and Thursdays:")
    
    lectures = []
    
    # Loop through the dates and find the next Tuesdays and Thursdays
    while current_date <= end_date:
        if current_date.weekday() == weekdays['Tuesday']:
            lectures.append([current_date.strftime('%Y-%m-%d'), 'Tu.'])
        elif current_date.weekday() == weekdays['Thursday']:
            lectures.append([current_date.strftime('%Y-%m-%d'), 'Th.'])
        
        # Increment the current date
        current_date += timedelta(days=1)

    return lectures


def _format_academic_calendar(df: pd.DataFrame) -> pd.DataFrame:
    """Conver the first column to data format"""
    return df.rename(columns={0: 'date', 1: 'event'})


def _fetch_calendar():
    """
    Fetch the calendar from the registrar's website.
    """
    # URL of the registrar's calendar
    URL = "https://www.wm.edu/offices/registrar/calendarsandexams/ugcalendars"
    return pd.read_html(URL)[1]


def parse_dates(date_str: str, event: str = None) -> list:
    """
    Converts a date string into a list of datetime ranges.
    
    Args:
        date_str (str): The date string to convert
        event (str): The event name to associate with the date string
    
    Returns:
        list: A list of datetime ranges and associated event names
    """
    today = datetime.now()
    year = today.year
    ranges = []

    # Handle multi-month ranges like 'October 23 - November 3'
    if '-' in date_str and ',' not in date_str and len(date_str.split(' ')) > 3:
        month_start, date_start, _, month_end, date_end = date_str.split(' ')
        date_start = datetime.strptime(f"{year} {month_start} {date_start}", '%Y %B %d')
        date_end = datetime.strptime(f"{year} {month_end} {date_end}", '%Y %B %d')

        while date_start <= date_end:
            ranges.append(date_start)
            date_start += timedelta(days=1)
    
    # Handle single month, multiple ranges like 'December 9-10, 16-17'
    elif ',' in date_str:
        month, days = date_str.split(' ', 1)
        for day_range in days.split(','):
            day_start, day_end = map(int, day_range.strip().split('-'))
            date_start = datetime.strptime(f"{year} {month} {day_start}", '%Y %B %d')
            date_end = datetime.strptime(f"{year} {month} {day_end}", '%Y %B %d')

            while date_start <= date_end:
                ranges.append(date_start)
                date_start += timedelta(days=1)
                
    # Handle single-day or single-range in a month like 'August 16' or 'August 25-29'
    else:
        parts = date_str.split(' ')
        month = parts[0]
        
        if '-' in parts[1]:
            day_start, day_end = map(int, parts[1].split('-'))
        else:
            day_start = day_end = int(parts[1])
            
        date_start = datetime.strptime(f"{year} {month} {day_start}", '%Y %B %d')
        date_end = datetime.strptime(f"{year} {month} {day_end}", '%Y %B %d')
        
        while date_start <= date_end:
            ranges.append(date_start)
            date_start += timedelta(days=1)

    return [[ranges], len(ranges) * [event]]


def main() -> int:
    df = _fetch_calendar()
    academic_calendar = _format_academic_calendar(df)
    important_dates = academic_calendar['date'].values.tolist()
    date_events = academic_calendar['event'].values.tolist()
    
    df = pd.DataFrame()
    for d, e in zip(important_dates, date_events):
        if ', 2024' in d:
            # remove the year
            d = d.replace(', 2024', '')
        # add the dates to the dataframe
        df = pd.concat([df, (pd.DataFrame(parse_dates(d, e)[1], index=parse_dates(d, e)[0], columns=['event']))])
    # df = df.sort_index()
    df = df.reset_index().rename(columns={'level_0': 'date'})
    print(df.head())
    
    print(df.to_markdown('calendar.md'))
    
    # fetch the course lecture dates
    lectures = next_tuesdays_thursdays("2023-08-31", "2023-12-31")
    
    # generate the class calendar to coincide with the academic calendar
    class_calendar = pd.DataFrame(columns=['date', 'day', 'topic', 'reading', 'academic calendar'])
    
    # add the lectures and days to the class calendar
    for l_date, day in lectures:
        l_date = pd.to_datetime(l_date)
        exists = l_date in df['date'].values
        # add the lecture and day to the class calendar (no events in academic calendar)
        if not exists:
            class_calendar = pd.concat([class_calendar, pd.DataFrame([[l_date, day, '', '', '']], columns=['date', 'day', 'topic', 'reading', 'academic calendar'])])
        # add the lecture and day to the class calendar (with events in academic calendar)
        if exists:
            class_calendar = pd.concat([class_calendar, pd.DataFrame([[l_date, day, '', '', df[df['date'] == l_date]['event'].values[0]]], columns=['date', 'day', 'topic', 'reading', 'academic calendar'])])
    
    class_calendar = class_calendar.set_index('date')
    class_calendar.to_markdown('class_calendar.md')
    
    return 0
    
if __name__ == '__main__':
    raise SystemExit(main())
