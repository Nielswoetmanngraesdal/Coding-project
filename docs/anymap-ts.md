# anymap-ts runtime guide (flood simulation)

This guide shows how you run the workshop flood simulation on a live map using anymap-ts.

## Goal

Use the dashboard notebook to visualize:

- the two fixed zones in Køge (flood zone and safe zone)
- pedestrians moving between zones during HIGH/LOW flood alerts
- live sensor + alert status from MQTT

## Requirements

- anymap-ts is installed from project dependencies
- a local MQTT broker is running (Mosquitto on Windows)
- the flood agent notebooks are available

Install dependencies from the project root:

```bash
python -m pip install -e ".[dev,notebooks]"
```

## Quick checks

Verify anymap-ts import:

```bash
py -c "import anymap; print('anymap-ts available')"
```

Verify broker is reachable:

```powershell
sc query mosquitto
powershell Test-NetConnection -ComputerName localhost -Port 1883
```

## Configuration used by the map

The simulation reads settings from `config.yaml` via `simulated_city.config.load_config()`.

Relevant keys:

- `mqtt.base_topic` (default: `simulated-city`)
- `flood.map_center` (lat/lon tuple)
- `flood.map_zoom` (default zoom level)

The dashboard also uses fixed workshop coordinates:

- Køge Torv (safe zone)
- Køge Søndre Strand (flood zone)

## Run the simulation with map rendering

Start notebooks in separate terminals:

1. `agent_trigger.ipynb`
2. `agent_observer.ipynb`
3. `agent_control.ipynb`
4. `agent_response.ipynb`
5. `dashboard.ipynb`

From the `notebooks/` folder:

```bash
python -m jupyterlab
```

In `dashboard.ipynb`, run cells top-to-bottom. The map should show:

- static marker for flood zone
- static marker for safe zone
- moving markers for pedestrians during evacuation and return

## MQTT data flow for map updates

- Trigger publishes flood state
- Observer publishes sensor levels
- Control publishes HIGH/LOW alert commands
- Response publishes pedestrian positions in `response/status`
- Dashboard subscribes to `base_topic/#` and updates map markers incrementally

## Troubleshooting

If no map appears:

- confirm anymap-ts import works
- restart the notebook kernel
- rerun dashboard cells from top to bottom

If markers do not move:

- ensure `agent_response.ipynb` is running
- verify `response/status` messages include pedestrian coordinates
- check dashboard subscription: `simulated-city/#`

If MQTT data is missing:

- start/restart Mosquitto (`net start mosquitto`)
- verify active profile in `config.yaml` (`active_profiles: [local]`)

## Validation commands

```bash
py -m pytest tests/test_flood.py tests/test_phase5_enhancements.py -v
py -m pytest -v
```

## Rule compliance

This workshop uses anymap-ts for map rendering. Do not replace live mapping with folium, plotly, or matplotlib.
