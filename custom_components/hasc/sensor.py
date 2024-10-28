import logging
from datetime import timedelta
from typing import Optional
import aiohttp
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import UnitOfEnergy, UnitOfMass, UnitOfPower
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import EntityCategory
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import ThermostatCoordinator
from .utils import get_todays_midnight

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("username"): cv.string,
        vol.Required("password"): cv.string,
    }
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    session: aiohttp.ClientSession = async_get_clientsession(hass)
    username = config["username"]
    password = config["password"]
    coordinator = ThermostatCoordinator(hass, session, username, password)
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("CHECK THERMOSTATUS")
    _LOGGER.debug("%s", len(coordinator.api.thermostats))
    for thermostat in coordinator.api.thermostats:
        async_add_entities(
            [
                ThermostatDailyUsageSensor(
                    coordinator,
                    thermostat,
                ),
            ]
        )

class ThermostatDailyUsageSensor(CoordinatorEntity, SensorEntity):
    """Representation of a sensor."""

    def __init__(
        self,
        coordinator,
        thermostat,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.thermostat = thermostat
        self._icon = "mdi:lightning-bolt"
        self._state_class = SensorStateClass.TOTAL
        self._state = self.calculate_energy_usage()
        self._entity_category = EntityCategory.DIAGNOSTIC
        self._available = True
        self._name = "Energy Used Today"
        self._device_class = SensorDeviceClass.ENERGY
        self._unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._suggested_display_precision = 2


    @property
    def unique_id(self):
        return self.thermostat.serial_number or self._name

    @property
    def name(self):
        return self._name

    @property
    def device_class(self):
        return self._device_class

    @property
    def last_reset(self):
        if self._state_class == SensorStateClass.TOTAL:
            return get_todays_midnight()
        return None

    @property
    def state(self) -> Optional[str]:
        return self.calculate_energy_usage()

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def state_class(self):
        return self._state_class
    
    @property
    def entity_category(self):
        return self._entity_category

    @property 
    def suggested_display_precision(self):
        return self._suggested_display_precision
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Schluter",
            "name": f"{self.thermostat.room} Thermostat",
        }

    def calculate_energy_usage(self):
        energy_usage_total = 0
        for usage in self.thermostat.energy_usage:
            energy_usage_total += usage.energy_in_kwh
        return energy_usage_total
    