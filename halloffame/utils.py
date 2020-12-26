# File: utils.py
# Creation: Friday December 4th 2020
# Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin


from datetime import datetime, timedelta


def xpath_soup(element):
    """Retrieve the ``xpath`` of a ``BeautifulSoup`` element.

    Args:
        element (bs4.Element): ``BeautifulSoup`` element.

    Returns:
        str
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


WEEK = {
    "Mon": "Monday",
    "Tue": "Tuesday",
    "Wed": "Wednesday",
    "Thu": "Thursday",
    "Fri": "Friday",
    "Sat": "Saturday",
    "Sun": "Sunday"
}

MONTHS = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12"
}


def convert_date(datestring):
    """Convert a facebook date to a datetime object.

    Args:
        datestring (str): The facebook date extracted from a post/comment.

    Returns:
        datetime.datetime


    Examples:
        >>> datestring = "on Sun"
        >>> convert_date(datestring)
            datetime.datetime(2020, 11, 29, 10, 49, 9, 708631)
        >>> datestring = "Aug 7, 2019"
        >>> convert_date(datestring)
            datetime.datetime(2019, 8, 7, 10, 49)
        >>> datestring = "November 30 at 4:51 PM"
        >>> convert_date(datestring)
            datetime.datetime(2019, 12, 12, 8, 18)
    """

    current_datetime = datetime.now()

    # For "on Tue" of "last Fri" dates
    if datestring.split(" ")[0] == "on" or datestring.split(" ")[0] == "last":
        posted_day = WEEK[datestring.split(" ")[1]]
        posted_datetime = current_datetime

        counter = 0
        while posted_datetime.strftime("%A") != posted_day and counter < 10:
            posted_datetime += timedelta(days=-1)
            counter += 1

    # For "12 hrs" dates
    elif datestring.split(" ")[-1] == "hrs":
        delta_hours = int(datestring.split(" ")[0])
        posted_datetime = current_datetime + timedelta(hours=-delta_hours)

    # For "1 wk" dates
    elif datestring.split(" ")[-1] == "wk" or datestring.split(" ")[-1] == "wks":
        delta_week = int(datestring.split(" ")[0])
        posted_datetime = current_datetime + timedelta(days=-7 * delta_week)

    # For "November 17, 2019 at 15:45 PM", "November 17" etc. dates
    else:
        year = current_datetime.year
        month = current_datetime.month
        day = current_datetime.day
        hour = current_datetime.hour
        minute = current_datetime.minute

        for month_string in MONTHS.keys():
            if month_string + " " in datestring or month_string[:3] + " " in datestring:
                month = MONTHS[month_string].replace(",", "")
                day = datestring.split(" ")[1].replace(",", "")

                if ", " in datestring:
                    year = datestring.split(", ")[1].split(" ")[0]
                if "at" in datestring:
                    time_string = datestring.split(" ")[-2]
                    hour, minute = time_string.split(":")
                    ampm = datestring.split(" ")[-1]
                    if ampm == "PM":
                        hour = int(hour) + 12
        # To isoformat
        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)

        posted_datetime = datetime.fromisoformat(f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}")

    return posted_datetime
