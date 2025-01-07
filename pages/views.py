import logging
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
import json

logger = logging.getLogger(__name__)

def load_json_file(file_path):
    """
    Loads JSON data from a file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or list: The parsed JSON data.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logger.info("Data loaded successfully!")
            return data
    except FileNotFoundError:
        logger.error(f"The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
    return None


def events_view(request):
    events = []
    for file_path in ["./extraction/d15t3pn.json", "./extraction/d15p954.json", "./extraction/d15ca4v.json"]:
        data = load_json_file(file_path)
        if data:
            events.extend(data)
    context = {
        'events': json.dumps(events)
    }
    print(context)
    return render(request, 'events_view.html', context)


def about_view(request):
    commit_id = os.getenv('COMMIT_ID', 'Unknown')
    return render(request, 'about.html', {'commit_id': commit_id})

def web_data_viewer(request):
    template = loader.get_template('web_data_viewer.html')
    return HttpResponse(template.render({}, request))
