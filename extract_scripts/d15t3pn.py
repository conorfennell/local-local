import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActivityParser:
    def __init__(self, html: str, venue_config: dict):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.venue_config = venue_config
        self.extracted_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.today = datetime.utcnow()
        self.day_map = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6,
        }

    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\u200b', '', text)  # Remove zero-width space
        text = re.sub(r'\s*-\s*$', '', text)  # Remove trailing dashes
        return text

    def _parse_time(self, time_str: str, event_day: str) -> tuple[str, str]:
        """Parse time string into ISO time and duration."""
        time_matches = re.findall(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))', time_str.lower())
        if not time_matches:
            return None, "Unknown"
            
        def convert_time(t: str) -> tuple[int, int]:
            t = t.replace('.', ':').strip()
            meridiem = 'am' if 'am' in t else 'pm'
            t = t.replace(meridiem, '').strip()
            
            if ':' in t:
                hour, minute = map(int, t.split(':'))
            else:
                hour, minute = int(t), 0
                
            if meridiem == 'pm' and hour != 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0
                
            return hour, minute

        start_hour, start_minute = convert_time(time_matches[0])
        
        # Calculate event date
        day_index = self.day_map.get(event_day)
        if day_index is not None:
            days_ahead = (day_index - self.today.weekday() + 7) % 7
            event_date = self.today + timedelta(days=days_ahead)
            time_iso = f"{event_date.strftime('%Y-%m-%dT')}{start_hour:02d}:{start_minute:02d}:00Z"
        else:
            time_iso = None

        # Calculate duration if end time exists
        duration = "Unknown"
        if len(time_matches) > 1:
            end_hour, end_minute = convert_time(time_matches[1])
            duration_mins = ((end_hour * 60 + end_minute) - 
                           (start_hour * 60 + start_minute))
            
            if duration_mins <= 0:  # Handle overnight events
                duration_mins += 24 * 60
                
            hours, minutes = divmod(duration_mins, 60)
            duration = f"PT{hours}H{minutes}M"
            
        return time_iso, duration

    def parse_activities(self) -> list[dict]:
        """Parse activities from HTML."""
        activities = []
        
        for day_heading in self.soup.find_all('h2', class_='wsite-content-title'):
            day = day_heading.get_text(strip=True)
            if day not in self.day_map:
                continue
                
            paragraph = day_heading.find_next('div', class_='paragraph')
            if not paragraph:
                continue
                
            for strong_tag in paragraph.find_all('strong'):
                name_and_time = strong_tag.get_text(strip=True)
                
                # Extract times using regex
                time_matches = re.findall(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)(?:\s*-\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?)', name_and_time, re.IGNORECASE)
                if time_matches:
                    time_str = time_matches[0]
                    name = re.sub(time_str, '', name_and_time, flags=re.IGNORECASE).strip()
                    time_iso, duration = self._parse_time(time_str, day)
                    
                    if time_iso:
                        activities.append({
                            "name": self._clean_text(name),
                            "start_time": time_iso,
                            "extracted_time": self.extracted_time,
                            "extracted_url": self.venue_config["url"],
                            "duration": duration,
                            "recurrence": "Weekly",
                            "eircode": self.venue_config["eircode"],
                            "longitude": self.venue_config["longitude"],
                            "latitude": self.venue_config["latitude"]
                        })
                        
        return activities

def parse_castleknock_website():
    """Main function to fetch and parse website."""
    venue_config = {
        "url": "https://www.castleknockcommunitycentre.ie/adults.html",
        "eircode": "d15t3pn",
        "longitude":  53.37743855202611,
        "latitude": -6.378832062945247
    }
    
    output_dir = Path('./extraction')
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Fetch webpage
        response = requests.get(venue_config['url'], timeout=30)
        response.raise_for_status()
        
        # Parse activities
        parser = ActivityParser(response.text, venue_config)
        activities = parser.parse_activities()
        
        # Save to JSON
        json_path = output_dir / f"{venue_config['eircode']}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(activities, f, indent=2)
        
        # Save HTML
        html_path = output_dir / f"{venue_config['eircode']}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        logger.info(f"Saved {len(activities)} activities")
        
    except Exception as e:
        logger.error(f"Error: {e}")
