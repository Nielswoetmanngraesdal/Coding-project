from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Literal, Any, Dict


ISOTime = str  # ISO8601 timestamp


@dataclass(frozen=True, slots=True)
class TriggerEvent:
    event: Literal["rain", "dam_break"]
    severity: Literal["low", "medium", "high"]
    timestamp: ISOTime

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_json(data: dict[str, Any]) -> "TriggerEvent":
        return TriggerEvent(
            event=data["event"],
            severity=data["severity"],
            timestamp=data["timestamp"],
        )


@dataclass(frozen=True, slots=True)
class ObserverReading:
    sensor_id: str
    water_level: float  # meters
    flow_rate: float  # m^3/s
    timestamp: ISOTime

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_json(data: dict[str, Any]) -> "ObserverReading":
        return ObserverReading(
            sensor_id=data["sensor_id"],
            water_level=float(data["water_level"]),
            flow_rate=float(data["flow_rate"]),
            timestamp=data["timestamp"],
        )


@dataclass(frozen=True, slots=True)
class ControlCommand:
    action: Literal["activate_pump", "close_gate", "alert"]
    target: str
    parameters: dict[str, Any]
    timestamp: ISOTime

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_json(data: dict[str, Any]) -> "ControlCommand":
        return ControlCommand(
            action=data["action"],
            target=data["target"],
            parameters=data.get("parameters", {}),
            timestamp=data["timestamp"],
        )


@dataclass(frozen=True, slots=True)
class ResponseStatus:
    device: str
    status: Literal["idle", "running", "error"]
    details: str
    timestamp: ISOTime

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_json(data: dict[str, Any]) -> "ResponseStatus":
        return ResponseStatus(
            device=data["device"],
            status=data["status"],
            details=data.get("details", ""),
            timestamp=data["timestamp"],
        )
