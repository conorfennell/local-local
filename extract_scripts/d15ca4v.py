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

    def _parse_time(self, time_str: str) -> str:
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
                
            # Get next occurrence of this time
            now = datetime.now()
            target_time = datetime.combine(now.date(), time_obj.time())
            
            # If the time has already passed today, move to tomorrow
            if target_time <= now:
                target_time += timedelta(days=1)
                
            return target_time.strftime('%Y-%m-%dT%H:%M:00Z')
            
        except Exception as e:
            logger.error(f"Error parsing time {time_str}: {e}")
            return None

    def _create_event(self, name: str, time_str: str, pattern: str = "Weekly") -> dict:
        """Create an event dictionary."""
        time_iso = self._parse_time(time_str)  # Removed the days parameter here
        if not time_iso:
            return None
            
        return {
            "name": f"{name} ({time_str})",
            "start_time": time_iso,
            "extracted_time": self.extracted_time,
            "extracted_url": self.venue_config["url"],
            "duration": "PT1H0M",
            "recurrence": pattern,
            "eircode": self.venue_config["eircode"],
            "longitude": self.venue_config["longitude"],
            "latitude": self.venue_config["latitude"]
        }

    def get_mass_schedule(self) -> list:
        """Extract mass schedule from the page."""
        events = []
        
        content = self.soup.find('div', {'itemprop': 'articleBody'})
        if not content:
            logger.error("Could not find main content")
            return events

        text = content.get_text()
        
        # Regular expressions with named groups for better clarity
        patterns = {
            # Weekday masses
            r'Monday to Friday:\s*(?:at\s*)?(?P<time>\d{1,2}(?::\d{2})?\s*(?:am|pm))': {
                'name': 'Weekday Mass',
                'days': ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
            },
            # Saturday vigil
            r'Saturday Vigil Mass:\s*(?:at\s*)?(?P<time>\d{1,2}(?::\d{2})?\s*(?:am|pm))': {
                'name': 'Vigil Mass',
                'days': ['SATURDAY']
            },
            # Sunday masses (with two times)
            r'Sunday Masses:\s*(?:at\s*)?(?P<time1>\d{1,2}(?::\d{2})?\s*(?:am|pm))(?:\s*and\s*)(?P<time2>\d{1,2}(?::\d{2})?\s*(?:am|pm))': {
                'name': 'Sunday Mass',
                'days': ['SUNDAY']
            }
        }

        # Look for special/one-off masses
        special_mass_pattern = r'(?P<date>\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December))\s*(?:at\s*)?(?P<time>\d{1,2}(?::\d{2})?\s*(?:am|pm))'
        special_masses = re.finditer(special_mass_pattern, text)
        
        # Process regular weekly masses
        for pattern, info in patterns.items():
            match = re.search(pattern, text)
            if match:
                if 'time1' in match.groupdict():  # Handle Sunday masses with two times
                    # First Sunday mass
                    event = self._create_event(
                        info['name'],
                        match.group('time1'),
                        info['days']
                    )
                    if event:
                        events.append(event)
                    
                    # Second Sunday mass
                    event = self._create_event(
                        info['name'],
                        match.group('time2'),
                        info['days']
                    )
                    if event:
                        events.append(event)
                else:
                    event = self._create_event(
                        info['name'],
                        match.group('time'),
                        info['days']
                    )
                    if event:
                        events.append(event)

        # Process special/one-off masses
        for match in special_masses:
            event = self._create_event(
                'Special Mass',
                match.group('time'),
                None,
                "ONCE"
            )
            if event:
                events.append(event)

        return events

def parse_d15ca4v():
    """Main function to fetch and parse website."""
    venue_config = {
        "url": "https://www.laurellodgeparish.ie/mass-times",
        "eircode": "d15ca4v",
        "latitude": 53.377527265212414,
        "longitude": -6.376180701572852,
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
