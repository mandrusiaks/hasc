"""GitHub Custom Component."""

import logging

from homeassistant import config_entries, core
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN
import asyncio

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the sensor platform.
    try:
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    except (asyncio.TimeoutError) as ex:
        raise ConfigEntryNotReady(f"Timeout while connecting") from ex



async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """test"""
    hass.data.setdefault(DOMAIN, {})
    return True
