"""The LK ICS.2 integration."""

import logging

from modbus_connection import ModbusSerialParams

from homeassistant.components.modbus import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SERIAL_PORT, CONF_UNIT
from .coordinator import SCAN_INTERVAL, LKICS2Coordinator
from .lk_modbus import LKICS2Controller

_LOGGER = logging.getLogger(__name__)
_PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR, Platform.SWITCH]

type LKICS2ConfigEntry = ConfigEntry[LKICS2Coordinator]


async def async_setup_entry(hass: HomeAssistant, entry: LKICS2ConfigEntry) -> bool:
    """Set up LK ICS.2 from a config entry."""

    unit = async_get_unit(
        hass,
        entry,
        ModbusSerialParams(
            device=entry.data[CONF_SERIAL_PORT],
            baudrate=38400,
            framer="rtu",
        ),
        entry.data[CONF_UNIT],
    )

    device = LKICS2Controller(unit)
    coordinator = LKICS2Coordinator(
        hass, entry, device, device.async_update, SCAN_INTERVAL
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    _LOGGER.debug(
        "Zone 1 temperature: %s", coordinator.device.zones[1].current_temperature
    )
    _LOGGER.debug(
        "Zone 4 temperature: %s", coordinator.device.zones[4].current_temperature
    )

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: LKICS2ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
