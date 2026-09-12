"""Constants for LK Systems ICS.2 Modbus communication."""

from __future__ import annotations

# Communication defaults
DEFAULT_UNIT_ID = 1
DEFAULT_BAUDRATE = 38400
DEFAULT_STOPBITS = 1
DEFAULT_BYTESIZE = 8
DEFAULT_PARITY = "N"

# Zone constraints and addressing
DEFAULT_ZONE_COUNT = 12
MAX_ZONES = 12
ZONE_BASE_OFFSET = 1000
ZONE_STRIDE = 100

# Temperature limits
MIN_TEMP = 7.0
MAX_TEMP = 35.0
TEMP_SCALE = 0.01
TEMP_PRECISION = 1
