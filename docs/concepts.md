# Simulated City Flooding – Concept Document

## System Overview
The flooding simulation is an agent‑based environment where independent notebooks mimic entities in a city. Agents communicate through MQTT, publishing sensor readings, control signals and status updates. A dashboard notebook subscribes to all feeds and renders a live map using `anymap‑ts`. The four key components of the system are:

* **Trigger** – an agent or external input that starts a flood event (e.g. heavy rainfall or dam failure). It emits a message when conditions exceed a threshold.
* **Observer** – sensors scattered around the city collect water levels, flow rates, and infrastructure status. Observers publish periodic JSON payloads reporting their readings.
* **Control** – logic that decides how to respond to flooding information. It may activate pumps, close gates, or send evacuation notices.
* **Response** – actuators or user interfaces that carry out the decisions; for example, a pump notebook that receives commands and updates its state, or a dashboard that displays alerts.

Each agent lives in its own notebook, maintains a loop, and uses helpers from the `simulated_city` library.

## MQTT Architecture
Topics are hierarchical under a base topic defined in configuration (default `city/flood`).

### Topics
* `city/flood/trigger` – published by Trigger agents.
* `city/flood/observer/<id>` – individual observer streams water data.
* `city/flood/control/command` – control decisions issued.
* `city/flood/response/<device>` – commands for actuators.
* `city/flood/dashboard` – aggregated status for the dashboard.

### Publishers & Subscribers
* **Trigger notebook**
  * Publishes: `.../trigger`
  * No subscribers.
* **Observer notebooks** (one per location)
  * Publishes: `.../observer/<id>`
  * Subscribers: none (pure sensors).
* **Control notebook**
  * Subscribes: `.../observer/#`, `.../trigger`
  * Publishes: `.../control/command`
* **Response notebooks**
  * Subscribes: `.../control/command`
  * Publishes: `.../response/<device>`
* **Dashboard notebook**
  * Subscribes to all topics under `city/flood/#`
  * Publishes: none (read‑only view).

### JSON Schemas
* **Trigger message**
  ```json
  {
    "event": "rain" | "dam_break",
    "severity": "low" | "medium" | "high",
    "timestamp": "ISO8601"
  }
  ```
* **Observer reading**
  ```json
  {
    "sensor_id": "string",
    "water_level": "float_meters",
    "flow_rate": "float_m3s",
    "timestamp": "ISO8601"
  }
  ```
* **Control command**
  ```json
  {
    "action": "activate_pump" | "close_gate" | "alert",
    "target": "string",
    "parameters": { ... },
    "timestamp": "ISO8601"
  }
  ```
* **Response update**
  ```json
  {
    "device": "string",
    "status": "idle" | "running" | "error",
    "details": "string",
    "timestamp": "ISO8601"
  }
  ```

## Configuration Parameters
Loaded via `simulated_city.config.load_config()` from `config.yaml` with overrides from the environment.

* `mqtt.host` – broker hostname (default: `broker.hivemq.com`)
* `mqtt.port` – integer port (default: `1883`)
* `mqtt.base_topic` – string root topic (default: `city/flood`)
* `mqtt.username` – env var name for user (none)
* `mqtt.password` – env var name for password (none)
* `agent.trigger.interval` – seconds between checks (default: `10`)
* `agent.observer.interval` – seconds between readings (default: `5`)
* `agent.control.threshold` – water level threshold (default: `2.0`)
* `agent.response.timeout` – seconds to wait for acknowledgement (default: `30`)
* `map.zoom` – initial map zoom level (default: `12`)
* `map.center` – `[lat, lon]` default center (default: `[40.0, -75.0]`)

## Architecture Decisions
* **MQTT pub/sub** was chosen for loose coupling and simplicity.
* **Separate notebooks per agent** to satisfy workshop requirements and allow distributed simulation.
* **anymap‑ts** for mapping; avoids heavier libraries and matches project policy.
* **Configuration via YAML and `.env`** supports flexible deployments.
* **Library helpers** (in `simulated_city.mqtt`, `geo`, etc.) encapsulate common behavior to keep notebooks focused.

## Notebooks & Library Structure
### Notebooks
1. `notebooks/agent_trigger.ipynb` – flood source simulator.
2. `notebooks/agent_observer_<id>.ipynb` – sensor nodes (could be parameterized).
3. `notebooks/agent_control.ipynb` – decision logic.
4. `notebooks/agent_response_<device>.ipynb` – actuators like pumps/gates.
5. `notebooks/dashboard.ipynb` – subscribes to all topics and visualizes using anymap‑ts.

### Library Code
* `simulated_city/config.py` – loader and dataclasses for configuration.
* `simulated_city/mqtt.py` – `connect_mqtt()`, `publish_json_checked()`.
* `simulated_city/geo.py` – coordinate transforms.
* `simulated_city/maplibre_live.py` – helper to build a live map subscription.

### Classes vs Functions
* **Dataclasses**: `MqttConfig`, `AppConfig`, sensor data containers.
* **Functions**: connection helpers, JSON validation helpers, the CLI entry point.
* Notebook cells will usually import functions and create lightweight classes for agent state.

## Open Questions / Assumptions

### ❓ Must Answer Before Implementation

1. **Pedestrian Agent**
   - Should people be modeled as a separate MQTT-publishing agent? No, they should only recieve information and warnings from the weather station, where they will be "registered" for seeing the warning, and thereafter, act accordingly, by wandering towards Køge Torv.
   - Or should pedestrian movement be implicit (controlled by the Response agent when alerts fire)? Yes. People should respond and be controlled by the warning they get, so that they comply and walk away from the beach and towards Køge torv.
   - How many pedestrians should we simulate? (You mentioned ~20) 10 people

2. **Evacuation Notification**
   - Which agent sends alerts to people's phones? The agents at the weather station who recieves the data given by the sensors.
   - Should the Control agent emit an "alert" action that a separate Response agent executes? The control agent should recieve data and alert the people, if the water is rising 5 or more meters. The response agent then execute the order.
   - Or does the Control agent directly notify people? No as explained above.

3. **Geographic Coordinates**
   - Provide GPS coordinates (lat, lon) for:
     * Køge Torv (inner city, high elevation)The coordinates: 55.456553861769855, 12.181774944848945
     * Køge Søndre Strand (beach area, flood-prone) The coordinates: 55.45058843620187, 12.197503222443261
     * Observer sensor locations (how many and where?)
     About 5 sensors and they are all located near Køge Søndre Strand.
   - Or shall we use realistic placeholder coordinates for Denmark?

4. **Simulation Timing**
   - Is this real-time (1 second = 1 second)?
   - Accelerated (10× speed, so 10 seconds simulates 100 seconds)?
   - How long should a typical run last? (e.g., 5 minutes of simulated time)
   Can you make it so that it floods every 30 seconds, for a duration of 15 seconds before it goes away. The people will get a notification about the flooding, 25 seconds in advance.

### ✅ Already Clarified

* How many observer nodes are needed in practice; should we auto‑spawn them? → **5 observer nodes, with auto-spawn possible.**
* Do control rules remain simple thresholds or require a rules engine? → **Simple threshold: if water_level ≥ 5 meters, alert.**
* What error handling strategy when MQTT broker disconnects? → **Backup broker + reconnect strategy.**
* Assumed non‑secure public broker in defaults; real deployments may require TLS. → **TLS is required.**
* Mapping coordinates are static; dynamic location updates may be needed later. → **People will move between Køge Torv and Køge Søndre Strand based on water level.**

> **Note:** This document assumes readers are familiar with basic MQTT concepts and Python. The system is designed for educational use and may not meet production reliability standards.
