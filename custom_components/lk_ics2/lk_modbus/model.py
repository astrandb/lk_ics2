"""Base component classes and reporting models for LK ICS.2."""

from __future__ import annotations

from dataclasses import dataclass

from modbus_connection import ModbusError
from modbus_connection.model import Component


@dataclass(frozen=True)
class UpdateReport:
    """What one poll refreshed; a failed component keeps its prior values."""

    updated: set[str]
    failed: dict[str, ModbusError]

    @property
    def complete(self) -> bool:
        """Whether every polled component refreshed."""
        return not self.failed


class LKICS2Component(Component):
    """A sub-system / register block of an LK ICS.2 controller."""

    max_span = 100
