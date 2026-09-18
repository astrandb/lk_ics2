"""Switch entities for LK ICS.2 integration."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, override

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import LKICS2ConfigEntry, LKICS2Coordinator
from .entity import LKICS2Entity
from .lk_modbus import MAX_ZONES, LKICS2Controller

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class LKICS2SwitchDescription(SwitchEntityDescription):
    """Describe a switch backed by a device attribute."""

    value_fn: Callable[[LKICS2Controller], bool | None]
    set_fn: Callable[[LKICS2Controller, bool], Awaitable[None]]
    report_name: str  # the name mentioned in the update report
    index: int | None = None


ENTITIES: tuple[LKICS2SwitchDescription, ...] = (
    *(
        LKICS2SwitchDescription(
            key=f"keylock_{idx}",
            translation_key="keylock",
            entity_category=EntityCategory.CONFIG,
            report_name=f"zone_{idx}.settings",
            index=idx,
            value_fn=lambda device, idx=idx: device.zones[idx].keylock,
            set_fn=lambda device, new_state, idx=idx: device.zones[
                idx
            ].async_set_keylock(new_state),
        )
        for idx in range(1, MAX_ZONES + 1)
    ),
    *(
        LKICS2SwitchDescription(
            key=f"backlight_{idx}",
            translation_key="backlight",
            entity_category=EntityCategory.CONFIG,
            report_name=f"zone_{idx}.settings",
            index=idx,
            value_fn=lambda device, idx=idx: device.zones[idx].backlight,
            set_fn=lambda device, new_state, idx=idx: device.zones[
                idx
            ].async_set_backlight(new_state),
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
        LKICS2Switch(coordinator, description)
        for description in ENTITIES
        if description.index in coordinator.device.zones
    )


class LKICS2Switch(LKICS2Entity, SwitchEntity):
    """Representation of a switch for the LK ICS.2 integration."""

    entity_description: LKICS2SwitchDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LKICS2Coordinator,
        entity_description: LKICS2SwitchDescription,
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
        """Return True if the switch is available."""
        return (
            super().available
            and self.entity_description.report_name in self.coordinator.data.updated
        )

    @property
    @override
    def is_on(self) -> bool | None:
        """Return the current value of the switch."""
        return self.entity_description.value_fn(self.coordinator.device)

    @override
    async def async_turn_on(self) -> None:
        """Turn the switch on."""
        if TYPE_CHECKING:
            assert self.entity_description.index is not None
        await self.entity_description.set_fn(self.coordinator.device, True)
        await self.coordinator.async_request_refresh()

    @override
    async def async_turn_off(self) -> None:
        """Turn the switch off."""
        if TYPE_CHECKING:
            assert self.entity_description.index is not None
        await self.entity_description.set_fn(self.coordinator.device, False)
        await self.coordinator.async_request_refresh()
