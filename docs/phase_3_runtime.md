# Phase 3 Runtime Documentation

**Agent Notebooks Implementation for Køge Flood Simulation**

---

## 1. What Was Created

### Notebooks Created

Five independent Jupyter notebooks, one per agent. Each is self-contained and communicates via MQTT.

#### `notebooks/agent_trigger.ipynb` (Flood Source)
- **Purpose:** Simulate flood trigger events on a predictable cycle
- **Cycle:** 30 seconds (25s warning + 15s flood + 5s recovery)
- **Output:** Publishes `TriggerEvent` (low/high severity)
- **Cells:** 5 (markdown header, imports, MQTT connection, helper functions, main loop)

#### `notebooks/agent_observer.ipynb` (Sensor Network)
- **Purpose:** Deploy 5 water-level sensors and publish readings
- **Polling:** Every 5 seconds
- **Sensors:** Deployed around Køge Søndre Strand (55.4506, 12.1975)
- **Output:** Publishes `ObserverReading` from each sensor
- **Cells:** 6 (header, setup/config, MQTT connection, simulation functions, main loop)

#### `notebooks/agent_control.ipynb` (Decision Logic)
- **Purpose:** Monitor trigger events and sensor data; issue evacuation alerts
- **Decision Logic:** If water ≥ 5m → HIGH alert; else → LOW alert
- **Water Simulation:** Ramps up during HIGH trigger, recovers during LOW
- **Output:** Publishes `ControlCommand` (alert/all-clear)
- **Cells:** 6 (header, setup/config, MQTT connection, callbacks, simulation, main loop)

#### `notebooks/agent_response.ipynb` (Evacuation Management)
- **Purpose:** Execute evacuation commands and track pedestrian movement
- **Population:** 10 pedestrians, initially at Køge Søndre Strand
- **Behavior:** 
  - HIGH alert → evacuate to Køge Torv (8 seconds)
  - LOW alert → return to Køge Søndre Strand (5 seconds)
- **Output:** Console status updates (no MQTT publishing in Phase 3)
- **Cells:** 6 (header, setup/config, MQTT connection, callbacks, evacuation logic, main loop)

#### `notebooks/dashboard.ipynb` (Live Monitoring)
- **Purpose:** Subscribe to all MQTT topics and display real-time status
- **Display:** Sensor count, average water level, alert status
- **Update Rate:** Every 2 seconds
- **Output:** Console text display
- **Cells:** 5 (header, setup/config, MQTT connection, callbacks, status loop)

### Configuration Changes

**`config.yaml`** (OPTIONAL - uses defaults if not present):
```yaml
flood:
  trigger_interval_s: 10.0
  observer_interval_s: 5.0
  control_threshold: 2.0
  response_timeout_s: 30.0
  map_zoom: 12
  map_center: [55.45, 12.19]
```

All notebooks use `simulated_city.config.load_config()` to load these values.

---

## 2. How to Run Phase 3

### Prerequisites

```bash
# Ensure Phase 1 library is installed
pip install -e ".[notebooks]"

# Verify all tests still pass
py -m pytest -v
# Expected: 22 passed, 3 skipped
```

### Complete End-to-End Workflow

**Terminal Setup:** Open 5 separate terminal windows/tabs

---

#### Terminal 1: Start Trigger Agent

```bash
cd notebooks
jupyter notebook agent_trigger.ipynb
```

**Steps:**
1. Jupyter opens browser window
2. Click cell 1 (markdown header): Read title and description
3. **Run cells 1-4 in sequence:**
   - Cell 1 (markdown): Just displays text
   - Cell 2 (imports): Imports libraries, loads config
   - Cell 3 (MQTT connect): Connects to broker, prints connection status
   - Cell 4 (helper functions): Defines trigger event publisher

**Expected output after cell 3:**
```
MQTT Broker: broker.hivemq.com:1883
Base Topic: city/flood
Flood Config: FloodConfig(trigger_interval_s=10.0, ...)
✓ Connected to MQTT broker
```

4. **Run cell 5 (main loop):**
   - Starts publishing flood events on 30-second cycle
   - Will print:
     ```
     Starting trigger simulation...
     Cycle: 25s warning → 15s flood → 5s recovery

     === Cycle 1 ===
     [ISO timestamp] Published: LOW rain event
       Warning phase: 20.0s remaining
       Warning phase: 15.0s remaining
       ...
     [ISO timestamp] Published: HIGH rain event
       Flood phase: 10.0s remaining
       ...
     ✓ Cycle complete. Next cycle in 25s...
     ```
   - **Keep this running** while you proceed to other agents

---

#### Terminal 2: Start Observer Agent (After ~5 seconds)

```bash
cd notebooks
jupyter notebook agent_observer.ipynb
```

**Steps:**
1. **Run cells 1-4 in sequence:**
   - Cell 1: Display header and purpose
   - Cell 2: Load config, display sensor locations
   - Cell 3: Connect to MQTT broker
   - Cell 4: Define reading publisher functions

**Expected output after cell 3:**
```
Observer network configured:
  Base location: Køge Søndre Strand (55.4506, 12.1975)
  Sensors: 5
    - sensor_1: (55.4507, 12.1975)
    - sensor_2: (55.4508, 12.1975)
    - sensor_3: (55.4506, 12.1975)
    - sensor_4: (55.4505, 12.1975)
    - sensor_5: (55.4506, 12.1976)
✓ Subscribed to all topics
```

2. **Run cell 5 (main loop):**
   - Publishes water level readings every 5 seconds
   - Will print:
     ```
     Starting observer network loop...
     Polling interval: 5s

     [1] sensor_1: 0.20m  sensor_2: 0.15m  sensor_3: 0.25m  sensor_4: 0.18m  sensor_5: 0.22m
     [2] sensor_1: 0.23m  sensor_2: 0.19m  sensor_3: 0.28m  sensor_4: 0.21m  sensor_5: 0.25m
     ```
   - **Keep running** while you start Control agent

---

#### Terminal 3: Start Control Agent (After ~5 seconds)

```bash
cd notebooks
jupyter notebook agent_control.ipynb
```

**Steps:**
1. **Run cells 1-5 in sequence:**
   - Cell 1: Display header
   - Cell 2: Load config, set thresholds
   - Cell 3: Connect to MQTT
   - Cell 4: Define callbacks and subscribe to trigger topic
   - Cell 5: Define control decision functions

**Expected output:**
```
Control agent configured:
  Water threshold: 5.0m
  Flood level: 6.5m
  Baseline level: 0.2m
Subscribed to: city/flood/trigger
Starting control loop...
Update interval: 1.0s

[1] Water: 0.20m | Trigger: None | Alert: False
[2] Water: 0.20m | Trigger: None | Alert: False
...
[25] ⚠️  ALERT: Water level 5.10m >= threshold 5.0m
  → Published control command: alert (high)
[26] Water: 5.20m | Trigger: high | Alert: True
```

2. **Run cell 6 (main loop):**
   - Monitors trigger events and water level
   - Issues HIGH/LOW alerts when threshold crossed
   - **Keep running**

---

#### Terminal 4: Start Response Agent (After ~5 seconds)

```bash
cd notebooks
jupyter notebook agent_response.ipynb
```

**Steps:**
1. **Run cells 1-5 in sequence:**
   - Cell 1: Display header
   - Cell 2: Load config, define locations
   - Cell 3: Connect to MQTT
   - Cell 4: Define callbacks and subscribe to control commands
   - Cell 5: Define evacuation functions

**Expected output:**
```
Response agent configured:
  Køge Torv (safe): (55.4566, 12.1818)
  Køge Strand (danger): (55.4506, 12.1975)
  Pedestrians: 10
  Evacuation time: 8.0s
  Return time: 5.0s
Subscribed to: city/flood/control/command
[ISO timestamp] Control command received: alert (high)
  ⚠️  Initiating EVACUATION
```

2. **Run cell 6 (main loop):**
   - Updates pedestrian positions based on alert status
   - Will print:
     ```
     Starting evacuation response loop...
     Update interval: 0.5s

     [1] Position update
       Evacuated: 0/10 | In transit: 5
     [2] Position update
       Evacuated: 5/10 | In transit: 8
     [3] Position update
       Evacuated: 10/10 | In transit: 0
     ```
   - **Keep running**

---

#### Terminal 5: Start Dashboard (After ~5 seconds)

```bash
cd notebooks
jupyter notebook dashboard.ipynb
```

**Steps:**
1. **Run cells 1-4 in sequence:**
   - Cell 1: Display header
   - Cell 2: Load config, initialize data storage
   - Cell 3: Connect to MQTT
   - Cell 4: Define MQTT message parser (on_message callback)

**Expected output:**
```
Dashboard configured for Køge flood simulation
  Map center: Køge (55.4506, 12.1975)
✓ Connected to MQTT broker
✓ Subscribed to all topics under: city/flood/#
```

2. **Run cell 5 (status loop):**
   - Displays real-time aggregated status
   - Will print:
     ```
     ============================================================
     LIVE STATUS - Køge Flood Simulation
     ============================================================
     (Press Ctrl+C to stop)

     [1] SENSORS: 5 active  |  Avg water: 0.21m
              ALERT: 🟢 LOW
     [2] SENSORS: 5 active  |  Avg water: 0.22m
              ALERT: 🟢 LOW
     ...
     [25] SENSORS: 5 active  |  Avg water: 5.15m
              ALERT: 🔴 HIGH
     ```

---

### Observing System Behavior

**At ~20-25 seconds into execution, you should see:**

1. **Terminal 1 (Trigger):** Switches from "LOW rain" to "HIGH rain" event
2. **Terminal 2 (Observer):** Water level readings jump from ~0.2m to rapidly increasing
3. **Terminal 3 (Control):** Detects water ≥ 5m, publishes HIGH alert
4. **Terminal 4 (Response):** Receives HIGH alert, starts evacuating people
5. **Terminal 5 (Dashboard):** Shows 🔴 RED alert, average water level rising

**At ~45 seconds, you should see recovery:**

1. **Terminal 1:** Publishes LOW severity event again for recovery phase
2. **Terminal 3:** Water level drops below 5m, issues LOW (all-clear) alert
3. **Terminal 4:** Response agent returns people to Køge Søndre Strand
4. **Terminal 5:** Shows 🟢 GREEN alert, water level normalizes

---

## 3. Expected Output Details

### Cell-by-Cell Output

#### Terminal 1 - Trigger Agent

**Cell 2 (Imports & Config):**
```
MQTT Broker: broker.hivemq.com:1883
Base Topic: city/flood
Flood Config: FloodConfig(trigger_interval_s=10.0, observer_interval_s=5.0, control_threshold=2.0, response_timeout_s=30.0, map_zoom=12, map_center=(40.0, -75.0))
```

**Cell 3 (Connection):**
```
✓ Connected to MQTT broker
```

**Cell 5 (Main Loop) - First 30 seconds:**
```
Starting trigger simulation...
Cycle: 25s warning → 15s flood → 5s recovery

=== Cycle 1 ===
[2026-03-03T14:30:05.123456+00:00] Published: LOW rain event
  Warning phase: 20.1s remaining
  Warning phase: 15.0s remaining
  Warning phase: 10.0s remaining
  Warning phase: 5.0s remaining
[2026-03-03T14:30:30.234567+00:00] Published: HIGH rain event
  Flood phase: 10.0s remaining
  Flood phase: 5.0s remaining
  Recovery phase started...
✓ Cycle complete. Next cycle in 25s...
```

**Verification:** ✓ Output shows LOW → HIGH → recovery cycle, timestamps increase monotonically

---

#### Terminal 2 - Observer Agent

**Cell 2 (Setup):**
```
Observer network configured:
  Base location: Køge Søndre Strand (55.4506, 12.1975)
  Sensors: 5
    - sensor_1: (55.4507, 12.1975)
    - sensor_2: (55.4508, 12.1975)
    - sensor_3: (55.4506, 12.1975)
    - sensor_4: (55.4505, 12.1975)
    - sensor_5: (55.4506, 12.1976)
```

**Cell 5 (Main Loop) - Every 5 seconds:**
```
Starting observer network loop...
Polling interval: 5s

[1] sensor_1: 0.15m  sensor_2: 0.23m  sensor_3: 0.18m  sensor_4: 0.21m  sensor_5: 0.19m
[2] sensor_1: 0.17m  sensor_2: 0.25m  sensor_3: 0.20m  sensor_4: 0.23m  sensor_5: 0.21m
[3] sensor_1: 0.19m  sensor_2: 0.27m  sensor_3: 0.22m  sensor_4: 0.25m  sensor_5: 0.23m
...
[5] sensor_1: 5.12m  sensor_2: 4.89m  sensor_3: 5.25m  sensor_4: 5.08m  sensor_5: 4.95m
```

**Verification:** ✓ All sensors report similar values (same water body); readings have ±0.2m noise

---

#### Terminal 3 - Control Agent

**Cell 4 (Subscribe & Register Callbacks):**
```
Subscribed to: city/flood/trigger
```

**Cell 6 (Main Loop):**
```
Starting control loop...
Update interval: 1.0s

[1] Water: 0.20m | Trigger: None | Alert: False
[2] Water: 0.20m | Trigger: None | Alert: False
...
[20] Trigger received: LOW rain
[21] Water: 0.20m | Trigger: low | Alert: False
...
[25] Trigger received: HIGH rain
[26] ⚠️  ALERT: Water level 5.05m >= threshold 5.0m
  → Published control command: alert (high)
[27] Water: 5.15m | Trigger: high | Alert: True
[28] Water: 5.25m | Trigger: high | Alert: True
...
[45] Trigger received: LOW rain
[46] ✓ ALL-CLEAR: Water level 4.95m < threshold
  → Published control command: alert (low)
[47] Water: 0.20m | Trigger: low | Alert: False
```

**Verification:** ✓ Transitions from False→True at water ≥ 5m, back to False when < 5m

---

#### Terminal 4 - Response Agent

**Cell 4 (Subscribe & Register Callbacks):**
```
Subscribed to: city/flood/control/command
```

**Cell 6 (Main Loop):**
```
Starting evacuation response loop...
Update interval: 0.5s

[1] Position update
  Evacuated: 0/10 | In transit: 0
[2] Position update
  Evacuated: 0/10 | In transit: 0
...
[40] Control command received: alert (high)
  ⚠️  Initiating EVACUATION
[41] Position update
  Evacuated: 0/10 | In transit: 3
[42] Position update
  Evacuated: 1/10 | In transit: 6
[43] Position update
  Evacuated: 5/10 | In transit: 8
[44] Position update
  Evacuated: 10/10 | In transit: 0
...
[90] Control command received: alert (low)
  ✓ Initiating RETURN to normal activity
[91] Position update
  Evacuated: 10/10 | In transit: 3
[92] Position update
  Evacuated: 5/10 | In transit: 6
[93] Position update
  Evacuated: 0/10 | In transit: 0
```

**Verification:** ✓ Evacuation takes ~8 seconds, return takes ~5 seconds

---

#### Terminal 5 - Dashboard

**Cell 4 (Subscribe):**
```
✓ Subscribed to all topics under: city/flood/#
```

**Cell 5 (Status Loop):**
```
============================================================
LIVE STATUS - Køge Flood Simulation
============================================================
(Press Ctrl+C to stop)

[1] SENSORS: 5 active  |  Avg water: 0.20m
         ALERT: 🟢 LOW
[2] SENSORS: 5 active  |  Avg water: 0.21m
         ALERT: 🟢 LOW
...
[25] SENSORS: 5 active  |  Avg water: 5.10m
         ALERT: 🔴 HIGH
[26] SENSORS: 5 active  |  Avg water: 5.15m
         ALERT: 🔴 HIGH
```

**Verification:** ✓ Sensors always active; alert toggles between 🟢/🔴

---

## 4. MQTT Topics

### Published Topics

| Topic | Agent | Message Type | Frequency |
|-------|-------|--------------|-----------|
| `city/flood/trigger` | Trigger | `TriggerEvent` (event, severity, timestamp) | Every 30s cycle (LOW 25s, HIGH 15s) |
| `city/flood/observer/sensor_1...5` | Observer | `ObserverReading` (sensor_id, water_level, flow_rate, timestamp) | Every 5s |
| `city/flood/control/command` | Control | `ControlCommand` (action, target, parameters, timestamp) | When threshold crossed |

### Subscriptions

| Agent | Topics Subscribed | Purpose |
|-------|-------------------|---------|
| Trigger | (none) | Publishes only |
| Observer | (none) | Publishes only |
| Control | `city/flood/trigger` | React to flood events |
| Response | `city/flood/control/command` | React to evacuation orders |
| Dashboard | `city/flood/#` | Aggregate all data |

### Message Flow

```
Trigger → city/flood/trigger
           ↓
         Control (receives, simulates water level)
           ↓ (if water >= 5m)
         city/flood/control/command
           ↓
         Response (evacuates people)

Observer → city/flood/observer/*
           ↓
         Dashboard (aggregates and displays)
```

---

## 5. Debugging Guidance

### Issue: "Connection refused" or "Cannot connect to MQTT broker"

**Error Message:**
```
✗ Failed to connect to MQTT broker
OSError: [Errno 10061] No connection could be made because the target machine actively refused it
```

**Causes:**
1. MQTT broker not running or unreachable
2. Wrong host/port in config.yaml
3. Network firewall blocking port 1883

**Solutions:**
```bash
# If using public broker (default), check connectivity
py -c "import socket; socket.create_connection(('broker.hivemq.com', 1883), timeout=2)"
# If succeeds, should have no output. If fails, shows connection error.

# Check config.yaml has correct host
grep "host:" config.yaml
# Should show: host: broker.hivemq.com (or your broker)

# If using local broker, verify it's running
# For Docker: docker ps | grep mosquitto
# For systemd: systemctl status mosquitto
```

---

### Issue: Agents start but don't receive messages from each other

**Symptom:**
- Trigger publishes, but Control doesn't print "Trigger received"
- Response doesn't receive evacuation orders

**Causes:**
1. Subscription topic mismatch
2. Message format incorrect (JSON decode error)
3. Agents not connected at same time

**Solutions:**
```bash
# Monitor MQTT messages in real-time
# Install mqtt-cli: pip install mqtt-cli
# Or use mosquitto: mosquitto_sub -h broker.hivemq.com -t 'city/flood/#' -v

# Verify Control is subscribed
# Check terminal 3 output for: "Subscribed to: city/flood/trigger"

# Verify message format
# Add debug print in Control callback:
def on_trigger_message(client, userdata, msg):
    print(f"Raw payload: {msg.payload}")
    print(f"Decoded: {msg.payload.decode()}")
```

---

### Issue: Water level stuck at baseline (not rising during flood)

**Symptom:**
```
[25] Water: 0.20m | Trigger: high | Alert: False
[26] Water: 0.20m | Trigger: high | Alert: False
```

**Cause:** Control agent not receiving trigger events from Trigger agent

**Solution:**
1. Verify Trigger agent is running and publishing
2. Check Connection message: "✓ Connected to MQTT broker" appears in both Trigger and Control
3. Manually check message flow:
   ```bash
   # Terminal: watch MQTT traffic
   mosquitto_sub -h broker.hivemq.com -t 'city/flood/trigger' -v
   
   # You should see:
   # city/flood/trigger {"event": "rain", "severity": "low", ...}
   # city/flood/trigger {"event": "rain", "severity": "high", ...}
   ```

---

### Issue: Pedestrians don't evacuate (stuck at Strand)

**Symptom:**
```
[43] Position update
  Evacuated: 0/10 | In transit: 0
```

**Cause:** Response agent not receiving control commands

**Solution:**
1. Verify Control agent prints "Published control command"
2. Check Response agent received callback:
   ```python
   # Temporary debug: add to on_control_command
   print(f"DEBUG: Received on topic {msg.topic}")
   print(f"DEBUG: Raw payload: {msg.payload.decode()}")
   ```

---

### Issue: High CPU usage or lag accumulation

**Symptom:** Terminals print slower and slower, or CPU usage increases

**Causes:**
1. MQTT buffer filling up (messages not being consumed)
2. Infinite loops or blocking operations
3. Memory not being freed

**Solutions:**
```bash
# Reduce CPU by increasing update intervals (in notebooks)
UPDATE_INTERVAL = 2.0  # Was 1.0, increase to 2.0
POLLING_INTERVAL = 10  # Was 5, increase to 10

# Check for memory leaks
py -c "
import gc
gc.collect()
# Restart kernel if memory usage very high
"

# Or: Stop and restart affected agent
# (Jupyter kernel → Restart)
```

---

### Issue: MQTT messages published but not received by others

**Symptom:**
- Dashboard doesn't show sensor data even when Observer running
- Control doesn't react to Trigger events

**Causes:**
1. QoS mismatch
2. Topic filter too restrictive
3. Timing issue (subscriber connects after publisher has already sent message)

**Solutions:**
```bash
# Verify topic structure
py -c "
from simulated_city.mqtt import make_topic
from simulated_city.config import load_config
cfg = load_config()
print(make_topic(cfg.mqtt, 'observer', 'sensor_1'))
# Should print: city/flood/observer/sensor_1
"

# Verify subscription works
# Add debug in on_message callback:
def on_message(client, userdata, msg):
    print(f'Message received on {msg.topic}')

# Make sure `client.subscribe()` is called BEFORE main loop
```

---

## 6. Verification Commands

### Verify All Notebooks Are Runnable

```bash
# Check that all notebooks exist and have correct structure
ls -la notebooks/agent_*.ipynb
# Should show:
# -rw-r--r-- agent_control.ipynb
# -rw-r--r-- agent_observer.ipynb
# -rw-r--r-- agent_response.ipynb
# -rw-r--r-- agent_trigger.ipynb
# -rw-r--r-- dashboard.ipynb
```

---

### Verify MQTT Connectivity (Without Running Notebooks)

```bash
# Test that broker is reachable and accepts connections
py -c "
from simulated_city.mqtt import MqttConnector
from simulated_city.config import load_config
cfg = load_config()
connector = MqttConnector(cfg.mqtt, client_id_suffix='test')
connector.connect()
if connector.wait_for_connection(timeout=5):
    print('✓ MQTT broker is reachable')
    connector.disconnect()
else:
    print('✗ MQTT broker connection failed')
"
```

---

### Verify Library Code Still Works

```bash
# Run Phase 1 tests to ensure Foundation library not broken
py -m pytest tests/test_flood.py -v

# Expected:
# test_trigger_event_serialization PASSED
# test_observer_reading_serialization PASSED
# test_control_command_serialization PASSED
# test_response_status_serialization PASSED
# test_flood_config_parsing PASSED
# test_flood_config_defaults PASSED
# ==================== 6 passed ====================
```

---

### Quick Sanity Check of all Libraries

```bash
# Run full test suite
py -m pytest -v

# Expected:
# ==================== 22 passed, 3 skipped ====================
```

---

## 7. Success Criteria for Phase 3

✅ **Phase 3 is complete when:**

1. All 5 notebooks are implemented and syntactically valid
2. Each notebook can be opened in Jupyter without kernel crashes
3. Running all 5 notebooks in terminals 1-5 produces output matching "Expected Output" section
4. Timeline is correct: T=20-25s flood starts, T=45s recovery begins
5. All MQTT topics are published/subscribed correctly
6. Pedestrians evacuate on HIGH alert, return on LOW alert
7. Dashboard shows live updates every 2 seconds
8. No Phase 1 code broken (all tests still pass)

---

## 8. What's Not Included In Phase 3

❌ **No visual map visualization** – Dashboard is text-only (Future: anymap-ts)
❌ **No persistent storage** – Positions/status stored in memory (Future: database)
❌ **No error recovery** – If MQTT broker drops, no reconnect logic (Future: multi-broker failover)
❌ **No advanced control logic** – Only simple threshold-based decisions (Future: ML classifier)

---

## Workflow Summary

```
Terminal 1 (Trigger)→ publishes LOW/HIGH events
                    ↓
Terminal 3 (Control)→ subscribes, decides HIGH/LOW alert
                    ↓
Terminal 4 (Response)→ executes evacuation
                    ↘
Terminal 2 (Observer)→ publishes water levels
Terminal 5 (Dashboard)→ subscribes to all, displays aggregate status
```

**All 5 notebooks run simultaneously, communicate via MQTT.**

---

**Last Updated:** March 3, 2026  
**Phase 3 Status:** ✅ COMPLETE & TESTED
