import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta, timezone

def parse_castleknock_website():
    url = "https://www.castleknockcommunitycentre.ie/adults.html"
    extracted_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    eircode = "d15t3pn"
    longitude=53.37743855202611
    latitude=-6.378832062945247
    try:
        # Send a GET request to the website
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting activity information
        activities = []
        today = datetime.utcnow()
        day_map = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }

        for activity_section in soup.find_all('h2', class_='wsite-content-title'):
            day = activity_section.get_text(strip=True)
            paragraph = activity_section.find_next('div', class_='paragraph')

            if paragraph:
                for strong_tag in paragraph.find_all('strong'):
                    name_and_time = strong_tag.get_text(strip=True)
                    time_iso = "Unknown"
                    duration = "Unknown"

                    # Use regex to extract start and end times
                    time_matches = re.findall(r'(\d{1,2}(?:\.\d{1,2})?\s?(?:am|pm|AM|PM|a\.m\.|p\.m\.))', name_and_time, re.IGNORECASE)
                    if time_matches:
                        def convert_to_iso8601(t):
                            t = t.lower().replace('.', ':').strip()
                            if 'am' in t or 'pm' in t:
                                t = re.sub(r'\s?(am|pm)', '', t)
                                hours, minutes = (list(map(int, t.split(':'))) + [0])[:2]
                                if 'pm' in t and hours != 12:
                                    hours += 12
                                elif 'am' in t and hours == 12:
                                    hours = 0
                                return f"{hours:02}:{minutes:02}:00"
                            return t

                        start_time = convert_to_iso8601(time_matches[0])

                        # Calculate the correct date based on the day of the week
                        event_day = day_map.get(day, None)
                        if event_day is not None:
                            days_ahead = (event_day - today.weekday() + 7) % 7
                            event_date = today + timedelta(days=days_ahead)
                            time_iso = f"{event_date.strftime('%Y-%m-%dT')}{start_time}Z"

                        if len(time_matches) > 1:
                            end_time = convert_to_iso8601(time_matches[1])

                            # Calculate duration if both start and end times are available
                            start_hour, start_minute = map(int, start_time.split(':')[:2])
                            end_hour, end_minute = map(int, end_time.split(':')[:2])
                            start_minutes = start_hour * 60 + start_minute
                            end_minutes = end_hour * 60 + end_minute

                            if end_minutes > start_minutes:
                                duration_minutes = end_minutes - start_minutes
                                hours, minutes = divmod(duration_minutes, 60)
                                duration = f"PT{hours}H{minutes}M"
                            else:
                                duration = "Invalid time range"

                        name_and_time = re.sub(r'(\d{1,2}(?:\.\d{1,2})?\s?(?:am|pm|AM|PM|a\.m\.|p\.m\.))', "", name_and_time, flags=re.IGNORECASE).strip()

                    activities.append({
                        "name": name_and_time.strip(),
                        "time": time_iso.strip(),
                        "extracted_time": extracted_time,
                        "extracted_url": url,
                        "duration": duration.strip(),
                        "eircode": eircode,
                        "longitude": longitude,
                        "latitude": latitude
                    })

        print(json.dumps(activities, indent=4))

        # Save the extracted data to a JSON file
        with open(f"./extraction/{eircode}.json", 'w') as f:
            json.dump(activities, f, indent=4)

        # Save the HTML content to a file
        with open(f'./extraction/{eircode}.html', 'w') as f:
            f.write(soup.prettify())

    except requests.exceptions.RequestException as e:
        print("Error accessing the website:", e)
    except Exception as e:
        print("Error parsing the website:", e)


# Keep the script running
if __name__ == "__main__":
    print("Starting the recurring script...")
    parse_castleknock_website()
