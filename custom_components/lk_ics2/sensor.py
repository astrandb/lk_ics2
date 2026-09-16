"""Sensors for LK ICS.2 integration."""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import override

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LKICS2ConfigEntry, LKICS2Coordinator
from .lk_modbus import LKICS2Controller

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MyDeviceSensorDescription(SensorEntityDescription):
    """Describe a sensor backed by a device attribute."""

    value_fn: Callable[[LKICS2Controller], float | None]
    report_name: str  # the name mentioned in the update report


SENSORS: tuple[MyDeviceSensorDescription, ...] = (
    MyDeviceSensorDescription(
        key="temperature",
        name="Zone 1 Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        report_name="sensors",
        value_fn=lambda device: device.zones[1].current_temperature,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LKICS2ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for the LK ICS.2 integration."""
    coordinator = entry.runtime_data
    async_add_entities(MySensor(coordinator, description) for description in SENSORS)


class MySensor(CoordinatorEntity[LKICS2Coordinator], SensorEntity):
    """Representation of a sensor for the LK ICS.2 integration."""

    entity_description: MyDeviceSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        runtime_data: LKICS2Coordinator,
        entity_description: MyDeviceSensorDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(runtime_data)
        self.entity_description = entity_description
        self.coordinator = runtime_data

    @property
    @override
    def available(self) -> bool:
        """Return True if the sensor is available."""
        return (
            super().available
            and self.entity_description.report_name in self.coordinator.data.updated
        )

    @property
    @override
    def native_value(self) -> float | None:
        """Return the current value of the sensor."""
        return self.entity_description.value_fn(self.coordinator.device)
