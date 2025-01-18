import logging
import os
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
import json
from pathlib import Path

logger = logging.getLogger(__name__)

def local_view(request):
    return render(request, 'local.html')

def load_json_file(file_path):
    """
    Loads JSON data from a file.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logger.info(f"Successfully loaded data from {file_path}")
            return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
    return None

def events_view(request):
    """
    Load all JSON files from the extraction directory and combine their events.
    """
    events = []
    extraction_dir = Path('./extraction')
    
    # Ensure the extraction directory exists
    if not extraction_dir.exists():
        logger.warning("Extraction directory does not exist")
        return render(request, 'events_view.html', {'events': json.dumps([])})
    
    # Load all JSON files from the extraction directory
    json_files = extraction_dir.glob('*.json')
    for json_file in json_files:
        data = load_json_file(json_file)
        if data:
            events.extend(data)
            logger.info(f"Added {len(data)} events from {json_file.name}")
    
    context = {
        'events': json.dumps(events)
    }
    logger.info(f"Total events loaded: {len(events)}")
    return render(request, 'events_view.html', context)

class CommitInfo:
    @staticmethod
    def get_commit_info():
        return {
            'commit_id': os.getenv('COMMIT_ID', 'Unknown'),
            'commit_time': os.getenv('COMMIT_TIME', 'Unknown'), 
            'commit_message': os.getenv('COMMIT_MESSAGE', 'Unknown')
        }

def about_view(request):
    commit_info = CommitInfo.get_commit_info()
    return render(request, 'about.html', commit_info)

def web_data_viewer(request):
    template = loader.get_template('web_data_viewer.html')
    return HttpResponse(template.render({}, request))
