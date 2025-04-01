from datetime import datetime

def format_gitlab_date(date_str):
    # Parse the input date
    parsed_date = datetime.strptime(date_str, '%A %B %d, %Y')

    # Get the day and determine the suffix
    day = parsed_date.day
    if 10 <= day <= 20:  # Special case for 11th-20th
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    # Format the date into the desired GitLab format
    formatted_date = parsed_date.strftime(f'%B {day}{suffix} %Y')
    return formatted_date

# Example usage:
date_str = 'Tuesday April 1, 2025'
formatted_date = format_gitlab_date(date_str)
print(formatted_date)  # Output: "April 1st 2025"