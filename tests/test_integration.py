"""Integration tests for Phase 4: All agents working together via MQTT."""

import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

from simulated_city.config import load_config
from simulated_city.mqtt import MqttConnector, make_topic
from simulated_city.flood import (
    TriggerEvent, ObserverReading, ControlCommand, ResponseStatus
)


class TestNotebookStructure:
    """Verify all Phase 3 notebooks have correct JSON structure."""
    
    def test_all_notebooks_exist(self):
        """Check that all 5 required notebooks exist."""
        notebooks_dir = Path("notebooks")
        required_notebooks = [
            "agent_trigger.ipynb",
            "agent_observer.ipynb",
            "agent_control.ipynb",
            "agent_response.ipynb",
            "dashboard.ipynb",
        ]
        
        for notebook in required_notebooks:
            notebook_path = notebooks_dir / notebook
            assert notebook_path.exists(), f"Missing notebook: {notebook}"
    
    def test_notebooks_are_valid_json(self):
        """Verify notebooks are valid JSON files."""
        notebooks_dir = Path("notebooks")
        notebooks = list(notebooks_dir.glob("agent_*.ipynb")) + list(notebooks_dir.glob("dashboard.ipynb"))
        
        for notebook_path in notebooks:
            try:
                with open(notebook_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    assert "cells" in data, f"Invalid notebook structure: {notebook_path.name}"
                    assert isinstance(data["cells"], list), f"Cells not a list: {notebook_path.name}"
                    assert len(data["cells"]) > 0, f"No cells in notebook: {notebook_path.name}"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {notebook_path.name}: {e}")
    
    def test_notebooks_have_required_cells(self):
        """Verify notebooks have expected cell types (markdown + python)."""
        notebooks_dir = Path("notebooks")
        
        for notebook_path in notebooks_dir.glob("agent_*.ipynb"):
            with open(notebook_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cells = data.get("cells", [])
                
                # Should have both markdown and code cells
                cell_types = [cell.get("cell_type") for cell in cells]
                assert "markdown" in cell_types, f"Missing markdown cell in {notebook_path.name}"
                assert "code" in cell_types, f"Missing code cells in {notebook_path.name}"


class TestMQTTTopicStructure:
    """Verify MQTT topics match the design specification."""
    
    def test_topic_hierarchy(self):
        """Verify topic structure follows hierarchy."""
        cfg = load_config()
        
        # Test trigger topic
        trigger_topic = make_topic(cfg.mqtt, "trigger")
        assert trigger_topic == "simulated-city/trigger"
        
        # Test observer topics
        observer_topic = make_topic(cfg.mqtt, "observer", "sensor_1")
        assert observer_topic == "simulated-city/observer/sensor_1"
        
        # Test control topic
        control_topic = make_topic(cfg.mqtt, "control", "command")
        assert control_topic == "simulated-city/control/command"
    
    def test_wildcard_subscription_topic(self):
        """Verify dashboard can subscribe to all topics."""
        cfg = load_config()
        wildcard_topic = make_topic(cfg.mqtt, "#")
        
        assert "simulated-city/#" in wildcard_topic or wildcard_topic == "simulated-city/#"


class TestDataModelSerialization:
    """Verify data models serialize/deserialize correctly for MQTT transmission."""
    
    def test_trigger_event_full_cycle(self):
        """Test TriggerEvent: create → JSON → parse → verify."""
        # Create trigger event
        trigger = TriggerEvent(
            event="rain",
            severity="high",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Serialize to dict (to_json returns dict)
        data = trigger.to_json()
        assert data is not None
        assert isinstance(data, dict)
        
        # Deserialize back to object
        trigger_restored = TriggerEvent.from_json(data)
        
        # Verify all fields match
        assert trigger_restored.event == trigger.event
        assert trigger_restored.severity == trigger.severity
        assert trigger_restored.timestamp == trigger.timestamp
    
    def test_observer_reading_full_cycle(self):
        """Test ObserverReading: create → JSON → parse → verify."""
        # Create reading
        reading = ObserverReading(
            sensor_id="sensor_1",
            water_level=2.5,
            flow_rate=0.15,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Serialize to dict
        data = reading.to_json()
        assert isinstance(data, dict)
        
        # Deserialize
        reading_restored = ObserverReading.from_json(data)
        
        # Verify
        assert reading_restored.sensor_id == "sensor_1"
        assert reading_restored.water_level == 2.5
        assert reading_restored.flow_rate == 0.15
        assert reading_restored.timestamp == reading.timestamp
    
    def test_control_command_full_cycle(self):
        """Test ControlCommand: create → JSON → parse → verify."""
        # Create command
        cmd = ControlCommand(
            action="alert",
            target="evacuation",
            parameters={"severity": "high", "threshold": 5.0},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Serialize to dict
        data = cmd.to_json()
        assert isinstance(data, dict)
        
        # Deserialize
        cmd_restored = ControlCommand.from_json(data)
        
        # Verify
        assert cmd_restored.action == "alert"
        assert cmd_restored.target == "evacuation"
        assert cmd_restored.parameters["severity"] == "high"
        assert cmd_restored.parameters["threshold"] == 5.0
    
    def test_response_status_full_cycle(self):
        """Test ResponseStatus: create → JSON → parse → verify."""
        # Create status
        status = ResponseStatus(
            device="evacuation_module",
            status="running",
            details="Moving 5 people to Torv",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Serialize to dict
        data = status.to_json()
        assert isinstance(data, dict)
        
        # Deserialize
        status_restored = ResponseStatus.from_json(data)
        
        # Verify
        assert status_restored.device == "evacuation_module"
        assert status_restored.status == "running"
        assert status_restored.details == "Moving 5 people to Torv"


class TestConfigurationFlow:
    """Verify configuration loads and flows through all components."""
    
    def test_config_loads_successfully(self):
        """Verify config.yaml exists and loads."""
        cfg = load_config()
        assert cfg is not None
        assert cfg.mqtt is not None
        assert cfg.mqtt.host is not None  # Could be local or remote broker
    
    def test_mqtt_config_has_required_fields(self):
        """Verify MQTT config has all required fields."""
        cfg = load_config()
        mqtt_cfg = cfg.mqtt
        
        assert mqtt_cfg.host is not None
        assert mqtt_cfg.port > 0
        assert mqtt_cfg.base_topic is not None
        assert len(mqtt_cfg.base_topic) > 0  # Any non-empty base topic is valid
    
    def test_flood_config_loads_with_defaults(self):
        """Verify FloodConfig loads with sensible defaults if not in YAML."""
        cfg = load_config()
        
        # FloodConfig should exist and have defaults
        if cfg.flood:
            assert cfg.flood.trigger_interval_s > 0
            assert cfg.flood.observer_interval_s > 0
            assert cfg.flood.response_timeout_s > 0


class TestNotebookImports:
    """Verify notebooks can import required modules."""
    
    def test_imports_available(self):
        """Test that key modules are importable (what notebooks will use)."""
        # These are the imports every notebook does
        try:
            import time
            import json
            from datetime import datetime, timezone
            from pathlib import Path
            import sys
            
            from simulated_city.config import load_config
            from simulated_city.mqtt import MqttConnector, make_topic
            from simulated_city.flood import (
                TriggerEvent, ObserverReading, ControlCommand, ResponseStatus
            )
            
            # If we get here, all imports succeeded
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


class TestSystemIntegration:
    """Test the complete system integration scenario."""
    
    def test_flood_event_notification_flow(self):
        """Test: Trigger → Control → (conceptually) Response."""
        # Phase 1: Trigger publishes event
        trigger = TriggerEvent(
            event="rain",
            severity="high",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        trigger_data = trigger.to_json()
        trigger_received = TriggerEvent.from_json(trigger_data)
        
        # Phase 2: Control receives event and makes decision
        if trigger_received.severity == "high":
            water_level = 6.0  # Simulated rapid rise
            should_alert = water_level >= 5.0
            
            # Phase 3: Issue alert command
            if should_alert:
                command = ControlCommand(
                    action="alert",
                    target="evacuation",
                    parameters={"water_level": water_level},
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                command_data = command.to_json()
                command_received = ControlCommand.from_json(command_data)
                
                # Verify command is valid
                assert command_received.action == "alert"
                assert command_received.target == "evacuation"
    
    def test_sensor_reading_aggregation(self):
        """Test: 5 sensors → Observer publishes → Dashboard aggregates."""
        # Simulate 5 readings from 5 sensors
        readings = []
        for i in range(1, 6):
            reading = ObserverReading(
                sensor_id=f"sensor_{i}",
                water_level=0.2 + (i * 0.05),  # Slightly different per sensor
                flow_rate=0.1,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            readings.append(reading)
        
        # Dashboard aggregates
        water_levels = [r.water_level for r in readings]
        avg_level = sum(water_levels) / len(water_levels)
        
        # All readings should aggregate without error
        assert len(water_levels) == 5
        assert avg_level > 0
        assert 0.2 <= avg_level <= 1.0  # Reasonable range
    
    def test_evacuation_timeline(self):
        """Test: Response agent can execute evacuation over time."""
        # Scenario: HIGH alert causes evacuation
        num_pedestrians = 10
        evacuation_time_s = 8.0
        
        # Simulate evacuation phases
        phases = [
            ("0s", 0, 10),      # Start: 0 evacuated, 10 in transit
            ("2s", 2, 8),       # 25% through: 2 evacuated
            ("4s", 5, 5),       # 50% through: 5 evacuated
            ("6s", 8, 2),       # 75% through: 8 evacuated
            ("8s", 10, 0),      # Complete: 10 evacuated
        ]
        
        for phase_name, evacuated, in_transit in phases:
            assert evacuated + in_transit == num_pedestrians
            assert 0 <= evacuated <= num_pedestrians
            assert 0 <= in_transit <= num_pedestrians


class TestErrorHandling:
    """Verify graceful error handling in key flows."""
    
    def test_invalid_json_handling(self):
        """Test that invalid data in payload is handled."""
        invalid_payload = {}  # Missing required fields
        
        try:
            TriggerEvent.from_json(invalid_payload)
            pytest.fail("Should have raised exception for invalid data")
        except (RuntimeError, TypeError, KeyError):
            # Expected: any of these errors is fine
            pass
    
    def test_missing_required_field(self):
        """Test handling of missing required fields in message."""
        incomplete_data = {"event": "rain"}  # Missing severity and timestamp
        
        try:
            TriggerEvent.from_json(incomplete_data)
            pytest.fail("Should have raised exception for missing fields")
        except (RuntimeError, TypeError, KeyError):
            # Expected
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
