import logging
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import ApiAuthError, MyThermostatApi


_LOGGER = logging.getLogger(__name__)


class MyThermostatApiClientCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, session, username, password):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Schluter DITRA Client Coordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=15),
        )
        self.api = MyThermostatApi(session, username, password)

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        # return
        try:
            # # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # # handled by the data update coordinator.
            # _LOGGER.warn(f"_async_update_data called!")
            statistics = {}
            await self.api.login()


            thermostats = await self.api.get_energy_usage()

            _LOGGER.debug("FINAL STATS")
            _LOGGER.debug(thermostats)
            return thermostats
        except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            _LOGGER.warn(
                "an exception occured during data update. Error was:", err)
            raise UpdateFailed("Error communicating with APS API.")
