# NEXTRAFFX: Intelligent Traffic Management System

**A Multi-City Open-Source Urban Mobility & Congestion Mitigation Platform**  
*Built with Python 3.13, Streamlit, Leaflet/Folium, OpenStreetMap, OSRM, and Scikit-Learn*

---

## 1. Project Overview

**NEXTRAFFX** is a production-grade, zero-cost (₹0 budget) Intelligent Traffic Management System designed to address urban vehicular congestion across major metropolitan corridors in India. The system unites empirical historical traffic observation datasets, hybrid machine learning regression models, citizen incident reporting via SQLite, OpenStreetMap-based GIS cartography, real-time OSRM (Open Source Routing Machine) road-network routing, live GPS turn-by-turn navigation with audio synthesis, and an emergency vehicle priority corridor dispatch simulator with Web Audio siren generation.

---

## 2. Problem Statement

Rapid urban growth and vehicular volume in Indian tier-1 and tier-2 metropolitan regions lead to severe junction choke points, unpredictable commute delays, heightened carbon emissions, and critical transit blockages for emergency response services (ambulances). Existing commercial solutions often rely on closed proprietary ecosystems, costly API key licensing (e.g., Google Maps / TomTom enterprise APIs), or simulated straight-line approximations that fail to reflect actual road-network topology and junction dynamics.

---

## 3. Project Objectives

1. **Zero-Licensing Cost Compliance:** Implement a complete GIS, routing, predictive, and dispatch infrastructure without relying on paid commercial APIs or proprietary cloud subscriptions.
2. **True Road-Network Topology:** Generate genuine road-aligned route geometries using Open Source Routing Machine (OSRM) and OpenStreetMap (OSM) without straight-line shortcuts.
3. **Dual Predictive Intelligence:** Deploy a hybrid engine combining Scikit-Learn Random Forest Regression with a deterministic pure NumPy/Pandas Empirical Statistical Baseline, guaranteeing stability across strict OS security policies (such as Windows Smart App Control).
4. **Google Maps-Style Live Navigation:** Provide continuous GPS position tracking (`watchPosition()`), real-time route progress calculation, off-route wrong-turn detection, dynamic automatic recalculation, and Web Speech API turn prompts.
5. **Simulated Emergency Green Corridors:** Enable multi-browser real-time ambulance dispatch with Web Audio synthesizer sirens, tactile vibration APIs, and approaching vehicle broadcast warnings for general road users.
6. **Multi-Metropolitan Scalability:** Maintain independent historical and GIS monitoring across 7 major metropolitan regions: Bengaluru, Mumbai, Delhi, Hyderabad, Chennai, Kolkata, and Pune.

---

## 4. System Architecture

```
+-----------------------------------------------------------------------------------+
|                                  CLIENT BROWSER                                   |
|   +---------------------------------------+   +-------------------------------+   |
|   |         Streamlit Web UI              |   |     HTML5 / Web APIs          |   |
|   |  - Interactive Dashboard Views        |   |  - Web Audio Synthesizer      |   |
|   |  - Leaflet / Folium Map Canvases      |   |  - Web Speech API Guidance    |   |
|   |  - Multi-City Filter & Controls       |   |  - Geolocation API (GPS)      |   |
|   +-------------------+-------------------+   +---------------+---------------+   |
+-----------------------|---------------------------------------|-------------------+
                        |                                       |
+-----------------------v---------------------------------------v-------------------+
|                              APPLICATION ENGINE (PYTHON)                          |
|   +---------------------------------------------------------------------------+   |
|   |  app.py : UI Orchestration, Session State & Component Lifecycle           |   |
|   +-------------------+-------------------+-------------------+---------------+   |
|                       |                   |                   |                   |
|   +-------------------v---+   +-----------v-------+   +-------v---------------+   |
|   |  traffic_predictor.py |   |  osrm_router.py   |   |  live_navigation.py   |   |
|   |  - Scikit-Learn RF    |   |  - Dual OSRM API  |   |  - Moving Map Follow  |   |
|   |  - NumPy/Pandas Base  |   |  - Polyline Dec.  |   |  - Wrong-Turn Detect  |   |
|   |  - Incident Weighting |   |  - Road Fallback  |   |  - Turn Guidance HUD  |   |
|   +-----------+-----------+   +-----------+-------+   +-------+---------------+   |
|               |                           |                   |                   |
+---------------|---------------------------|-------------------|-------------------+
                |                           |                   |
+---------------v---------------------------v-------------------v-------------------+
|                              PERSISTENCE & SERVICES                               |
|   +-----------------------------------+   +-----------------------------------+   |
|   |   SQLite (traffic_system.db)      |   |   External FOSS Services          |   |
|   |   - city_observations (2,100/city)|   |   - OpenStreetMap Tile Server     |   |
|   |   - incident_reports              |   |   - OSRM Public Routing APIs      |   |
|   |   - emergency_broadcast_trips     |   |   - Nominatim Geocoding API       |   |
|   +-----------------------------------+   +-----------------------------------+   |
+-----------------------------------------------------------------------------------+
```

---

## 5. Key Features

### 5.1 Multi-City Traffic Overview & Historical Analytics
- Real-time time filtering (24-hour format: 00:00 to 23:59) and day-of-week selection.
- Regional baseline observations: 2,100 records per city across 20 monitored high-density corridors.
- High-resolution interactive charts for hourly congestion profiles, queue lengths, and congestion severity distributions.

### 5.2 City Hotspot Congestion Map
- High-contrast OpenStreetMap GIS basemap rendering monitored corridors with color-coded choke indicators (Green = Low, Amber = Moderate, Red = High).
- Circle markers with radius proportional to queue lengths and custom popups detailing junction delays and vehicle speeds.

### 5.3 OSRM Road Routing & Turn-by-Turn Navigation
- Actual road-network route calculation between arbitrary origins and destinations using OSRM.
- Alternative route comparison (Primary Arterial vs Bypass Corridor) with estimated travel time, total distance, and congestion risk index.
- Google Maps-style moving map navigation with heading orientation, vehicle marker tracking, completed vs remaining route differentiation, and spoken voice guidance.
- Automatic off-route detection (>65m deviation) triggering instant route recalculation.
- Desktop Test Drive Simulator allowing developers to test navigation trajectories without driving.

### 5.4 Emergency Priority Dispatch & Green Wave Simulation
- Hospital emergency corridor routing connecting major medical centers (e.g., Apollo, Fortis, KIMS, Lilavati, AIIMS) with critical junctions.
- In-browser Web Audio synthesizer generating realistic dual-frequency (650 Hz / 900 Hz) siren alerts without audio media files.
- Tactile haptic vibration alerts for mobile devices via the HTML5 Vibration API.
- Cross-session real-time broadcast: an ambulance moving in one browser session dynamically broadcasts approaching priority alerts to general commuters in separate browser sessions.

### 5.5 Crowdsourced Citizen Incident Reporting
- Direct logging of verified road hazards (accidents, waterlogging, construction, road closures) into SQLite.
- Linear decay algorithm weighting incident impacts based on elapsed age:
  $$\text{Decayed Impact} = \text{Base Severity} \times \max(0.40,\; 1.0 - 0.15 \times \text{age}_{\text{hours}})$$
  $$\text{Final Congestion Score} = \min(99.0,\; \max(5.0,\; \text{Base Score} + \text{Decayed Impact}))$$

---

## 6. Technologies Used

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | **Python 3.13** | Core runtime environment |
| **User Interface** | **Streamlit** | Reactive dashboard, sidebar navigation, widgets |
| **Mapping & GIS** | **Leaflet.js & Folium** | Interactive geospatial map canvases |
| **Map Tiles** | **OpenStreetMap (OSM)** | 100% Free basemap tiles with zero API keys |
| **Routing Engine** | **OSRM Project** | Connected road-network routing & step instructions |
| **Predictive Modeling** | **Scikit-Learn** | Random Forest Regression (Score & Speed) |
| **Statistical Fallback** | **NumPy & Pandas** | Deterministic empirical baseline under security locks |
| **Data Storage** | **SQLite3** | Embedded relational database (`traffic_system.db`) |
| **Audio Synthesis** | **HTML5 Web Audio API** | Dual-tone siren synthesizer (650Hz / 900Hz) |
| **Haptic Feedback** | **HTML5 Vibration API** | Tactile emergency alerting on mobile browsers |
| **Voice Prompts** | **Web Speech API** | Spoken client-side turn-by-turn guidance |

---

## 7. Installation Instructions

### Prerequisites
- Python 3.10 to 3.13 (64-bit recommended)
- Git installed on your system

### Step 1: Clone the Repository
```bash
git clone https://github.com/23capoorva-ui/smart-traffic-congestion-prediction.git
cd smart-traffic-congestion-prediction
```

### Step 2: Create a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 8. How to Run the Application

### Option A: Windows One-Click Execution (Recommended)
Double-click `START_SYSTEM.bat` in the project root folder.  
The launcher will automatically discover an available network port (handling port 8501 locks by switching to 8502 if required) and open the application in your default browser.

### Option B: Using the Python Launcher
```bash
python launcher.py
```

### Option C: Direct Streamlit Execution
```bash
streamlit run app.py
```

Once launched, access the application at:
```
http://localhost:8501   (or http://localhost:8502)
```

---

## 9. Data Sources and Academic Limitations

1. **Historical Dataset:**
   - Bengaluru empirical observation dataset (`Bengaluru_Traffic_Condition_Dataset.xlsx`, 2,100 records) covers the hours between 08:00 and 22:00.
   - In accordance with academic integrity, predictions are withheld for off-peak hours (23:00 to 07:59) when observations do not exist, preventing fabricated numbers.
2. **Multi-City Profiles:**
   - Observations for Mumbai, Delhi, Hyderabad, Chennai, Kolkata, and Pune are calibrated to regional vehicular density profiles and stored in `traffic_system.db`.
3. **Physical Sensor Feeds:**
   - Under the ₹0 project budget constraint, the system does not integrate paid municipal inductive-loop camera feeds or commercial floating-car GPS telematics.
4. **Emergency Signals:**
   - The emergency corridor simulation is an academic demonstration and does not connect to municipal 108/112 CAD or override physical traffic signal hardware.

---

## 10. Repository File Structure

```
├── app.py                                # Main Streamlit application and view controllers
├── db_manager.py                         # SQLite database schemas, queries, and seeder
├── traffic_predictor.py                  # Dual ML & empirical statistical prediction engine
├── live_navigation.py                    # Leaflet turn-by-turn navigation & GPS tracking HUD
├── osrm_router.py                        # OSRM road-geometry routing and polyline decoding
├── emergency_broadcast_server.py         # Real-time WebSocket emergency broadcast daemon
├── launcher.py                           # Resilient network port scanner & app launcher
├── START_SYSTEM.bat                      # Windows one-click startup batch script
├── requirements.txt                      # Project dependencies
├── traffic_icon.png                      # Favicon / line icon asset
├── Bengaluru_Traffic_Condition_Dataset.xlsx # Baseline observation dataset (2,100 records)
├── traffic_system.db                     # SQLite database with seeded city observations
├── incident_reports.csv                  # Sample incident logs
├── user_feedback.csv                     # Sample feedback logs
├── .gitignore                            # Git exclusion rules
├── .streamlit/
│   └── config.toml                       # Dark navy theme and server configuration
└── README.md                             # Project documentation
```

---

## 11. Future Enhancements

- Integration of OpenStreetMap Overpass API for real-time traffic signal node mapping.
- Offline routing support via localized Valhalla or OSRM Docker instances.
- Computer-vision-based queue length estimation using open traffic camera video streams.
- Multi-language voice guidance prompts for regional Indian languages.

---

## 12. License

This project is developed for educational and academic research purposes under the MIT License.
