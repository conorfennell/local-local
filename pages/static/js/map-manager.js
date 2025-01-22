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
        const color = this.locationColors[`${location.lng},${location.lat}`];
        const marker = L.marker([location.lat, location.lng], {
            icon: L.divIcon({
                html: `
                    <div class="marker-pin">
                        <div style="position: relative;">
                            <div style="width: 24px; height: 24px; position: relative;">
                                <div style="
                                    background-color: ${color};
                                    width: 24px;
                                    height: 24px;
                                    border-radius: 50% 50% 50% 0;
                                    transform: rotate(-45deg);
                                    box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
                                    border: 2px solid white;
                                    position: absolute;
                                    top: 0;
                                    left: 0;
                                "></div>
                                <div style="
                                    width: 8px;
                                    height: 8px;
                                    background: white;
                                    border-radius: 50%;
                                    position: absolute;
                                    top: 8px;
                                    left: 8px;
                                    box-shadow: inset 0 0 2px rgba(0,0,0,0.3);
                                "></div>
                            </div>
                            <div style="
                                width: 24px;
                                height: 6px;
                                background: rgba(0,0,0,0.15);
                                border-radius: 50%;
                                position: absolute;
                                bottom: -3px;
                                left: 0;
                                filter: blur(2px);
                            "></div>
                        </div>
                    </div>
                `,
                className: 'custom-div-icon',
                iconSize: [24, 32],
                iconAnchor: [12, 32]
            })
        })
            .bindPopup(
                `<div class="popup-content" style="
                    min-width: 250px;
                    max-width: 300px;
                    padding: 12px;
                    font-family: 'Inter', sans-serif;
                ">` +
                events.map(event => `
                    <div class="event-popup" style="
                        background: white;
                        border-radius: 8px;
                        margin-bottom: 8px;
                    ">
                        <div style="
                            padding: 8px;
                            border-left: 4px solid ${color};
                            background: rgba(0,0,0,0.02);
                        ">
                            <h3 style="
                                color: #2d3748;
                                font-size: 16px;
                                font-weight: 600;
                                margin-bottom: 8px;
                            ">${event.name}</h3>
                            <div style="
                                color: #4a5568;
                                font-size: 14px;
                                margin-bottom: 8px;
                            ">${this.formatEventTime(event.start_time)}</div>
                            <a href="${event.extracted_url}" 
                               target="_blank"
                               style="
                                display: inline-block;
                                padding: 6px 12px;
                                background: ${color};
                                color: white;
                                text-decoration: none;
                                border-radius: 4px;
                                font-size: 13px;
                                font-weight: 500;
                                transition: opacity 0.2s;
                            "
                               onmouseover="this.style.opacity='0.8'"
                               onmouseout="this.style.opacity='1'"
                            >View Source</a>
                        </div>
                    </div>
                `).join('') +
                `</div>`,
                {
                    className: 'custom-popup'
                }
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

    createEventMarker(coords, color, title, startTime, extracted_url) {
        const marker = L.marker(coords, {
            icon: L.divIcon({
                html: `
                    <div class="marker-pin">
                        <div style="position: relative;">
                            <div style="width: 24px; height: 24px; position: relative;">
                                <div style="
                                    background-color: ${color};
                                    width: 24px;
                                    height: 24px;
                                    border-radius: 50% 50% 50% 0;
                                    transform: rotate(-45deg);
                                    box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
                                    border: 2px solid white;
                                    position: absolute;
                                    top: 0;
                                    left: 0;
                                "></div>
                                <div style="
                                    width: 8px;
                                    height: 8px;
                                    background: white;
                                    border-radius: 50%;
                                    position: absolute;
                                    top: 8px;
                                    left: 8px;
                                    box-shadow: inset 0 0 2px rgba(0,0,0,0.3);
                                "></div>
                            </div>
                            <div style="
                                width: 24px;
                                height: 6px;
                                background: rgba(0,0,0,0.15);
                                border-radius: 50%;
                                position: absolute;
                                bottom: -3px;
                                left: 0;
                                filter: blur(2px);
                            "></div>
                        </div>
                    </div>
                `,
                className: 'custom-div-icon',
                iconSize: [24, 32],
                iconAnchor: [12, 32]
            })
        }).bindPopup(`
            <div class="popup-content" style="
                min-width: 250px;
                max-width: 300px;
                padding: 12px;
                font-family: 'Inter', sans-serif;
            ">
                <div class="event-popup" style="
                    background: white;
                    border-radius: 8px;
                ">
                    <div style="
                        padding: 8px;
                        border-left: 4px solid ${color};
                        background: rgba(0,0,0,0.02);
                    ">
                        <h3 style="
                            color: #2d3748;
                            font-size: 16px;
                            font-weight: 600;
                            margin-bottom: 8px;
                        ">${title}</h3>
                        <div style="
                            color: #4a5568;
                            font-size: 14px;
                            margin-bottom: 8px;
                        ">${this.formatEventTime(startTime)}</div>
                        <a href="${extracted_url}" 
                           target="_blank"
                           style="
                            display: inline-block;
                            padding: 6px 12px;
                            background: ${color};
                            color: white;
                            text-decoration: none;
                            border-radius: 4px;
                            font-size: 13px;
                            font-weight: 500;
                            transition: opacity 0.2s;
                        "
                           onmouseover="this.style.opacity='0.8'"
                           onmouseout="this.style.opacity='1'"
                        >View Source</a>
                    </div>
                </div>
            </div>
        `, {
            className: 'custom-popup'
        });
        
        return marker;
    }
}
