import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LaurelLodgeParser:
    def __init__(self, html: str, venue_config: dict):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.venue_config = venue_config
        self.extracted_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        text = re.sub(r'\s+', ' ', text.strip())
        return text

    def _parse_time(self, time_str: str, day_name: str = None) -> str:
        """Convert time string to ISO format."""
        # Handle special cases
        if time_str.lower() == "vigil":
            time_str = "6:30pm"  # Based on the current schedule
            
        # Remove any extra whitespace and convert to lowercase
        time_str = time_str.strip().lower()
        
        try:
            # Parse time
            if ":" in time_str:
                time_obj = datetime.strptime(time_str, "%I:%M%p")
            else:
                time_obj = datetime.strptime(time_str, "%I%p")
                
            # Get current date
            today = datetime.now()
            
            # If day_name is provided, adjust the date to the next occurrence of that day
            if day_name:
                # Convert day name to weekday number (0 = Monday, 6 = Sunday)
                day_map = {
                    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
                    'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
                }
                target_day = day_map[day_name]
                current_day = today.weekday()
                days_ahead = target_day - current_day
                
                if days_ahead <= 0:  # Target day has passed this week
                    days_ahead += 7
                    
                target_date = today + timedelta(days=days_ahead)
                datetime_obj = datetime.combine(target_date.date(), time_obj.time())
            else:
                datetime_obj = datetime.combine(today.date(), time_obj.time())
                
            return datetime_obj.strftime('%Y-%m-%dT%H:%M:00Z')
        except Exception as e:
            logger.error(f"Error parsing time {time_str}: {e}")
            return None

    def get_mass_schedule(self) -> list:
        """Extract mass schedule from the page."""
        events = []
        
        # Find the main content
        content = self.soup.find('div', {'itemprop': 'articleBody'})
        if not content:
            logger.error("Could not find main content")
            return events

        # Extract text content
        text = content.get_text()
        
        # Regular expressions for different mass times
        patterns = {
            r'Monday to Friday:\s*(?:at\s*)?(\d{1,2}(?::\d{2})?\s*(?:am|pm))': {
                'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                'name': 'Weekday Mass'
            },
            r'Saturday Vigil Mass:\s*(?:at\s*)?(\d{1,2}(?::\d{2})?\s*(?:am|pm))': {
                'days': ['Saturday'],
                'name': 'Vigil Mass'
            },
            r'Sunday Masses:\s*(?:at\s*)?(\d{1,2}(?::\d{2})?\s*(?:am|pm))(?:\s*and\s*)?(\d{1,2}(?::\d{2})?\s*(?:am|pm))': {
                'days': ['Sunday'],
                'name': 'Sunday Mass'
            }
        }

        # Process each pattern
        for pattern, info in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):  # Multiple times (e.g., Sunday)
                    times = matches[0]
                else:  # Single time
                    times = [matches[0]]

                for time_str in times:
                    for day in info['days']:
                        time_iso = self._parse_time(time_str, day)
                        if time_iso:
                            events.append({
                                "name": f"{info['name']} ({time_str})",
                                "start_time": time_iso,
                                "extracted_time": self.extracted_time,
                                "extracted_url": self.venue_config["url"],
                                "duration": "PT1H0M",  # Standard 1-hour duration
                                "recurrence": "Weekly",
                                "eircode": self.venue_config["eircode"],
                                "longitude": self.venue_config["longitude"],
                                "latitude": self.venue_config["latitude"]
                            })

        return events

def parse_d15ca4v():
    """Main function to fetch and parse website."""
    venue_config = {
        "url": "https://www.laurellodgeparish.ie/mass-times",
        "eircode": "d15ca4v",
        "longitude": 53.377527265212414,
        "latitude": -6.376180701572852
    }
    
    output_dir = Path('./extraction')
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Fetch webpage
        response = requests.get(venue_config['url'], timeout=30)
        response.raise_for_status()
        
        # Parse activities
        parser = LaurelLodgeParser(response.text, venue_config)
        activities = parser.get_mass_schedule()
        
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
