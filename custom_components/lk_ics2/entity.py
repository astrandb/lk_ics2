"""LK ICS.2 Entity class."""

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LKICS2Coordinator


class LKICS2Entity(CoordinatorEntity[LKICS2Coordinator]):
    """LK ICS.2 Entity class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LKICS2Coordinator,
        entity_description: EntityDescription,
        idx: int,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        if TYPE_CHECKING:
            assert coordinator.config_entry
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{coordinator.config_entry.entry_id}_{idx}",
                ),
            },
            manufacturer="LK Systems",
            model="ICS.2",
            translation_key="zone",
            translation_placeholders={"index": str(idx)},
        )
