"""The LK ICS.2 integration."""

from modbus_connection import ModbusSerialParams

from custom_components.lk_ics2.lk_modbus import LKICS2Controller
from homeassistant.components.modbus import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SERIAL_PORT, CONF_UNIT

_PLATFORMS: list[Platform] = []

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
type LKICS2ConfigEntry = ConfigEntry[MyApi]  # noqa: F821


async def async_setup_entry(hass: HomeAssistant, entry: LKICS2ConfigEntry) -> bool:
    """Set up LK ICS.2 from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

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

    # connection = ModbusConnection(
    #     ModbusSerialParams(device=entry.data[CONF_SERIAL_PORT], baudrate=38400)
    # )
    controller = LKICS2Controller(unit)
    # controller = LKICS2Controller(connection.for_unit(1))
    # print("Updating controller...")
    await controller.async_update()
    # print("Zone 1 temperature:", controller.zones[1].current_temperature)

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: LKICS2ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
