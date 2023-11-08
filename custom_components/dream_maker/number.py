import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.typing import HomeAssistantType

from . import async_register_entity
from .coordinator import DeviceCoordinator
from .core.attribute import DreamAttribute
from .core.device import DreamDevice
from .entity import DreamAbstractEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities) -> None:
    await async_register_entity(
        hass,
        entry,
        async_add_entities,
        Platform.NUMBER,
        lambda coordinator, device, attribute: DreamNumber(coordinator, device, attribute)
    )


class DreamNumber(DreamAbstractEntity, NumberEntity):

    def __init__(self, coordinator: DeviceCoordinator, device: DreamDevice, attribute: DreamAttribute):
        super().__init__(coordinator, device, attribute)

    def _update_value(self):
        self._attr_native_value = self.coordinator.data[self._attribute.key]

    def set_native_value(self, value: float) -> None:
        self._send_command({
            self._attribute.key: value
        })



