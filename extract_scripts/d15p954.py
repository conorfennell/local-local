import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChurchEventParser:
    def __init__(self, html: str, venue_config: dict):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.venue_config = venue_config
        self.extracted_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\u200b', '', text)  # Remove zero-width space
        text = re.sub(r'\s*-\s*$', '', text)  # Remove trailing dashes
        text = text.replace('[&hellip;]', '')
        return text

    def _parse_time(self, event_date: str, time_text: str) -> tuple[str, str]:
        """Parse date and time string into ISO time and duration."""
        try:
            # Extract time using regex
            time_pattern = r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))'
            times = re.findall(time_pattern, time_text.lower())
            
            if not times:
                return None, "Unknown"

            # Parse start time
            start_time = times[0].strip()
            # Remove extra spaces and ensure proper format for AM/PM
            start_time = re.sub(r'\s+(am|pm)', r'\1', start_time)
            start_dt = datetime.strptime(f"{event_date} {start_time}", "%Y-%m-%d %I:%M%p")
            time_iso = start_dt.strftime('%Y-%m-%dT%H:%M:00Z')

            # Calculate duration if end time exists
            duration = "PT1H0M"  # Default 1 hour
            if len(times) > 1:
                end_time = times[1].strip()
                # Remove extra spaces and ensure proper format for AM/PM
                end_time = re.sub(r'\s+(am|pm)', r'\1', end_time)
                end_dt = datetime.strptime(f"{event_date} {end_time}", "%Y-%m-%d %I:%M%p")
                
                duration_mins = int((end_dt - start_dt).total_seconds() / 60)
                if duration_mins <= 0:  # Handle overnight events
                    duration_mins += 24 * 60
                    
                hours, minutes = divmod(duration_mins, 60)
                duration = f"PT{hours}H{minutes}M"
                
            return time_iso, duration

        except Exception as e:
            logger.error(f"Error parsing time: {e}")
            return None, "Unknown"

    def parse_events(self) -> list[dict]:
        """Parse all events from the HTML."""
        events = []
        event_rows = self.soup.find_all('article', class_='tribe-events-calendar-list__event')
        
        for event_row in event_rows:
            try:
                # Get event name
                name_elem = event_row.find('h3', class_='tribe-events-calendar-list__event-title')
                if not name_elem or not name_elem.find('a'):
                    continue
                name = self._clean_text(name_elem.find('a').text)
                
                # Get date and time
                datetime_elem = event_row.find('time', class_='tribe-events-calendar-list__event-datetime')
                if not datetime_elem:
                    continue
                    
                # Extract date from parent date tag
                date_tag = event_row.find_previous('time', class_='tribe-events-calendar-list__event-date-tag-datetime')
                if not date_tag:
                    continue
                    
                event_date = date_tag.get('datetime')
                if not event_date:
                    continue
                    
                # Parse time and duration
                time_text = datetime_elem.text.strip()
                time_iso, duration = self._parse_time(event_date, time_text)
                
                if not time_iso:
                    continue
                    
                events.append({
                    "name": name,
                    "start_time": time_iso,
                    "extracted_time": self.extracted_time,
                    "extracted_url": self.venue_config["url"],
                    "duration": duration,
                    "recurrence": "Weekly", # Default to weekly
                    "eircode": self.venue_config["eircode"],
                    "longitude": self.venue_config["longitude"], 
                    "latitude": self.venue_config["latitude"]
                })
                
            except Exception as e:
                logger.error(f"Error parsing event: {e}")
                continue
                
        return events

def parse_d15p954():
    """Main function to fetch and parse website."""
    venue_config = {
        "url": "https://castleknock.dublin.anglican.org/events/",
        "eircode": "d15p954",
        "longitude":  53.37379251866193,
        "latitude": -6.362814323860707
    }
    
    output_dir = Path('./extraction')
    output_dir.mkdir(exist_ok=True)
    try:
        # Fetch webpage
        response = requests.get(venue_config['url'], timeout=30)
        response.raise_for_status()
        
        # Parse activities
        parser = ChurchEventParser(response.text, venue_config)
        activities = parser.parse_events()
        
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
