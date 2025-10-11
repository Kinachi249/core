"""Support for Cync switch entities."""

import logging
from typing import Any

from pycync import CyncPlug

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CyncConfigEntry, CyncCoordinator
from .entity import CyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: CyncConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Cync plugs from a config entry."""

    coordinator = entry.runtime_data
    cync = coordinator.cync

    entities_to_add = []

    for home in cync.get_homes():
        for room in home.rooms:
            room_plugs = [
                CyncPlugEntity(device, coordinator, room.name)
                for device in room.devices
                if isinstance(device, CyncPlug)
            ]
            entities_to_add.extend(room_plugs)

            group_plugs = [
                CyncPlugEntity(device, coordinator, room.name)
                for group in room.groups
                for device in group.devices
                if isinstance(device, CyncPlug)
            ]
            entities_to_add.extend(group_plugs)

    async_add_entities(entities_to_add)


class CyncPlugEntity(CyncBaseEntity, SwitchEntity):
    """Representation of a Cync plug."""

    _attr_translation_key = "plug"
    _attr_device_class = "outlet"
    _attr_name = None

    def __init__(
        self,
        device: CyncPlug,
        coordinator: CyncCoordinator,
        room_name: str | None = None,
    ) -> None:
        """Set up base attributes."""
        super().__init__(device, coordinator, room_name)

    @property
    def is_on(self) -> bool | None:
        """Return True if the plug is on."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Process an action on the plug."""
        await self._device.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self._device.turn_off()

    @property
    def _device(self) -> CyncPlug:
        """Fetch the reference to the backing Cync plug for this device."""

        return self.coordinator.data[self.unique_id]
