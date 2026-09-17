"""Climate entities for LK ICS.2 integration."""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Any, override

from homeassistant.components.climate import ClimateEntity, ClimateEntityDescription
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LKICS2ConfigEntry, LKICS2Coordinator
from .lk_modbus import MAX_TEMP, MIN_TEMP, LKICS2Controller

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MyDeviceClimateDescription(ClimateEntityDescription):
    """Describe a sensor backed by a device attribute."""

    value_fn: Callable[[LKICS2Controller], float | None]
    report_name: str  # the name mentioned in the update report
    index: int | None = None


ENTITIES: tuple[MyDeviceClimateDescription, ...] = (
    *(
        MyDeviceClimateDescription(
            key=f"climate_{idx}",
            translation_key="climate",
            translation_placeholders={"index": str(idx)},
            report_name=f"zone_{idx}.readings",
            index=idx,
            value_fn=lambda device, idx=idx: device.zones[idx].current_temperature,
        )
        for idx in range(1, 9)
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LKICS2ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for the LK ICS.2 integration."""
    coordinator = entry.runtime_data
    async_add_entities(MyClimate(coordinator, description) for description in ENTITIES)


class MyClimate(CoordinatorEntity[LKICS2Coordinator], ClimateEntity):
    """Representation of a sensor for the LK ICS.2 integration."""

    entity_description: MyDeviceClimateDescription
    _attr_has_entity_name = True
    _attr_precision = 0.1
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_max_temp = MAX_TEMP
    _attr_min_temp = MIN_TEMP

    def __init__(
        self,
        runtime_data: LKICS2Coordinator,
        entity_description: MyDeviceClimateDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(runtime_data)
        self.entity_description = entity_description
        self.coordinator = runtime_data
        self._attr_unique_id = f"{DOMAIN}_{self.entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"ABC123_{self.entity_description.index}",
                ),
            },
            manufacturer="LK Systems",
            model="ICS.2",
            name=f"Zone {self.entity_description.index}",
        )

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
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if TYPE_CHECKING:
            assert self.entity_description.index
        return self.coordinator.device.zones[
            self.entity_description.index
        ].current_temperature

    @property
    @override
    def target_temperature(self) -> float | None:
        """Return the target temperature."""

        if TYPE_CHECKING:
            assert self.entity_description.index
        return self.coordinator.device.zones[
            self.entity_description.index
        ].target_temperature

    @property
    @override
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action."""
        if TYPE_CHECKING:
            assert self.entity_description.index
        return (
            HVACAction.HEATING
            if self.coordinator.device.zones[self.entity_description.index].heating
            else HVACAction.IDLE
        )

    @override
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if TYPE_CHECKING:
            assert self.entity_description.index
        await self.coordinator.device.zones[
            self.entity_description.index
        ].async_set_target_temperature(kwargs.get("temperature", MIN_TEMP))
        await self.coordinator.async_request_refresh()
