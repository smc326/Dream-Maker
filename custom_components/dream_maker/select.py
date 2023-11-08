import logging

from homeassistant.components.select import SelectEntity
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
        Platform.SELECT,
        lambda coordinator, device, attribute: DreamSelect(coordinator, device, attribute)
    )


class DreamSelect(DreamAbstractEntity, SelectEntity):

    def __init__(self, coordinator: DeviceCoordinator, device: DreamDevice, attribute: DreamAttribute):
        super().__init__(coordinator, device, attribute)

        if 'value_comparison_table' not in attribute.ext.keys():
            raise ValueError('value_comparison_table must exist')

    def _update_value(self):
        self._attr_current_option = self._get_value_from_comparison_table(self.coordinator.data[self._attribute.key])

    def select_option(self, option: str) -> None:
        self._send_command({
            self._attribute.key: self._get_value_from_comparison_table(option)
        })

    def _get_value_from_comparison_table(self, value):
        value_comparison_table = self._attribute.ext.get('value_comparison_table', {})
        if str(value) not in value_comparison_table:
            _LOGGER.warning('Device [{}] attribute [{}] value [{}] not recognizable'.format(
                self._device.id, self._attribute.key, value
            ))
            return value

        return value_comparison_table.get(str(value))
