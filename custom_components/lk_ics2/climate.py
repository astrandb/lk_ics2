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
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LKICS2ConfigEntry, LKICS2Coordinator
from .entity import LKICS2Entity
from .lk_modbus import MAX_TEMP, MAX_ZONES, MIN_TEMP, LKICS2Controller

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class LKICS2ClimateDescription(ClimateEntityDescription):
    """Describe a sensor backed by a device attribute."""

    value_fn: Callable[[LKICS2Controller], float | None]
    report_name: str  # the name mentioned in the update report
    index: int | None = None


ENTITIES: tuple[LKICS2ClimateDescription, ...] = (
    *(
        LKICS2ClimateDescription(
            key=f"climate_{idx}",
            name=None,
            report_name=f"zone_{idx}.readings",
            index=idx,
            value_fn=lambda device, idx=idx: device.zones[idx].current_temperature,
        )
        for idx in range(1, MAX_ZONES + 1)
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LKICS2ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for the LK ICS.2 integration."""
    coordinator = entry.runtime_data
    async_add_entities(
        LKICS2Climate(coordinator, description)
        for description in ENTITIES
        if description.index in coordinator.device.zones
    )


class LKICS2Climate(LKICS2Entity, ClimateEntity):
    """Representation of a sensor for the LK ICS.2 integration."""

    entity_description: LKICS2ClimateDescription
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
        coordinator: LKICS2Coordinator,
        entity_description: LKICS2ClimateDescription,
    ) -> None:
        """Initialize the entity."""
        if TYPE_CHECKING:
            assert entity_description.index is not None
        super().__init__(coordinator, entity_description, entity_description.index)
        self.entity_description = entity_description
        self.coordinator = coordinator

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
