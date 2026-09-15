"""Top-level LK ICS.2 controller device."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
import logging
from typing import TYPE_CHECKING

from modbus_connection import ModbusConnectionError, ModbusError

from .const import DEFAULT_ZONE_COUNT
from .model import LKICS2Component, UpdateReport
from .zone import Zone

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

_LOGGER = logging.getLogger(__name__)


class LKICS2Controller:
    """An LK Systems ICS.2 underfloor heating controller on a ``ModbusUnit``."""

    def __init__(
        self,
        unit: ModbusUnit,
        *,
        zone_count: int = DEFAULT_ZONE_COUNT,
        zones: Sequence[int] | None = None,
    ) -> None:
        """Initialize the controller with a ModbusUnit and configured zones."""
        self.unit = unit
        indices = zones if zones is not None else range(1, zone_count + 1)
        self.zones: dict[int, Zone] = {idx: Zone(unit, idx) for idx in indices}
        self._listeners: list[Callable[[], None]] = []

    def get_zone(self, index: int) -> Zone:
        """Retrieve a zone by its 1-based index."""
        if index not in self.zones:
            self.zones[index] = Zone(self.unit, index)
        return self.zones[index]

    def add_update_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a callback for completed controller updates.

        Returns a zero-argument callable that unregisters the listener.
        """
        self._listeners.append(listener)
        return lambda: self.remove_update_listener(listener)

    def remove_update_listener(self, listener: Callable[[], None]) -> None:
        """Remove a previously registered update callback."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify(self, report: UpdateReport) -> None:
        """Notify updated components and top-level listeners."""
        for name in report.updated:
            parts = name.split(".")
            if len(parts) == 2 and parts[0].startswith("zone_"):
                zone_idx = int(parts[0].removeprefix("zone_"))
                comp_type = parts[1]
                zone = self.zones.get(zone_idx)
                if zone is not None:
                    component: LKICS2Component = getattr(zone, comp_type)
                    component.notify()
        for listener in list(self._listeners):
            try:
                listener()
            except Exception:  # pylint: disable=broad-exception-caught  # noqa: PERF203
                _LOGGER.exception("Error in update listener")

    async def _async_poll(
        self,
        components: Iterable[tuple[str, LKICS2Component]],
        report: UpdateReport | None = None,
    ) -> UpdateReport:
        """Poll the provided named components."""
        if report is None:
            report = UpdateReport(updated=set(), failed={})

        for name, component in components:
            try:
                await component.async_update(notify=False)
            except ModbusConnectionError:  # noqa: PERF203
                raise
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.add(name)

        self._notify(report)
        return report

    async def async_update_readings(self) -> UpdateReport:
        """Refresh telemetry measurements for all zones."""
        components = [
            (f"zone_{idx}.readings", zone.readings) for idx, zone in self.zones.items()
        ]
        return await self._async_poll(components)

    async def async_update_settings(self) -> UpdateReport:
        """Refresh configuration registers for all zones."""
        components = [
            (f"zone_{idx}.settings", zone.settings) for idx, zone in self.zones.items()
        ]
        return await self._async_poll(components)

    async def async_update(self) -> UpdateReport:
        """Refresh both telemetry and configuration across all zones."""
        components: list[tuple[str, LKICS2Component]] = []
        for idx, zone in self.zones.items():
            components.append((f"zone_{idx}.readings", zone.readings))
            components.append((f"zone_{idx}.settings", zone.settings))
        return await self._async_poll(components)

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Dump all declared registers and bits undecoded for diagnostics."""
        raw: dict[str, dict[int, int | bool]] = {
            "input_registers": {},
            "holding_registers": {},
            "coils": {},
            "discrete_inputs": {},
        }

        for zone in self.zones.values():
            base = 1000 + (zone.index - 1) * 100
            try:
                in_regs = await self.unit.read_input_registers(base + 1, 3)
                for i, val in enumerate(in_regs):
                    raw["input_registers"][base + 1 + i] = val
            except ModbusError:
                pass

            try:
                hold_regs = await self.unit.read_holding_registers(base + 1, 11)
                for i, val in enumerate(hold_regs):
                    raw["holding_registers"][base + 1 + i] = val
            except ModbusError:
                pass

            try:
                coils = await self.unit.read_coils(base + 2, 1)
                if coils:
                    raw["coils"][base + 2] = coils[0]
            except ModbusError:
                pass

            try:
                discs = await self.unit.read_discrete_inputs(base + 3, 1)
                if discs:
                    raw["discrete_inputs"][base + 3] = discs[0]
            except ModbusError:
                pass

        return raw
