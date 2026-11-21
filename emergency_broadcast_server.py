"""
Emergency Broadcast Server for NEXTRAFFX Intelligent Traffic Management System.
Provides real-time bi-directional WebSocket communication and persistent state
for emergency vehicle (ambulance) dispatches across separate browser sessions.
"""

import asyncio
import json
import logging
import socket
import threading
import time
import websockets
import db_manager

# Port for WebSocket broadcasting
WS_PORT = 8765
WS_HOST = "0.0.0.0"

logger = logging.getLogger("emergency_broadcast")
logger.setLevel(logging.INFO)

# In-memory registry of active emergency trips
ACTIVE_TRIPS = {}
CONNECTED_CLIENTS = set()
_SERVER_LOCK = threading.Lock()
_SERVER_RUNNING = False


def is_port_in_use(port, host="127.0.0.1"):
    """Checks whether the specified port is already bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


async def broadcast_event(event_dict, exclude_ws=None):
    """Broadcasts a JSON message to all connected WebSocket clients."""
    if not CONNECTED_CLIENTS:
        return
    message = json.dumps(event_dict)
    disconnected = set()
    for ws in list(CONNECTED_CLIENTS):
        if ws == exclude_ws:
            continue
        try:
            await ws.send(message)
        except Exception:
            disconnected.add(ws)
    for ws in disconnected:
        CONNECTED_CLIENTS.discard(ws)


async def handle_client(websocket):
    """Handles an incoming WebSocket connection from Driver or Citizen."""
    CONNECTED_CLIENTS.add(websocket)
    try:
        # Immediately send active trips to the newly connected client
        init_payload = {
            "type": "SYNC_ACTIVE_TRIPS",
            "active_trips": list(ACTIVE_TRIPS.values()),
            "timestamp": time.time()
        }
        await websocket.send(json.dumps(init_payload))

        async for raw_msg in websocket:
            try:
                data = json.loads(raw_msg)
            except Exception:
                continue

            msg_type = data.get("type", "")

            # 1. Driver Starts Emergency Trip
            if msg_type == "START_EMERGENCY_TRIP":
                trip = data.get("trip", {})
                trip_id = trip.get("trip_id") or f"AMB-{int(time.time())}"
                trip["trip_id"] = trip_id
                trip["status"] = "ACTIVE"
                trip["last_updated"] = time.time()
                ACTIVE_TRIPS[trip_id] = trip

                # Persist to SQLite
                try:
                    db_manager.publish_emergency_trip(
                        trip_id=trip_id,
                        ambulance_id=trip.get("ambulance_id", "AMB-108"),
                        city=trip.get("city", "Bengaluru"),
                        origin_name=trip.get("origin_name", "Origin"),
                        dest_name=trip.get("dest_name", "Hospital"),
                        priority=trip.get("priority", "Priority 1 - Critical Trauma"),
                        current_lat=trip.get("current_lat", 0.0),
                        current_lon=trip.get("current_lon", 0.0),
                        heading=trip.get("heading", 0.0),
                        speed_kmh=trip.get("speed_kmh", 0.0),
                        route_coords_json=json.dumps(trip.get("route_coords", []))
                    )
                except Exception as e:
                    logger.warning("DB trip publish warning: %s", e)

                # Broadcast to all other sessions
                await broadcast_event({
                    "type": "EMERGENCY_TRIP_STARTED",
                    "trip": trip
                })

            # 2. Driver Updates Live Telemetry
            elif msg_type == "UPDATE_AMBULANCE_LOCATION":
                trip_id = data.get("trip_id")
                if trip_id and trip_id in ACTIVE_TRIPS:
                    t = ACTIVE_TRIPS[trip_id]
                    t["current_lat"] = float(data.get("current_lat", t.get("current_lat", 0.0)))
                    t["current_lon"] = float(data.get("current_lon", t.get("current_lon", 0.0)))
                    t["heading"] = float(data.get("heading", t.get("heading", 0.0)))
                    t["speed_kmh"] = float(data.get("speed_kmh", t.get("speed_kmh", 0.0)))
                    t["last_updated"] = time.time()

                    # Update DB
                    try:
                        db_manager.update_emergency_trip_location(
                            trip_id=trip_id,
                            current_lat=t["current_lat"],
                            current_lon=t["current_lon"],
                            heading=t["heading"],
                            speed_kmh=t["speed_kmh"]
                        )
                    except Exception as e:
                        logger.warning("DB location update warning: %s", e)

                    # Broadcast position to all other sessions
                    await broadcast_event({
                        "type": "AMBULANCE_LOCATION_UPDATED",
                        "trip_id": trip_id,
                        "ambulance_id": t.get("ambulance_id", "AMB-108"),
                        "city": t.get("city", "Bengaluru"),
                        "origin_name": t.get("origin_name", "Origin"),
                        "dest_name": t.get("dest_name", "Hospital"),
                        "priority": t.get("priority", "Priority 1"),
                        "current_lat": t["current_lat"],
                        "current_lon": t["current_lon"],
                        "heading": t["heading"],
                        "speed_kmh": t["speed_kmh"],
                        "timestamp": t["last_updated"]
                    })

            # 3. Driver Ends Emergency Trip
            elif msg_type == "STOP_EMERGENCY_TRIP":
                trip_id = data.get("trip_id")
                if trip_id:
                    if trip_id in ACTIVE_TRIPS:
                        del ACTIVE_TRIPS[trip_id]
                    try:
                        db_manager.stop_emergency_trip(trip_id)
                    except Exception as e:
                        logger.warning("DB stop trip warning: %s", e)

                    await broadcast_event({
                        "type": "EMERGENCY_TRIP_STOPPED",
                        "trip_id": trip_id,
                        "timestamp": time.time()
                    })

            # 4. Request Sync
            elif msg_type == "REQUEST_SYNC":
                await websocket.send(json.dumps({
                    "type": "SYNC_ACTIVE_TRIPS",
                    "active_trips": list(ACTIVE_TRIPS.values()),
                    "timestamp": time.time()
                }))

    except Exception:
        pass
    finally:
        CONNECTED_CLIENTS.discard(websocket)


async def _start_async_server():
    """Runs the asyncio WebSocket server loop."""
    # Preload any active trips from SQLite
    try:
        db_trips = db_manager.get_active_emergency_trips()
        for r in db_trips:
            trip_id = r["trip_id"]
            coords = []
            try:
                coords = json.loads(r.get("route_coords_json") or "[]")
            except Exception:
                pass
            ACTIVE_TRIPS[trip_id] = {
                "trip_id": trip_id,
                "ambulance_id": r["ambulance_id"],
                "city": r["city"],
                "origin_name": r["origin_name"],
                "dest_name": r["dest_name"],
                "priority": r["priority"],
                "current_lat": r["current_lat"],
                "current_lon": r["current_lon"],
                "heading": r["heading"],
                "speed_kmh": r["speed_kmh"],
                "route_coords": coords,
                "status": "ACTIVE",
                "last_updated": time.time()
            }
    except Exception as e:
        logger.warning("Preload active trips error: %s", e)

    server = await websockets.serve(
        handle_client,
        WS_HOST,
        WS_PORT,
        ping_interval=20,
        ping_timeout=20
    )
    await asyncio.Future()  # run forever


def _run_server_thread():
    """Target function for background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_start_async_server())
    except Exception as e:
        logger.warning("Broadcast server stopped: %s", e)


def ensure_broadcast_server_running():
    """
    Spawns the real-time broadcast WebSocket server in a daemon thread
    if not already running on port 8765.
    """
    global _SERVER_RUNNING
    with _SERVER_LOCK:
        if _SERVER_RUNNING:
            return True
        if is_port_in_use(WS_PORT):
            _SERVER_RUNNING = True
            return True

        t = threading.Thread(target=_run_server_thread, daemon=True, name="EmergencyBroadcastServer")
        t.start()
        time.sleep(0.3)
        _SERVER_RUNNING = is_port_in_use(WS_PORT)
        return _SERVER_RUNNING


if __name__ == "__main__":
    print(f"Starting standalone NEXTRAFFX Emergency Broadcast Server on ws://{WS_HOST}:{WS_PORT}...")
    asyncio.run(_start_async_server())
