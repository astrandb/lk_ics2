"""lk-ics2-modbus — read and control LK Systems ICS.2 underfloor heating over Modbus.

Built on ``modbus-connection``::

    from modbus_connection import ModbusSerialParams
    from modbus_connection.tmodbus import ModbusConnection
    from lk_ics2_modbus import LKICS2Controller

    connection = ModbusConnection(
        ModbusSerialParams(port="/dev/ttyUSB0", baudrate=38400)
    )
    controller = LKICS2Controller(connection.for_unit(1))
    await controller.async_update()
    print("Zone 1 temperature:", controller.zones[1].current_temperature)
"""

from .const import (
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_STOPBITS,
    DEFAULT_UNIT_ID,
    DEFAULT_ZONE_COUNT,
    MAX_TEMP,
    MAX_ZONES,
    MIN_TEMP,
    TEMP_PRECISION,
    TEMP_SCALE,
    ZONE_BASE_OFFSET,
    ZONE_STRIDE,
)
from .device import LKICS2Controller
from .model import LKICS2Component, UpdateReport
from .zone import Zone, ZoneReadings, ZoneSettings

__all__ = [
    "DEFAULT_BAUDRATE",
    "DEFAULT_BYTESIZE",
    "DEFAULT_PARITY",
    "DEFAULT_STOPBITS",
    "DEFAULT_UNIT_ID",
    "DEFAULT_ZONE_COUNT",
    "LKICS2Component",
    "LKICS2Controller",
    "MAX_TEMP",
    "MAX_ZONES",
    "MIN_TEMP",
    "TEMP_PRECISION",
    "TEMP_SCALE",
    "UpdateReport",
    "ZONE_BASE_OFFSET",
    "ZONE_STRIDE",
    "Zone",
    "ZoneReadings",
    "ZoneSettings",
]
