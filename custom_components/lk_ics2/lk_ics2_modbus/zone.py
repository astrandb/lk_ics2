"""Zone models and register mapping for LK ICS.2."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection.model import coil, discrete_input, gauge, integer

from .const import ZONE_STRIDE
from .model import LKICS2Component

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


class ZoneReadings(LKICS2Component):
    """Input telemetry registers and discrete status inputs for one zone."""

    register_space = "input"

    current_temperature = gauge(1001, 0.01, stride=ZONE_STRIDE, signed=True, unit="°C")
    battery_level = integer(1003, stride=ZONE_STRIDE, signed=False, unit="%")
    heating = discrete_input(1003, stride=ZONE_STRIDE)


class ZoneSettings(LKICS2Component):
    """Holding configuration registers and coils for one zone."""

    register_space = "holding"

    target_temperature = gauge(
        1002, 0.01, stride=ZONE_STRIDE, signed=True, unit="°C", writable=True
    )
    bypass_temperature = integer(
        1011, stride=ZONE_STRIDE, signed=True, unit="°C", writable=True
    )
    backlight = coil(1002, stride=ZONE_STRIDE, writable=True)


class Zone:
    """A single room/channel zone on an LK ICS.2 controller."""

    def __init__(self, unit: ModbusUnit, index: int, name: str | None = None) -> None:
        """Initialize a zone with its 1-based index."""
        self.index = index
        self.name = name or f"Zone {index}"
        self.readings = ZoneReadings(unit, index=index)
        self.settings = ZoneSettings(unit, index=index)

    @property
    def current_temperature(self) -> float | None:
        """Current measured room temperature in °C."""
        return self.readings.current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Target setpoint temperature in °C."""
        return self.settings.target_temperature

    @property
    def battery_level(self) -> int | None:
        """Thermostat battery level in %."""
        return self.readings.battery_level

    @property
    def heating(self) -> bool | None:
        """Whether the zone heating actuator is actively open/heating."""
        return self.readings.heating

    @property
    def backlight(self) -> bool | None:
        """Whether the thermostat display backlight is turned on."""
        return self.settings.backlight

    @property
    def bypass_temperature(self) -> int | None:
        """Bypass setting / temperature for the zone."""
        return self.settings.bypass_temperature

    async def async_set_target_temperature(self, temperature: float) -> None:
        """Set the target setpoint temperature."""
        await self.settings.write("target_temperature", temperature)

    async def async_set_backlight(self, enabled: bool) -> None:
        """Set the display backlight state."""
        await self.settings.write("backlight", enabled)

    async def async_set_bypass_temperature(self, temperature: int) -> None:
        """Set the bypass temperature / setting."""
        await self.settings.write("bypass_temperature", temperature)
