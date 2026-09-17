"""Diagnostics support for Sofar."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import LKICS2ConfigEntry

TO_REDACT = {"serial_number"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: LKICS2ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    device = entry.runtime_data.device
    raw = await device.async_read_raw()

    return async_redact_data(
        {
            "readings_components": device.zones,
            "updated": entry.runtime_data.data.updated,
            "raw": raw,
        },
        TO_REDACT,
    )
