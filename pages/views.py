from django.http import HttpResponse
from django.shortcuts import render
import json

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
            print("Data loaded successfully!")
            return data
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    return None


def home_age_view(request):
    events = load_json_file("./extraction/d15t3pn.json")
        # Prepare JavaScript markers from event data
    markers_js = ""
    for event in events:
        name = event.get("name", "Unknown Event").replace("'", "\\'")
        longitude = event.get("longitude", 0)
        latitude = event.get("latitude", 0)
        markers_js += f"""
            L.marker([{longitude}, {latitude}])
                .addTo(map)
                .bindPopup('<strong>{name}</strong>');
        """
    print(markers_js)
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OpenStreetMap - Hello World</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
        <style>
            #map {{
                height: 100vh; /* Full screen height */
                width: 100%;  /* Full screen width */
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            // Initialize the map and set its view to the desired coordinates and zoom level
            const map = L.map('map').setView([53.37743855202611, -6.378832062945247], 13); // Coordinates for London

            // Add OpenStreetMap tiles
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            // Add markers for all events
            {markers_js}
        </script>
    </body>
    </html>
    """)


def web_data_viewer(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Web Data Educational Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                background-color: #f4f4f9;
                margin: 20px;
            }
            h1 {
                color: #333;
            }
            .box {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            pre {
                background-color: #eee;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <h1>Educational Web Data Viewer</h1>
        <p>This page demonstrates what types of browser data websites can access. All information stays local and is not sent anywhere.</p>

        <div class="box">
            <h2>Cookies (for this site only)</h2>
            <pre id="cookies">Loading...</pre>
        </div>

        <div class="box">
            <h2>Local Storage Data</h2>
            <pre id="local-storage">Loading...</pre>
        </div>

        <div class="box">
            <h2>Session Storage Data</h2>
            <pre id="session-storage">Loading...</pre>
        </div>

        <div class="box">
            <h2>Browser and Device Information</h2>
            <pre id="browser-info">Loading...</pre>
        </div>

        <script>
            // Display Cookies
            document.getElementById('cookies').textContent = document.cookie || "No cookies set for this site.";

            // Display Local Storage
            const localStorageData = localStorage.length 
                ? JSON.stringify(localStorage, null, 2) 
                : "No local storage data.";
            document.getElementById('local-storage').textContent = localStorageData;

            // Display Session Storage
            const sessionStorageData = sessionStorage.length 
                ? JSON.stringify(sessionStorage, null, 2) 
                : "No session storage data.";
            document.getElementById('session-storage').textContent = sessionStorageData;

            // Display Browser and Device Information
            const browserInfo = `
                User Agent: ${navigator.userAgent}
                Platform: ${navigator.platform}
                Language: ${navigator.language}
                Cookies Enabled: ${navigator.cookieEnabled}
                Online: ${navigator.onLine}
                Screen Resolution: ${screen.width} x ${screen.height}
                Color Depth: ${screen.colorDepth}
                Pixel Depth: ${screen.pixelDepth}
            `;
            document.getElementById('browser-info').textContent = browserInfo;
        </script>
    </body>
    </html>
                        """)