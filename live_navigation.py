"""
Live Turn-by-Turn Navigation Engine (Google Maps Style)
Built with Leaflet.js, OpenStreetMap, OSRM, Geolocation API, and SpeechSynthesis API.
100% Free Open-Source Architecture (₹0 API Cost). Zero Emojis.
"""

import json
import html

def generate_navigation_component(
    origin_name, origin_lat, origin_lon,
    dest_name, dest_lat, dest_lon,
    route_coords, directions,
    distance_km, duration_min,
    is_emergency=True,
    emergency_priority="Priority 1 - Critical Trauma (Immediate Clearance)"
):
    """
    Generates a self-contained Google Maps-style live turn-by-turn navigation web app
    with real-time GPS tracking, moving map following, voice prompts, automatic route progress,
    automatic rerouting on wrong turns, and simulated test drive for evaluation.
    """
    clean_orig_name = html.escape(str(origin_name))
    clean_dest_name = html.escape(str(dest_name))
    
    # Safe JSON payloads
    coords_json = json.dumps(route_coords)
    directions_json = json.dumps(directions)
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>Live Road Navigation System</title>
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }}
        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #070d19;
            color: #f8fafc;
        }}
        #nav-app-container {{
            position: relative;
            width: 100%;
            height: 100%;
            background-color: #070d19;
        }}
        #map {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            background: #0b1324;
        }}
        
        /* Top Navigation Header HUD - Compact, High-Visibility Design */
        .hud-top-card {{
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 1000;
            max-width: 380px;
            width: calc(100% - 24px);
            background: rgba(11, 20, 38, 0.94);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 12px;
            padding: 10px 14px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: all 0.3s ease;
        }}
        .hud-main-row {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .turn-icon-box {{
            width: 42px;
            height: 42px;
            border-radius: 10px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
        }}
        .turn-icon-box.arrive {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
        }}
        .turn-icon-box svg {{
            width: 26px;
            height: 26px;
            fill: #ffffff;
        }}
        .turn-text-group {{
            flex-grow: 1;
            overflow: hidden;
        }}
        .turn-dist-count {{
            font-size: 1.25rem;
            font-weight: 800;
            color: #f8fafc;
            letter-spacing: -0.02em;
            line-height: 1.1;
            margin-bottom: 2px;
        }}
        .turn-road-title {{
            font-size: 0.92rem;
            font-weight: 600;
            color: #38bdf8;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .turn-instruct-sub {{
            font-size: 0.74rem;
            color: #94a3b8;
            margin-top: 1px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .hud-then-row {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.72rem;
            color: #94a3b8;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            padding-top: 5px;
            margin-top: 2px;
        }}
        .then-tag {{
            text-transform: uppercase;
            font-weight: 700;
            font-size: 0.64rem;
            color: #64748b;
            letter-spacing: 0.05em;
        }}
        .then-detail {{
            color: #cbd5e1;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .hud-quick-stats {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid rgba(255, 255, 255, 0.07);
            padding-top: 5px;
            margin-top: 2px;
            font-size: 0.72rem;
            color: #94a3b8;
        }}
        .hud-stat-item strong {{
            color: #38bdf8;
            font-weight: 700;
        }}
        .hud-stat-divider {{
            color: rgba(255, 255, 255, 0.15);
        }}

        /* Reroute Alert Banner */
        .reroute-pill {{
            display: none;
            position: absolute;
            top: 18px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1001;
            background: #f59e0b;
            color: #0f172a;
            font-weight: 700;
            font-size: 0.82rem;
            padding: 7px 18px;
            border-radius: 9999px;
            box-shadow: 0 4px 16px rgba(245, 158, 11, 0.45);
            animation: pulseBanner 1.5s infinite;
        }}
        @keyframes pulseBanner {{
            0%, 100% {{ transform: translateX(-50%) scale(1); }}
            50% {{ transform: translateX(-50%) scale(1.05); }}
        }}

        /* Floating GPS Status Pill */
        .gps-status-pill {{
            position: absolute;
            top: 12px;
            right: 12px;
            z-index: 1000;
            background: rgba(11, 20, 38, 0.9);
            border: 1px solid rgba(56, 189, 248, 0.25);
            backdrop-filter: blur(8px);
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 0.72rem;
            color: #cbd5e1;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .gps-indicator {{
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10b981;
        }}
        @media (max-width: 640px) {{
            .hud-top-card {{
                max-width: calc(100% - 24px);
            }}
            .gps-status-pill {{
                top: auto;
                bottom: 120px;
                right: 12px;
            }}
        }}

        /* Leaflet OpenStreetMap Attribution Styling */
        .leaflet-control-attribution {{
            margin-bottom: 74px !important;
            margin-right: 8px !important;
            background: rgba(11, 20, 38, 0.8) !important;
            color: #94a3b8 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 4px !important;
            padding: 2px 6px !important;
            font-size: 10px !important;
        }}
        .leaflet-control-attribution a {{
            color: #38bdf8 !important;
            text-decoration: none !important;
        }}

        /* Floating Controls on Right */
        .floating-action-bar {{
            position: absolute;
            bottom: 120px;
            right: 14px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .btn-float {{
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: rgba(15, 23, 42, 0.92);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: #f8fafc;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
            transition: all 0.2s ease;
        }}
        .btn-float:hover {{
            background: #1e293b;
            border-color: #38bdf8;
            transform: scale(1.05);
        }}
        .btn-float svg {{
            width: 20px;
            height: 20px;
            fill: #38bdf8;
        }}
        .btn-recenter {{
            display: none;
            background: rgba(14, 165, 233, 0.2);
            border-color: #38bdf8;
        }}

        /* Bottom Trip Bar */
        .hud-bottom-bar {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: rgba(11, 20, 38, 0.96);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-top: 1px solid rgba(56, 189, 248, 0.25);
            padding: 12px 18px 14px 18px;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.4);
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .trip-metrics-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .trip-eta-group {{
            display: flex;
            align-items: baseline;
            gap: 10px;
        }}
        .trip-time-rem {{
            font-size: 1.4rem;
            font-weight: 800;
            color: #10b981;
        }}
        .trip-dist-rem {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #94a3b8;
        }}
        .trip-clock-eta {{
            font-size: 0.8rem;
            color: #64748b;
        }}
        .priority-badge-pill {{
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #34d399;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .bottom-action-buttons {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .btn-nav {{
            flex: 1;
            padding: 9px 12px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s ease;
        }}
        .btn-primary-start {{
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
        }}
        .btn-primary-start:hover {{
            background: #0284c7;
        }}
        .btn-pause {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #f1f5f9;
        }}
        .btn-pause:hover {{
            background: rgba(255, 255, 255, 0.14);
        }}
        .btn-end {{
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #f87171;
        }}
        .btn-end:hover {{
            background: rgba(239, 68, 68, 0.25);
        }}

        /* Test Mode Bar */
        .test-mode-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 0.72rem;
            color: #94a3b8;
        }}
        .test-btn {{
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: #38bdf8;
            padding: 2px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.7rem;
            font-weight: 600;
        }}
        .test-btn:hover {{
            background: rgba(56, 189, 248, 0.25);
        }}
        .wrong-turn-btn {{
            background: rgba(245, 158, 11, 0.15);
            border-color: rgba(245, 158, 11, 0.35);
            color: #fbbf24;
        }}

        /* Custom Vehicle Navigation Arrow Marker */
        .vehicle-marker-wrapper {{
            position: relative;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .vehicle-pulse-ring {{
            position: absolute;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(56, 189, 248, 0.25);
            animation: radarPulse 1.8s infinite ease-out;
        }}
        .vehicle-arrow-svg {{
            position: relative;
            z-index: 2;
            width: 28px;
            height: 28px;
            filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.6));
            transition: transform 0.3s ease;
        }}
        @keyframes radarPulse {{
            0% {{ transform: scale(0.6); opacity: 1; }}
            100% {{ transform: scale(1.6); opacity: 0; }}
        }}
    </style>
</head>
<body>

<div id="nav-app-container">
    <!-- Map Container -->
    <div id="map"></div>

    <!-- Top Navigation HUD -->
    <div class="hud-top-card" id="hud-top">
        <div class="hud-main-row">
            <div class="turn-icon-box" id="turn-icon-container">
                <svg viewBox="0 0 24 24" id="turn-svg-icon">
                    <path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z" />
                </svg>
            </div>
            <div class="turn-text-group">
                <div class="turn-dist-count" id="hud-turn-dist">Start Navigation</div>
                <div class="turn-road-title" id="hud-road-name">{clean_orig_name}</div>
                <div class="turn-instruct-sub" id="hud-instruction">Destination: {clean_dest_name}</div>
            </div>
        </div>
        <div class="hud-then-row" id="hud-then-container">
            <span class="then-tag">Then</span>
            <span class="then-detail" id="hud-then-text">Proceed along corridor towards destination</span>
        </div>
        <div class="hud-quick-stats" id="hud-quick-stats">
            <span class="hud-stat-item"><strong id="hud-quick-dist">{distance_km:.2f} km</strong> rem</span>
            <span class="hud-stat-divider">|</span>
            <span class="hud-stat-item"><strong id="hud-quick-eta">{duration_min:.1f} min</strong> ETA</span>
            <span class="hud-stat-divider">|</span>
            <span class="hud-stat-item"><strong id="hud-quick-speed">0.0 km/h</strong></span>
        </div>
    </div>

    <!-- Reroute Notification -->
    <div class="reroute-pill" id="reroute-alert">
        Off Route — Recalculating Navigation...
    </div>

    <!-- Floating Live GPS Status -->
    <div class="gps-status-pill">
        <span class="gps-indicator" id="gps-dot"></span>
        <strong id="gps-status-text">GPS Standby</strong>
        <span style="color: rgba(255,255,255,0.2);">|</span>
        <span id="gps-acc-text">± 8m</span>
    </div>

    <!-- Floating Right Map Controls -->
    <div class="floating-action-bar">
        <button class="btn-float btn-recenter" id="btn-recenter" onclick="recenterMap()" title="Recenter on vehicle">
            <svg viewBox="0 0 24 24">
                <path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm8.94 3c-.46-4.17-3.77-7.48-7.94-7.94V1h-2v2.06C6.83 3.52 3.52 6.83 3.06 11H1v2h2.06c.46 4.17 3.77 7.48 7.94 7.94V23h2v-2.06c4.17-.46 7.48-3.77 7.94-7.94H23v-2h-2.06zM12 19c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z"/>
            </svg>
        </button>
        <button class="btn-float" id="btn-voice-toggle" onclick="toggleVoice()" title="Toggle voice guidance">
            <svg viewBox="0 0 24 24" id="voice-svg-icon">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
        </button>
    </div>

    <!-- Bottom Trip Bar -->
    <div class="hud-bottom-bar">
        <!-- Interactive Evaluator Test Drive Bar -->
        <div class="test-mode-bar">
            <span>Evaluation Mode:</span>
            <div style="display: flex; gap: 6px;">
                <button class="test-btn" id="btn-toggle-mode" onclick="toggleTrackingMode()">Switch to Test Drive Simulator</button>
                <button class="test-btn wrong-turn-btn" id="btn-wrong-turn" onclick="simulateWrongTurn()" style="display: none;">Simulate Wrong Turn (Test Rerouting)</button>
            </div>
        </div>

        <div class="trip-metrics-row">
            <div class="trip-eta-group">
                <span class="trip-time-rem" id="trip-time-val">{duration_min:.1f} min</span>
                <span class="trip-dist-rem" id="trip-dist-val">{distance_km:.2f} km</span>
                <span class="trip-clock-eta" id="trip-eta-val">Calculating ETA</span>
            </div>
            <div class="priority-badge-pill" id="priority-tag">
                {"GREEN WAVE PRIORITY CORRIDOR" if is_emergency else "CONNECTED ROUTE"}
            </div>
        </div>

        <div class="bottom-action-buttons">
            <button class="btn-nav btn-primary-start" id="btn-start-nav" onclick="startNavigation()">
                Start Live Navigation
            </button>
            <button class="btn-nav btn-pause" id="btn-pause-nav" onclick="togglePauseNav()" style="display: none;">
                Pause
            </button>
            <button class="btn-nav btn-end" id="btn-end-nav" onclick="endNavigation()" style="display: none;">
                End Navigation
            </button>
        </div>
    </div>
</div>

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

<script>
    // --- Initial Route Data Payloads ---
    let routeCoords = {coords_json};
    let routeSteps = {directions_json};
    const destCoords = [{dest_lat}, {dest_lon}];
    const originCoords = [{origin_lat}, {origin_lon}];
    const destName = "{clean_dest_name}";
    const isEmergencyMode = {str(is_emergency).lower()};

    // --- State Variables ---
    let map = null;
    let completedPolyline = null;
    let remainingPolyline = null;
    let vehicleMarker = null;
    let accuracyCircle = null;
    let destMarker = null;

    let isNavigating = false;
    let isPaused = false;
    let isAutoFollow = true;
    let voiceEnabled = true;
    let trackingMode = "GPS"; // "GPS" or "SIMULATION"

    let watchId = null;
    let simInterval = null;
    let simIdx = 0;
    let simSpeedMultiplier = 1;

    let currentStepIdx = 0;
    let currentUserPos = [originCoords[0], originCoords[1]];
    let currentHeading = 0;
    let currentSpeedKmh = 0;
    let currentAccuracyM = 10;
    let offRouteConsecutiveCount = 0;
    let isRerouting = false;
    let lastSpokenStep = -1;
    let lastSpokenType = "";

    // SVG Icons Map
    const TURN_ICONS = {{
        "depart": '<path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/>',
        "arrive": '<path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z"/>',
        "straight": '<path d="M12 4l-5 5h3v10h4V9h3z"/>',
        "turn_right": '<path d="M15.5 5.5l5 5-5 5v-3h-4c-2.2 0-4 1.8-4 4v3h-3v-3c0-3.9 3.1-7 7-7h4v-4z"/>',
        "turn_left": '<path d="M8.5 5.5l-5 5 5 5v-3h4c2.2 0 4 1.8 4 4v3h3v-3c0-3.9-3.1-7-7-7h-4v-4z"/>',
        "turn_slight right": '<path d="M14.5 6.5l4.5 2.5-2.5 4.5-2.1-1.2c-2.4 2.8-3.4 5.7-3.4 8.7h-3c0-3.7 1.3-7.3 4.2-10.7l-2.2-1.3 4.5-2.5z"/>',
        "turn_slight left": '<path d="M9.5 6.5l-4.5 2.5 2.5 4.5 2.1-1.2c2.4 2.8 3.4 5.7 3.4 8.7h3c0-3.7-1.3-7.3-4.2-10.7l2.2-1.3-4.5-2.5z"/>',
        "merge": '<path d="M7 3v6.2c0 3.3 2.7 6 6 6h4v-3l5 4-5 4v-3h-4c-4.4 0-8-3.6-8-8V3h2z"/>',
        "roundabout": '<path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm1 17.9v-3h-2v3c-3.9-.5-7-3.6-7.5-7.5h3v-2h-3C4 8.5 7.1 5.4 11 4.9v3h2v-3c3.9.5 7 3.6 7.5 7.5h-3v2h3c-.5 3.9-3.6 7-7.5 7.5z"/>',
        "default": '<path d="M12 4l-5 5h3v10h4V9h3z"/>'
    }};

    // --- Math Utilities ---
    function haversineMeters(lat1, lon1, lat2, lon2) {{
        const R = 6371000;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }}

    function calculateBearing(lat1, lon1, lat2, lon2) {{
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δλ = (lon2 - lon1) * Math.PI / 180;
        const y = Math.sin(Δλ) * Math.cos(φ2);
        const x = Math.cos(φ1) * Math.sin(φ2) - Math.sin(φ1) * Math.cos(φ2) * Math.cos(Δλ);
        const θ = Math.atan2(y, x);
        return (θ * 180 / Math.PI + 360) % 360;
    }}

    function distanceToSegmentMeters(p, a, b) {{
        // Perpendicular cross-track distance from point p to segment ab
        const l2 = (b[0]-a[0])*(b[0]-a[0]) + (b[1]-a[1])*(b[1]-a[1]);
        if (l2 === 0) return haversineMeters(p[0], p[1], a[0], a[1]);
        let t = ((p[0]-a[0])*(b[0]-a[0]) + (p[1]-a[1])*(b[1]-a[1])) / l2;
        t = Math.max(0, Math.min(1, t));
        const proj = [a[0] + t * (b[0]-a[0]), a[1] + t * (b[1]-a[1])];
        return haversineMeters(p[0], p[1], proj[0], proj[1]);
    }}

    // --- Web Speech Synthesis ---
    function speakPrompt(text) {{
        if (!voiceEnabled || !('speechSynthesis' in window)) return;
        try {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.05;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        }} catch(e) {{
            console.warn("Speech synthesis error:", e);
        }}
    }}

    // --- Map Initialization ---
    function initMap() {{
        map = L.map('map', {{
            zoomControl: false,
            attributionControl: true
        }}).setView(originCoords, 15);

        // Standard OpenStreetMap Tiles (100% Free FOSS, Zero API Keys, Genuine Road Data)
        const osmLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            subdomains: ['a', 'b', 'c'],
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
        }}).addTo(map);

        // Handle tile loading errors gracefully
        osmLayer.on('tileerror', function(error) {{
            console.warn("OpenStreetMap tile layer warning, retrying...", error);
        }});

        // Detect user manual pan to show Recenter button
        map.on('dragstart', () => {{
            if (isNavigating) {{
                isAutoFollow = false;
                document.getElementById('btn-recenter').style.display = 'flex';
            }}
        }});

        // Draw initial polylines
        completedPolyline = L.polyline([], {{
            color: '#64748b',
            weight: 7,
            opacity: 0.6,
            lineJoin: 'round'
        }}).addTo(map);

        const routeColor = isEmergencyMode ? '#10b981' : '#0284c7';
        remainingPolyline = L.polyline(routeCoords, {{
            color: routeColor,
            weight: 7,
            opacity: 0.9,
            lineJoin: 'round'
        }}).addTo(map);

        // Destination Marker
        const destIcon = L.divIcon({{
            className: 'custom-dest-pin',
            html: '<div style="background: #ef4444; width: 18px; height: 18px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 10px #ef4444;"></div>',
            iconSize: [18, 18],
            iconAnchor: [9, 9]
        }});
        destMarker = L.marker(destCoords, {{ icon: destIcon }}).addTo(map);

        // User Vehicle Navigation Marker (Cyan rotating arrow + radar pulse)
        const vehicleHtml = `
            <div class="vehicle-marker-wrapper">
                <div class="vehicle-pulse-ring"></div>
                <svg class="vehicle-arrow-svg" id="vehicle-svg" viewBox="0 0 24 24">
                    <path fill="#38bdf8" stroke="#ffffff" stroke-width="1.8" d="M12 2L4 21l8-4 8 4z"/>
                </svg>
            </div>
        `;
        const vehicleIcon = L.divIcon({{
            className: 'custom-vehicle-icon',
            html: vehicleHtml,
            iconSize: [44, 44],
            iconAnchor: [22, 22]
        }});
        vehicleMarker = L.marker(originCoords, {{ icon: vehicleIcon, zIndexOffset: 1000 }}).addTo(map);

        // Accuracy Halo
        accuracyCircle = L.circle(originCoords, {{
            radius: 12,
            color: '#38bdf8',
            fillColor: '#38bdf8',
            fillOpacity: 0.12,
            weight: 1
        }}).addTo(map);

        // Fit bounds initially
        map.fitBounds(remainingPolyline.getBounds(), {{ padding: [60, 60] }});

        // Initialize HUD with first step
        updateHudInstruction(0, 0);
        updateEtaTime(routeCoords.length > 0 ? {duration_min} : 0);
    }}

    // --- HUD Updating ---
    function updateHudInstruction(stepIdx, distToNextTurnM) {{
        if (!routeSteps || routeSteps.length === 0) return;
        const currentStep = routeSteps[stepIdx] || routeSteps[0];
        const nextStep = routeSteps[stepIdx + 1];

        // Format distance string
        let distDisp = "";
        if (distToNextTurnM <= 25) {{
            distDisp = "Now";
        }} else if (distToNextTurnM < 1000) {{
            distDisp = "In " + Math.round(distToNextTurnM) + " m";
        }} else {{
            distDisp = "In " + (distToNextTurnM / 1000.0).toFixed(1) + " km";
        }}

        document.getElementById('hud-turn-dist').innerText = distDisp;
        document.getElementById('hud-road-name').innerText = currentStep.road || "Connected Corridor";
        document.getElementById('hud-instruction').innerText = currentStep.instruction || "Proceed along route";

        // Update Turn SVG Icon
        const iconKey = currentStep.icon || "straight";
        const svgPath = TURN_ICONS[iconKey] || TURN_ICONS["straight"];
        document.getElementById('turn-svg-icon').innerHTML = svgPath;

        const iconContainer = document.getElementById('turn-icon-container');
        if (iconKey === "arrive") {{
            iconContainer.classList.add('arrive');
        }} else {{
            iconContainer.classList.remove('arrive');
        }}

        // Secondary Maneuver Preview ("Then...")
        const thenContainer = document.getElementById('hud-then-container');
        if (nextStep) {{
            thenContainer.style.display = 'flex';
            document.getElementById('hud-then-text').innerText = nextStep.instruction || nextStep.road;
        }} else {{
            thenContainer.style.display = 'none';
        }}
    }}

    function updateEtaTime(remainingMins) {{
        const now = new Date();
        now.setMinutes(now.getMinutes() + Math.round(remainingMins));
        const hours = now.getHours().toString().padStart(2, '0');
        const mins = now.getMinutes().toString().padStart(2, '0');
        document.getElementById('trip-eta-val').innerText = "ETA " + hours + ":" + mins;
        document.getElementById('trip-time-val').innerText = remainingMins.toFixed(1) + " min";
        const quickEta = document.getElementById('hud-quick-eta');
        if (quickEta) quickEta.innerText = remainingMins.toFixed(1) + " min";
    }}

    // --- Live Location Processor ---
    function onLocationUpdate(lat, lon, heading, speedKmh, accuracyM) {{
        currentUserPos = [lat, lon];
        currentAccuracyM = accuracyM || 10;
        currentSpeedKmh = speedKmh || 0;

        // Update accuracy display
        accuracyCircle.setLatLng(currentUserPos).setRadius(currentAccuracyM);
        vehicleMarker.setLatLng(currentUserPos);

        // Rotate vehicle arrow
        if (heading !== null && heading !== undefined && !isNaN(heading)) {{
            currentHeading = heading;
            const svgEl = document.getElementById('vehicle-svg');
            if (svgEl) svgEl.style.transform = `rotate(${{currentHeading}}deg)`;
        }}

        // Auto-follow map pan
        if (isAutoFollow) {{
            map.panTo(currentUserPos, {{ animate: true, duration: 0.6 }});
        }}

        // Update HUD telemetry badge
        document.getElementById('gps-dot').style.background = '#10b981';
        document.getElementById('gps-status-text').innerText = trackingMode === "GPS" ? "Live GPS Active" : "Simulated Drive";
        document.getElementById('gps-acc-text').innerText = `± ${{Math.round(currentAccuracyM)}} m`;
        const quickSpd = document.getElementById('hud-quick-speed');
        if (quickSpd) quickSpd.innerText = `${{currentSpeedKmh.toFixed(1)}} km/h`;

        // If actively navigating, evaluate progress and route matching
        if (isNavigating && !isPaused) {{
            evaluateRouteProgress(lat, lon);
        }}
    }}

    // --- Route Progress & Maneuver Logic ---
    function evaluateRouteProgress(userLat, userLon) {{
        if (!routeCoords || routeCoords.length < 2) return;

        // 1. Check distance to current maneuver waypoint
        const activeStep = routeSteps[currentStepIdx];
        let distToManeuver = 999999;
        if (activeStep && activeStep.lat && activeStep.lon) {{
            distToManeuver = haversineMeters(userLat, userLon, activeStep.lat, activeStep.lon);
        }} else {{
            // Fallback: estimate from remaining polyline
            distToManeuver = haversineMeters(userLat, userLon, routeCoords[Math.min(currentStepIdx + 1, routeCoords.length - 1)][0], routeCoords[Math.min(currentStepIdx + 1, routeCoords.length - 1)][1]);
        }}

        // Check if destination arrived
        const distToFinal = haversineMeters(userLat, userLon, destCoords[0], destCoords[1]);
        if (distToFinal <= 35) {{
            handleArrival();
            return;
        }}

        // Advance to next maneuver if within 30 meters
        if (distToManeuver <= 32 && currentStepIdx < routeSteps.length - 1) {{
            currentStepIdx++;
            const newStep = routeSteps[currentStepIdx];
            updateHudInstruction(currentStepIdx, distToManeuver);
            speakPrompt(newStep.instruction);
            lastSpokenStep = currentStepIdx;
        }} else {{
            updateHudInstruction(currentStepIdx, distToManeuver);

            // Spoken turn announcements at 250m and 60m
            if (currentStepIdx !== lastSpokenStep) {{
                if (distToManeuver <= 260 && distToManeuver > 180 && lastSpokenType !== "250m") {{
                    speakPrompt(`In 250 meters, ${{activeStep.instruction}}`);
                    lastSpokenType = "250m";
                }} else if (distToManeuver <= 65 && distToManeuver > 20 && lastSpokenType !== "now") {{
                    speakPrompt(`${{activeStep.instruction}}`);
                    lastSpokenType = "now";
                }}
            }}
        }}

        // 2. Polyline progress slicing (slice completed vs remaining)
        let closestIdx = 0;
        let minSegDist = 999999;
        for (let i = 0; i < routeCoords.length - 1; i++) {{
            const segDist = distanceToSegmentMeters([userLat, userLon], routeCoords[i], routeCoords[i+1]);
            if (segDist < minSegDist) {{
                minSegDist = segDist;
                closestIdx = i;
            }}
        }}

        // Split polyline
        const completedSegment = routeCoords.slice(0, closestIdx + 1);
        completedSegment.push([userLat, userLon]);
        const remainingSegment = [[userLat, userLon]].concat(routeCoords.slice(closestIdx + 1));

        completedPolyline.setLatLngs(completedSegment);
        remainingPolyline.setLatLngs(remainingSegment);

        // Calculate remaining trip distance along polyline
        let remDistM = 0;
        for (let j = 0; j < remainingSegment.length - 1; j++) {{
            remDistM += haversineMeters(remainingSegment[j][0], remainingSegment[j][1], remainingSegment[j+1][0], remainingSegment[j+1][1]);
        }}
        const remDistKm = remDistM / 1000.0;
        document.getElementById('trip-dist-val').innerText = `${{remDistKm.toFixed(2)}} km`;
        const quickDist = document.getElementById('hud-quick-dist');
        if (quickDist) quickDist.innerText = `${{remDistKm.toFixed(2)}} km`;

        // Remaining time estimate based on 36 km/h speed
        const remTimeMin = (remDistKm / 36.0) * 60;
        updateEtaTime(remTimeMin);

        // 3. Off-Route Detection & Automatic Rerouting (> 65m deviation)
        if (minSegDist > 65.0) {{
            offRouteConsecutiveCount++;
            if (offRouteConsecutiveCount >= 2 && !isRerouting) {{
                triggerReroute(userLat, userLon);
            }}
        }} else {{
            offRouteConsecutiveCount = 0;
        }}
    }}

    // --- Automatic Rerouting via OSRM Client API ---
    function triggerReroute(fromLat, fromLon) {{
        isRerouting = true;
        document.getElementById('reroute-alert').style.display = 'block';
        speakPrompt("Off route. Recalculating road navigation.");

        const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${{fromLon.toFixed(5)}},${{fromLat.toFixed(5)}};${{destCoords[1].toFixed(5)}},${{destCoords[0].toFixed(5)}}?overview=full&geometries=geojson&steps=true`;

        fetch(osrmUrl)
            .then(res => res.json())
            .then(data => {{
                if (data.code === 'Ok' && data.routes && data.routes.length > 0) {{
                    const newRoute = data.routes[0];
                    applyReroutedData(newRoute);
                }} else {{
                    fallbackLocalReroute(fromLat, fromLon);
                }}
            }})
            .catch(err => {{
                console.warn("OSRM network reroute fallback:", err);
                fallbackLocalReroute(fromLat, fromLon);
            }})
            .finally(() => {{
                setTimeout(() => {{
                    document.getElementById('reroute-alert').style.display = 'none';
                    isRerouting = false;
                }}, 2200);
            }});
    }}

    function applyReroutedData(route) {{
        // Extract new coordinates [lat, lon]
        const rawCoords = route.geometry.coordinates;
        routeCoords = rawCoords.map(c => [c[1], c[0]]);

        // Extract steps
        const leg = route.legs[0];
        const newSteps = [];
        if (leg && leg.steps) {{
            leg.steps.forEach((s, idx) => {{
                const loc = s.maneuver ? s.maneuver.location : [0, 0];
                newSteps.push({{
                    step_no: idx + 1,
                    instruction: s.name ? `Proceed onto ${{s.name}}` : "Follow updated corridor",
                    road: s.name || "Connecting Road",
                    distance_m: s.distance,
                    lat: loc[1],
                    lon: loc[0],
                    icon: s.maneuver.type === 'turn' ? `turn_${{s.maneuver.modifier}}` : 'straight'
                }});
            }});
        }}

        routeSteps = newSteps.length > 0 ? newSteps : routeSteps;
        currentStepIdx = 0;
        offRouteConsecutiveCount = 0;

        remainingPolyline.setLatLngs(routeCoords);
        completedPolyline.setLatLngs([]);

        updateHudInstruction(0, haversineMeters(currentUserPos[0], currentUserPos[1], routeSteps[0].lat, routeSteps[0].lon));
        speakPrompt(`New route found. ${{routeSteps[0].instruction}}`);
    }}

    function fallbackLocalReroute(fromLat, fromLon) {{
        // Connect directly back to nearest waypoint of original route
        routeCoords = [[fromLat, fromLon], [destCoords[0], destCoords[1]]];
        routeSteps = [
            {{ step_no: 1, instruction: "Proceed towards destination corridor", road: "Recalculated Route", lat: destCoords[0], lon: destCoords[1], icon: "straight" }},
            {{ step_no: 2, instruction: `Arrive at ${{destName}}`, road: "Destination Bay", lat: destCoords[0], lon: destCoords[1], icon: "arrive" }}
        ];
        currentStepIdx = 0;
        remainingPolyline.setLatLngs(routeCoords);
        speakPrompt("Recalculated route towards destination.");
    }}

    function handleArrival() {{
        isNavigating = false;
        if (simInterval) clearInterval(simInterval);
        if (watchId) navigator.geolocation.clearWatch(watchId);

        document.getElementById('hud-turn-dist').innerText = "Arrived";
        document.getElementById('hud-road-name').innerText = destName;
        document.getElementById('hud-instruction').innerText = "You have reached your destination.";
        document.getElementById('turn-icon-container').classList.add('arrive');
        document.getElementById('turn-svg-icon').innerHTML = TURN_ICONS["arrive"];
        document.getElementById('trip-time-val').innerText = "0 min";
        document.getElementById('trip-dist-val').innerText = "0 m";
        const quickDist = document.getElementById('hud-quick-dist');
        if (quickDist) quickDist.innerText = "0 m";
        const quickEta = document.getElementById('hud-quick-eta');
        if (quickEta) quickEta.innerText = "0 min";
        const quickSpd = document.getElementById('hud-quick-speed');
        if (quickSpd) quickSpd.innerText = "0.0 km/h";

        speakPrompt(`You have arrived at your destination: ${{destName}}.`);
        document.getElementById('btn-start-nav').style.display = 'flex';
        document.getElementById('btn-start-nav').innerText = 'Start Navigation Again';
        document.getElementById('btn-pause-nav').style.display = 'none';
        document.getElementById('btn-end-nav').style.display = 'none';
    }}

    // --- Navigation Controls ---
    function startNavigation() {{
        isNavigating = true;
        isPaused = false;
        isAutoFollow = true;
        currentStepIdx = 0;

        document.getElementById('btn-start-nav').style.display = 'none';
        document.getElementById('btn-pause-nav').style.display = 'flex';
        document.getElementById('btn-end-nav').style.display = 'flex';
        document.getElementById('btn-recenter').style.display = 'none';

        if (trackingMode === "GPS") {{
            startRealGpsTracking();
        }} else {{
            startSimulationTracking();
        }}

        // Announce initial maneuver
        const firstStep = routeSteps[0];
        if (firstStep) {{
            speakPrompt(`Starting navigation to ${{destName}}. ${{firstStep.instruction}}`);
        }}
    }}

    function togglePauseNav() {{
        isPaused = !isPaused;
        const btn = document.getElementById('btn-pause-nav');
        if (isPaused) {{
            btn.innerText = "Resume";
            btn.style.background = "rgba(16, 185, 129, 0.2)";
            btn.style.borderColor = "#10b981";
            btn.style.color = "#34d399";
            speakPrompt("Navigation paused.");
        }} else {{
            btn.innerText = "Pause";
            btn.style.background = "rgba(255, 255, 255, 0.08)";
            btn.style.borderColor = "rgba(255, 255, 255, 0.15)";
            btn.style.color = "#f1f5f9";
            speakPrompt("Resuming navigation.");
        }}
    }}

    function endNavigation() {{
        isNavigating = false;
        isPaused = false;
        if (simInterval) clearInterval(simInterval);
        if (watchId) navigator.geolocation.clearWatch(watchId);

        document.getElementById('btn-start-nav').style.display = 'flex';
        document.getElementById('btn-start-nav').innerText = 'Start Live Navigation';
        document.getElementById('btn-pause-nav').style.display = 'none';
        document.getElementById('btn-end-nav').style.display = 'none';
        document.getElementById('btn-recenter').style.display = 'none';

        // Reset map to full route view
        completedPolyline.setLatLngs([]);
        remainingPolyline.setLatLngs(routeCoords);
        map.fitBounds(remainingPolyline.getBounds(), {{ padding: [60, 60] }});

        const quickDist = document.getElementById('hud-quick-dist');
        if (quickDist) quickDist.innerText = "{distance_km:.2f} km";
        const quickEta = document.getElementById('hud-quick-eta');
        if (quickEta) quickEta.innerText = "{duration_min:.1f} min";
        const quickSpd = document.getElementById('hud-quick-speed');
        if (quickSpd) quickSpd.innerText = "0.0 km/h";

        speakPrompt("Navigation ended.");
    }}

    function recenterMap() {{
        isAutoFollow = true;
        document.getElementById('btn-recenter').style.display = 'none';
        map.panTo(currentUserPos, {{ animate: true, duration: 0.8 }});
    }}

    function toggleVoice() {{
        voiceEnabled = !voiceEnabled;
        const btn = document.getElementById('btn-voice-toggle');
        if (voiceEnabled) {{
            btn.style.borderColor = '#38bdf8';
            btn.querySelector('svg').style.fill = '#38bdf8';
            speakPrompt("Voice guidance enabled.");
        }} else {{
            btn.style.borderColor = '#64748b';
            btn.querySelector('svg').style.fill = '#64748b';
            window.speechSynthesis.cancel();
        }}
    }}

    // --- GPS Tracking Implementation ---
    function startRealGpsTracking() {{
        if (!navigator.geolocation) {{
            alert("Geolocation is not supported by your browser. Switching to Test Drive Simulator mode.");
            toggleTrackingMode();
            return;
        }}

        const geoOptions = {{
            enableHighAccuracy: true,
            maximumAge: 1000,
            timeout: 10000
        }};

        watchId = navigator.geolocation.watchPosition(
            (pos) => {{
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;
                let heading = pos.coords.heading;
                const speed = pos.coords.speed ? pos.coords.speed * 3.6 : 28.0; // km/h
                const acc = pos.coords.accuracy || 8.0;

                if (heading === null || isNaN(heading)) {{
                    heading = calculateBearing(currentUserPos[0], currentUserPos[1], lat, lon);
                }}

                onLocationUpdate(lat, lon, heading, speed, acc);
            }},
            (err) => {{
                console.warn("GPS tracking warning:", err.message);
                document.getElementById('gps-dot').style.background = '#ef4444';
                document.getElementById('gps-status-text').innerText = "GPS Unavailable / Perm Denied";
                document.getElementById('gps-acc-text').innerText = "Unavailable";
            }},
            geoOptions
        );
    }}

    // --- Interactive Test Drive Simulation Mode ---
    function startSimulationTracking() {{
        if (simInterval) clearInterval(simInterval);
        simIdx = 0;

        simInterval = setInterval(() => {{
            if (!isNavigating || isPaused) return;

            if (simIdx < routeCoords.length - 1) {{
                const p1 = routeCoords[simIdx];
                const p2 = routeCoords[simIdx + 1];
                const heading = calculateBearing(p1[0], p1[1], p2[0], p2[1]);
                const simSpeed = 38.5; // km/h
                onLocationUpdate(p1[0], p1[1], heading, simSpeed, 4.5);
                simIdx++;
            }} else {{
                const lastPt = routeCoords[routeCoords.length - 1];
                onLocationUpdate(lastPt[0], lastPt[1], currentHeading, 0, 3.0);
                handleArrival();
            }}
        }}, 900);
    }}

    function toggleTrackingMode() {{
        if (trackingMode === "GPS") {{
            trackingMode = "SIMULATION";
            document.getElementById('btn-toggle-mode').innerText = "Switch to Real Device GPS";
            document.getElementById('btn-wrong-turn').style.display = 'inline-block';
            if (watchId) navigator.geolocation.clearWatch(watchId);
            if (isNavigating) startSimulationTracking();
        }} else {{
            trackingMode = "GPS";
            document.getElementById('btn-toggle-mode').innerText = "Switch to Test Drive Simulator";
            document.getElementById('btn-wrong-turn').style.display = 'none';
            if (simInterval) clearInterval(simInterval);
            if (isNavigating) startRealGpsTracking();
        }}
        document.getElementById('gps-status-text').innerText = trackingMode === "GPS" ? "Real GPS Selected" : "Simulator Selected";
    }}

    function simulateWrongTurn() {{
        if (!isNavigating) {{
            alert("Please press 'Start Live Navigation' first before testing a wrong turn.");
            return;
        }}
        // Shift position 110 meters perpendicular to simulate deviation
        const currentPt = currentUserPos;
        const offsetLat = currentPt[0] + 0.0011; // ~120m North
        const offsetLon = currentPt[1] + 0.0012; // ~120m East
        onLocationUpdate(offsetLat, offsetLon, (currentHeading + 90) % 360, 32.0, 5.0);
        evaluateRouteProgress(offsetLat, offsetLon);
    }}

    // Start map on load
    window.addEventListener('DOMContentLoaded', initMap);
</script>

</body>
</html>
"""
    return html_content
