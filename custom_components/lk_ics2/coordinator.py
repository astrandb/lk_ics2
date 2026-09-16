"""Data update coordinator for LK_ICS.2."""

from collections.abc import Awaitable, Callable
from datetime import timedelta

# from functools import cached_property
from functools import cached_property
import logging

from modbus_connection import ModbusError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# from . import LKICS2ConfigEntry
from .const import DOMAIN
from .lk_modbus import LKICS2Controller, UpdateReport

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)

type LKICS2ConfigEntry = ConfigEntry[LKICS2Coordinator]


class LKICS2Coordinator(DataUpdateCoordinator[UpdateReport]):
    """Run one of the device's update methods on its own interval."""

    _failed: frozenset[str] = frozenset()

    def __init__(
        self,
        hass: HomeAssistant,
        entry: LKICS2ConfigEntry,
        device: LKICS2Controller,
        poll: Callable[[], Awaitable[UpdateReport]],
        interval: timedelta,
    ) -> None:
        """Initialize the LKICS2Coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=entry.title,
            update_interval=interval,
        )

        self.device = device
        self._poll = poll

    async def _async_update_data(self) -> UpdateReport:
        try:
            report = await self._poll()
        except ModbusError as err:
            raise UpdateFailed(str(err)) from err
        if not report.updated:
            errors = list(report.failed.values())
            raise UpdateFailed(
                f"no sub-system answered: {errors[0]}"
            ) from ExceptionGroup("every sub-system failed", errors)

        for name in sorted(report.failed.keys() - self._failed):
            _LOGGER.warning("Failed to fetch %s: %s", name, report.failed[name])
        self._failed = frozenset(report.failed)
        return report

    @cached_property
    def device_info(self) -> DeviceInfo:
        """Describe the device to the registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"ABC123_{self.device.unit}")},
            manufacturer="LK Systems",
            model="ICS.2",
        )
