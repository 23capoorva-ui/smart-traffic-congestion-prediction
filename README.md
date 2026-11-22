# NEXTRAFFX: Intelligent Traffic Management System

**A Multi-City Open-Source Urban Mobility & Congestion Mitigation Platform**  
*Built with Python 3.13, Streamlit, Leaflet/Folium, OpenStreetMap, OSRM, and Scikit-Learn*

---

## 1. Project Title & Overview

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

## 4. Main Features

### 4.1 Multi-City Traffic Overview & Historical Analytics
- Real-time time filtering (24-hour format: 00:00 to 23:59) and day-of-week selection.
- Regional baseline observations: 2,100 records per city across 20 monitored high-density corridors.
- High-resolution interactive charts for hourly congestion profiles, queue lengths, and congestion severity distributions.

### 4.2 City Hotspot Congestion Map
- High-contrast OpenStreetMap GIS basemap rendering monitored corridors with color-coded choke indicators (Green = Low, Amber = Moderate, Red = High).
- Circle markers with radius proportional to queue lengths and custom popups detailing junction delays and vehicle speeds.

### 4.3 OSRM Road Routing & Turn-by-Turn Navigation
- Actual road-network route calculation between arbitrary origins and destinations using OSRM.
- Alternative route comparison (Primary Arterial vs Bypass Corridor) with estimated travel time, total distance, and congestion risk index.
- Google Maps-style moving map navigation with heading orientation, vehicle marker tracking, completed vs remaining route differentiation, and spoken voice guidance.
- Automatic off-route detection (>65m deviation) triggering instant route recalculation.
- Desktop Test Drive Simulator allowing developers to test navigation trajectories without driving.

### 4.4 Emergency Priority Dispatch & Green Wave Simulation
- Hospital emergency corridor routing connecting major medical centers (e.g., Apollo, Fortis, KIMS, Lilavati, AIIMS) with critical junctions.
- In-browser Web Audio synthesizer generating realistic dual-frequency (650 Hz / 900 Hz) siren alerts without audio media files.
- Tactile haptic vibration alerts for mobile devices via the HTML5 Vibration API.
- Cross-session real-time broadcast: an ambulance moving in one browser session dynamically broadcasts approaching priority alerts to general commuters in separate browser sessions.

### 4.5 Crowdsourced Citizen Incident Reporting
- Direct logging of verified road hazards (accidents, waterlogging, construction, road closures) into SQLite.
- Linear decay algorithm weighting incident impacts based on elapsed age:
  $$\text{Decayed Impact} = \text{Base Severity} \times \max(0.40,\; 1.0 - 0.15 \times \text{age}_{\text{hours}})$$
  $$\text{Final Congestion Score} = \min(99.0,\; \max(5.0,\; \text{Base Score} + \text{Decayed Impact}))$$

---

## 5. Technologies Used

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

## 6. System Architecture

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

## 7. Dataset Source & Attribution

- **Primary Historical Dataset Source:** `Bengaluru_Traffic_Condition_Dataset.xlsx` is sourced from the open research repository [aswinmangatt/Bengaluru-Traffic-Analysis](https://github.com/aswinmangatt/Bengaluru-Traffic-Analysis) created by **Aswin Mangatt**.
- **Licensing Audit & Redistribution Notice:**  
  An audit of the upstream source repository confirms that it currently provides no explicit open-source license file (`License: None`). Under international intellectual property law and GitHub's Terms of Service, all rights remain reserved to the original author, and third-party redistribution or re-hosting of the raw Excel dataset is not permitted without express written consent.
- **Compliance Measure:**  
  In strict adherence to ethical research standards, copyright law, and open-source licensing compliance, the dataset binary is excluded from git tracking via `.gitignore`. Evaluators and researchers can download the dataset directly from the original author's repository using the instructions provided below.
- **Dataset Scope:** 2,100 hourly observation records covering 20 key traffic corridors in Bengaluru sampled across 7 days from 08:00 to 22:00.

---

## 8. Dataset Installation Instructions

To activate historical baseline analytics and machine learning prediction models on a fresh installation:

1. **Download the Excel Dataset:**  
   Download `Bengaluru_Traffic_Condition_Dataset.xlsx` directly from the original author's repository:
   - Repository: [aswinmangatt/Bengaluru-Traffic-Analysis](https://github.com/aswinmangatt/Bengaluru-Traffic-Analysis) (located under `data/`)
   - Direct raw download link: [data/Bengaluru_Traffic_Condition_Dataset.xlsx](https://raw.githubusercontent.com/aswinmangatt/Bengaluru-Traffic-Analysis/main/data/Bengaluru_Traffic_Condition_Dataset.xlsx)

2. **Command-Line Download (PowerShell / curl):**
   ```bash
   curl -L -o Bengaluru_Traffic_Condition_Dataset.xlsx https://raw.githubusercontent.com/aswinmangatt/Bengaluru-Traffic-Analysis/raw/main/data/Bengaluru_Traffic_Condition_Dataset.xlsx
   ```

3. **Placement:**  
   Place the downloaded `Bengaluru_Traffic_Condition_Dataset.xlsx` file directly in the root directory of this repository:
   ```
   smart-traffic-congestion-prediction/
   ├── Bengaluru_Traffic_Condition_Dataset.xlsx    <-- Place file here
   ├── app.py
   ├── requirements.txt
   └── ...
   ```

4. **Automatic Database Seeding:**  
   When NEXTRAFFX starts, `db_manager.init_database()` automatically detects the Excel file, creates the local SQLite database (`traffic_system.db`), seeds the 2,100 records for Bengaluru, generates calibrated regional baselines for Mumbai, Delhi, Hyderabad, Chennai, Kolkata, and Pune, and enables full prediction and visualization models.

*(Note: If the application is launched without the dataset, NEXTRAFFX does not crash. It displays an informative guidance banner explaining how to download and place the file).*

---

## 9. Python Environment Setup

### Prerequisites
- Python 3.10 to 3.13 (64-bit CPython recommended)
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

---

## 10. Dependency Installation

Install all required production dependencies using `pip`:
```bash
pip install -r requirements.txt
```

Verify the installation:
```bash
python -c "import streamlit, folium, sklearn, pandas, numpy; print('All core modules imported successfully!')"
```

---

## 11. Application Startup Command

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

Once launched, access the application in your browser at:
```
http://localhost:8501   (or http://localhost:8502)
```

---

## 12. GitHub Repository Information

- **Repository Name:** `smart-traffic-congestion-prediction`
- **Owner / Organization:** `23capoorva-ui`
- **Repository URL:** `https://github.com/23capoorva-ui/smart-traffic-congestion-prediction`
- **Default Branch:** `main`
- **Visibility:** Public

---

## 13. Streamlit Community Cloud Deployment

To deploy NEXTRAFFX to **Streamlit Community Cloud** (free tier):

1. **Fork or Push:** Push this repository to your GitHub account under `smart-traffic-congestion-prediction`.
2. **Sign in to Streamlit:** Navigate to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **Create New App:**
   - **Repository:** `23capoorva-ui/smart-traffic-congestion-prediction`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. **Cloud Persistence Disclosure:**  
   Streamlit Community Cloud runs containers with ephemeral filesystems. SQLite databases (`traffic_system.db`) and citizen reports are stored locally in the container and reset when the container restarts. Permanent cross-session storage on cloud hosting would require an external cloud database (e.g. Supabase, AWS RDS, or PostgreSQL).
5. **Dataset Handling on Cloud:**  
   Because `Bengaluru_Traffic_Condition_Dataset.xlsx` is excluded from GitHub for licensing compliance (its upstream redistribution licence is not confirmed), cloud deployments such as Streamlit Community Cloud will not display historical Bengaluru analytics unless the dataset is supplied through a supported source (such as local self-hosting or private storage mounts). In strict compliance with academic and research integrity, historical time-series graphs and historical congestion scores for Bengaluru are withheld rather than filled with fabricated numbers. All other core capabilities—including full GIS corridor maps, live OSRM road routing, turn-by-turn navigation, ambulance dispatch simulation, and citizen hazard logging—remain 100% operational. See Section 8 for instructions on downloading and setting up the dataset for local use.

---

## 14. Known Limitations & Dependencies

1. **Historical Dataset Operating Hours & Cloud Availability:**  
   The empirical baseline dataset covers the daytime/evening hours between 08:00 and 22:00. In strict accordance with academic integrity, predictions and historical time-series graphs are withheld for off-peak hours (23:00 to 07:59) rather than populated with fabricated values. Furthermore, public cloud deployments will not display historical Bengaluru analytics unless the dataset is supplied through a supported source.
2. **Physical Sensor Integration:**  
   In compliance with the zero-cost budget constraint, this prototype does not license commercial live GPS probe feeds (e.g., TomTom or Google Maps Traffic API) or municipal inductive loop traffic camera networks.
3. **External Services & Network Connectivity:**  
   Road-network route geometry and map tiles rely on external public services: Open Source Routing Machine (`router.project-osrm.org`) for road-network routing and OpenStreetMap tile servers for GIS cartography. Routing, map loading, and recalculation depend on external server availability and network connectivity.
4. **Browser Permissions & Client APIs:**  
   Live navigation, voice guidance, and siren notifications depend on client-side browser permissions and modern Web API support:
   - **GPS Tracking:** Real-time turn-by-turn navigation requires explicit user permission for the HTML5 Geolocation API (`navigator.geolocation`).
   - **Audio Siren & Speech:** Spoken voice prompts (Web Speech API) and emergency siren audio (Web Audio API) require initial user interaction (such as clicking 'Start Navigation' or 'Sound Siren') in accordance with modern browser autoplay policies.
   - **Haptic Alerts:** Vibration notifications depend on device and browser support for the HTML5 Vibration API.
5. **Emergency Dispatch Simulation:**  
   Ambulance alerts, priority green-wave corridors, and approaching vehicle broadcasts are strictly educational simulations and research demonstrations, **NOT** actual emergency-service or 108/112 municipal integration, and do not interface with real hospitals or physical traffic signal hardware controllers.

---

## 15. Future Enhancements

- **Overpass API Signal Mapping:** Direct querying of traffic signal nodes from OpenStreetMap to estimate intersection delays dynamically.
- **Local OSRM / Valhalla Backend:** Self-hosted routing server via Docker for offline, zero-latency routing.
- **Edge Vision Telemetry:** Computer-vision queue length estimation from open municipal traffic camera streams.
- **Multi-Lingual Audio Prompts:** Support for regional Indian languages (Kannada, Hindi, Tamil, Telugu, Marathi, Bengali) in spoken turn-by-turn guidance.

---

## 16. Project Disclaimer & License

### Disclaimer
This software is developed strictly for educational, academic research, and urban mobility simulation purposes. It does not provide certified emergency navigation, does not control real-world traffic signals, and does not replace official emergency dispatch protocols.

### License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
All external basemap tiles remain &copy; [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
