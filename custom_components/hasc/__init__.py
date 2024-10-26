"""GitHub Custom Component."""

import logging

from homeassistant import config_entries, core
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN
import asyncio
from homeassistant.const import UnitOfEnergy, UnitOfMass, UnitOfPower
from .sensor import MyThermostatApiClientSensor, MyThermostatApiClientCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity,
)
from homeassistant.helpers.entity import EntityCategory

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass, entry, async_add_entities
) -> bool:
    """Set up platform from a ConfigEntry"""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data


    config = hass.data[DOMAIN][entry.entry_id]
    session = async_get_clientsession(hass)
    username = config["username"]
    password = config["password"]
    coordinator = MyThermostatApiClientCoordinator(hass, session, username, password)
    try:
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
        return True
    except (asyncio.TimeoutError) as ex:
        raise ConfigEntryNotReady(f"Timeout while connecting") from ex



async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """test"""
    hass.data.setdefault(DOMAIN, {})
    return True
