class MapManager {
    constructor(mapId, initialView, tileLayerUrl) {
        this.map = L.map(mapId).setView(initialView, 13);
        L.tileLayer(tileLayerUrl, {
            attribution: '© OpenStreetMap contributors, © CARTO'
        }).addTo(this.map);
        this.markers = L.layerGroup().addTo(this.map);
        this.locationColors = {};
    }

    generateLocationColors(events) {
        events.forEach(event => {
            const key = `${event.longitude},${event.latitude}`;
            if (!this.locationColors[key]) {
                this.locationColors[key] = this.getRandomColor();
            }
        });
        return this.locationColors;
    }

    getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    clearMarkers() {
        this.markers.clearLayers();
    }

    addLocationMarker(location, events) {
        console.log('Adding marker at:', location, 'with events:', events);
        const marker = L.marker([location.lat, location.lng])
            .bindPopup(
                `<div class="popup-content">` +
                events.map(event => `
                    <div class="event-popup">
                        <strong>${event.name}</strong>
                        <div>${this.formatEventTime(event.start_time)}</div>
                    </div>
                `).join('<hr>') +
                `</div>`
            );
        this.markers.addLayer(marker);
    }

    formatEventTime(timeString) {
        try {
            const date = new Date(timeString);
            if (isNaN(date.getTime())) return 'Invalid time';
            return date.toLocaleString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                hour12: true
            });
        } catch (e) {
            return 'Invalid time';
        }
    }

    setView(coords, zoom) {
        this.map.setView(coords, zoom);
    }

    createEventMarker(coords, color, title, startTime) {
        const marker = L.marker(coords, {
            icon: L.divIcon({
                html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>`,
                className: 'custom-div-icon',
                iconSize: [12, 12],
                iconAnchor: [6, 6]
            })
        }).bindPopup(`<strong>${title}</strong><br>${new Date(startTime).toLocaleString()}`);
        
        return marker;
    }
}
