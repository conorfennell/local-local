from django.http import HttpResponse
from django.shortcuts import render

def home_age_view(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OpenStreetMap - Hello World</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
        <style>
            #map {
                height: 100vh; /* Full screen height */
                width: 100%;  /* Full screen width */
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            // Initialize the map and set its view to the desired coordinates and zoom level
            const map = L.map('map').setView([51.505, -0.09], 13); // Coordinates for London

            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);

            // Add a marker at the same coordinates
            L.marker([51.505, -0.09])
                .addTo(map)
                .bindPopup('Hello, OpenStreetMap!')
                .openPopup();
        </script>
    </body>
    </html>
    """)
