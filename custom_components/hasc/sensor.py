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


# async def async_setup_entry(
#     hass: core.HomeAssistant,
#     config_entry: config_entries.ConfigEntry,
#     async_add_entities,
# ):
#     """Setup sensors from a config entry created in the integrations UI."""
#     config = hass.data[DOMAIN][config_entry.entry_id]
#     session: aiohttp.ClientSession = async_get_clientsession(hass)
#     username = config["username"]
#     password = config["password"]
#     coordinator = ThermostatCoordinator(hass, session, username, password)
#     await coordinator.async_config_entry_first_refresh()
#     _LOGGER.debug("CHECK THERMOSTATUS")
#     _LOGGER.debug("%s", len(coordinator.api.thermostats))
#     for thermostat in coordinator.api.thermostats:
#         async_add_entities(
#             [
#                 ThermostatDailyUsageSensor(
#                     coordinator,
#                     thermostat,
#                 ),
#             ]
#         )

# class ThermostatDailyUsageSensor(CoordinatorEntity, SensorEntity):
#     """Representation of a sensor."""

#     def __init__(
#         self,
#         coordinator,
#         thermostat,
#     ):
#         """Pass coordinator to CoordinatorEntity."""
#         super().__init__(coordinator)

#         _LOGGER.debug("THERMOSTAT SENSOR")

#         energy_usage_total = 0
#         for usage in thermostat.energy_usage:
#             energy_usage_total += usage.energy_in_kwh

#         self.coordinator = coordinator
#         self.thermostat = thermostat
#         self._state = energy_usage_total
#         self._available = True

#     @property
#     def unique_id(self):
#         return self.thermostat.serial_number or self.name

#     @property
#     def name(self):
#         return "Energy Used Today",

#     @property
#     def device_class(self):
#         return SensorDeviceClass.ENERGY

#     @property
#     def last_reset(self):
#         if self._state_class == SensorStateClass.TOTAL:
#             return get_todays_midnight()
#         return None

#     @property
#     def state(self) -> Optional[str]:
#         energy_usage_total = 0
#         for usage in self.thermostat.energy_usage:
#             energy_usage_total += usage.energy_in_kwh
#         return energy_usage_total

#     @property
#     def icon(self):
#         return "mdi:lightning-bolt"

#     @property
#     def unit_of_measurement(self):
#         return UnitOfEnergy.KILO_WATT_HOUR

#     @property
#     def state_class(self):
#         return SensorStateClass.TOTAL
    
#     @property
#     def entity_category(self):
#         return EntityCategory.DIAGNOSTIC

#     @property 
#     def suggested_display_precision(self):
#         return 2
    
#     @property
#     def device_info(self):
#         return {
#             "identifiers": {(DOMAIN, self.unique_id)},
#             "manufacturer": "Schluter",
#             "name": f"{self.thermostat.room} Thermostat",
#         }

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
                MyThermostatApiClientSensor(
                    coordinator,
                    thermostat=thermostat,
                    label=f"Thermostat {thermostat.serial_number}",
                    dev_class=SensorDeviceClass.ENERGY,
                    icon="mdi:lightning-bolt",
                    unit=UnitOfEnergy.KILO_WATT_HOUR,
                    entity_category=EntityCategory.DIAGNOSTIC,
                    state_class=SensorStateClass.TOTAL,
                ),
            ]
        )
    # async_add_entities(
    #     [
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="current_power",
    #             label="current power generation",
    #             dev_class=SensorDeviceClass.POWER,
    #             icon="mdi:solar-power",
    #             unit=UnitOfPower.WATT,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.MEASUREMENT,
    #         ),
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="today_total_kwh",
    #             label="energy generated today",
    #             dev_class=SensorDeviceClass.ENERGY,
    #             icon="mdi:lightning-bolt",
    #             unit=UnitOfEnergy.KILO_WATT_HOUR,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.TOTAL,
    #         ),
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="today_co2_kg",
    #             label="co2 reduced",
    #             dev_class=SensorDeviceClass.CO2,
    #             icon="mdi:molecule-co2",
    #             unit=UnitOfMass.KILOGRAMS,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.TOTAL,
    #         ),
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="system_capacity",
    #             label="System capacity",
    #             dev_class=SensorDeviceClass.POWER,
    #             icon="mdi:solar-power-variant",
    #             unit=UnitOfPower.WATT,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.MEASUREMENT,
    #         ),
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="lifetime_co2_kg",
    #             label="CO2 reduced in lifetime",
    #             dev_class=SensorDeviceClass.CO2,
    #             icon="mdi:molecule-co2",
    #             unit=UnitOfMass.KILOGRAMS,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.TOTAL_INCREASING,
    #         ),
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="month_total_kwh",
    #             label="Energy generated this month",
    #             dev_class=SensorDeviceClass.ENERGY,
    #             icon="mdi:lightning-bolt",
    #             unit=UnitOfEnergy.KILO_WATT_HOUR,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.TOTAL,
    #         ),
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="lifetime_total_kwh",
    #             label="Energy generated during lifetime",
    #             dev_class=SensorDeviceClass.ENERGY,
    #             icon="mdi:lightning-bolt",
    #             unit=UnitOfEnergy.KILO_WATT_HOUR,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.TOTAL_INCREASING,
    #         ),
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="tree_years",
    #             label="trees saved?",
    #             dev_class=None,
    #             icon="mdi:pine-tree",
    #             unit=None,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.TOTAL_INCREASING,
    #         ),
    #         MyThermostatApiClientSensor(
    #             coordinator,
    #             field="year_total_kwh",
    #             label="Energy generated this year",
    #             dev_class=SensorDeviceClass.ENERGY,
    #             icon="mdi:lightning-bolt",
    #             unit=UnitOfEnergy.KILO_WATT_HOUR,
    #             entity_category=EntityCategory.DIAGNOSTIC,
    #             state_class=SensorStateClass.TOTAL,
    #         ),
    #     ]
    # )


class MyThermostatApiClientSensor(CoordinatorEntity, SensorEntity):
    """Representation of a sensor."""

    def __init__(
        self,
        coordinator,
        # field,
        thermostat,
        label,
        dev_class,
        icon,
        unit,
        entity_category,
        state_class=None,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        _LOGGER.debug("THERMOSTAT SENSOR")
        _LOGGER.debug("%s", thermostat)

        energy_usage_total = 0
        for usage in thermostat.energy_usage:
            energy_usage_total += usage.energy_in_kwh

        self.coordinator = coordinator
        self.thermostat = thermostat
        self._name = label
        # self._field = "ditra_" + field
        # self.field = field
        self._label = label
        # if not label:
        #     self._label = field
        self._dev_class = dev_class
        self._icon = icon
        self._entity_category = entity_category
        self._state_class = state_class

        self._unit = unit
        self._state = energy_usage_total # self.coordinator.data[self.field]
        self._available = True

    @property
    def unique_id(self):
        return self._name

    @property
    def name(self):
        return self._name

    @property
    def device_class(self):
        return SensorDeviceClass.ENERGY

    @property
    def last_reset(self):
        if self._state_class == SensorStateClass.TOTAL:
            return get_todays_midnight()
        return None

    @property
    def state(self) -> Optional[str]:
        energy_usage_total = 0
        for usage in self.thermostat.energy_usage:
            energy_usage_total += usage.energy_in_kwh
        return energy_usage_total

    @property
    def icon(self):
        return "mdi:lightning-bolt"

    @property
    def unit_of_measurement(self):
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def state_class(self):
        return SensorStateClass.TOTAL

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": "Schluter DITRA Client tst",
        }

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC