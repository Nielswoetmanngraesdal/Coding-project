from datetime import datetime

import pytest

from simulated_city.flood import (
    TriggerEvent,
    ObserverReading,
    ControlCommand,
    ResponseStatus,
)
from simulated_city.config import FloodConfig, load_config


def test_trigger_event_serialization():
    evt = TriggerEvent(event="rain", severity="high", timestamp="2025-01-01T00:00:00Z")
    data = evt.to_json()
    assert data["event"] == "rain"
    assert data["severity"] == "high"
    assert data["timestamp"] == "2025-01-01T00:00:00Z"
    restored = TriggerEvent.from_json(data)
    assert restored == evt


def test_observer_reading_serialization():
    r = ObserverReading(sensor_id="s1", water_level=1.5, flow_rate=0.2, timestamp="2025-01-01T00:00:00Z")
    data = r.to_json()
    assert isinstance(data["water_level"], float)
    assert data["flow_rate"] == 0.2
    assert r == ObserverReading.from_json(data)


def test_control_command_serialization():
    c = ControlCommand(action="alert", target="area1", parameters={"msg": "hi"}, timestamp="now")
    assert c == ControlCommand.from_json(c.to_json())


def test_response_status_serialization():
    s = ResponseStatus(device="pump1", status="running", details="ok", timestamp="now")
    assert s == ResponseStatus.from_json(s.to_json())


def test_response_status_structured_details_serialization():
    details = {
        "evacuated": 3,
        "in_transit": 7,
        "pedestrians": [
            {"id": "person_1", "lat": 55.45, "lon": 12.19, "location": "strand"}
        ],
    }
    s = ResponseStatus(device="response", status="running", details=details, timestamp="now")
    restored = ResponseStatus.from_json(s.to_json())
    assert isinstance(restored.details, dict)
    assert restored.details["evacuated"] == 3


def test_flood_config_parsing(tmp_path, monkeypatch):
    yaml = tmp_path / "cfg.yaml"
    yaml.write_text(
        """
        mqtt:
          host: test
          port: 1234
          tls: false
        flood:
          trigger_interval_s: 2.5
          map_center: [12.3, 45.6]
        """
    )
    cfg = load_config(str(yaml))
    assert cfg.flood is not None
    assert cfg.flood.trigger_interval_s == 2.5
    assert cfg.flood.map_center == (12.3, 45.6)


def test_flood_config_defaults():
    cfg = FloodConfig()
    assert cfg.control_threshold == 2.0
    assert cfg.map_zoom == 12
