import enum
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
    for thermostat in coordinator.api.thermostats:
        async_add_entities(
            [
                ThermostatSensor(
                    coordinator,
                    thermostat,
                ),
            ]
        )

class ThermostatSensor(CoordinatorEntity, SensorEntity):
    """Representation of a sensor."""
    class EnergyType(enum):
        DAY = 1
        WEEK = 2
        MONTH = 3

    def __init__(
        self,
        coordinator,
        thermostat,
        energy_type
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.thermostat = thermostat
        self._attr_unique_id = thermostat.serial_number
        self._attr_icon = "mdi:lightning-bolt"
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_suggested_display_precision = 2
        self._attr_available = True

        self._attr_name = self._get_name(energy_type)
        self._attr_state = self._calculate_energy_usage(energy_type)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.thermostat.serial_number)},
            "manufacturer": "Schluter",
            "name": f"{self.thermostat.room} Thermostat",
        }
    @property
    def last_reset(self):
        return get_todays_midnight()

    @property
    def state(self) -> Optional[str]:
        return self.calculate_energy_usage()

    def _calculate_energy_usage(self, energy_type):
        number_of_days = 1
        match energy_type:
            case ThermostatSensor.EnergyType.DAY:
                number_of_days = 1
            case ThermostatSensor.EnergyType.WEEK:
                number_of_days = 7
            case ThermostatSensor.EnergyType.MONTH:
                number_of_days = 30

        energy_usage_total = 0
        for index in range(0, number_of_days):
            if index >= len(self.thermostat.energy_usage):
                break
            usage = self.thermostat.energy_usage[index]
            energy_usage_total += usage.energy_in_kwh

        return energy_usage_total

    def _get_name(self, energy_type):
        name = self.thermostat.room
        match energy_type:
            case ThermostatSensor.EnergyType.DAY:
                name += " Energy Used Today"
            case ThermostatSensor.EnergyType.WEEK:
                name += " Energy Used Last 7 Days"
            case ThermostatSensor.EnergyType.MONTH:
                name += " Energy Used Last 30 Days"
