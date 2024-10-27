import json
import logging
from datetime import date
import aiohttp
from .const import BASE_API_URL

_LOGGER = logging.getLogger(__name__)
DAYS_OF_HISTORY = 0 # 0 + today, so 1 day total including today

class Thermostat:
    def __init__(self, json):
        self.serial_number = json["SerialNumber"]
        self.room = json["Room"]
        self.energy_usage = []

    def update_energy_usage(self, energy_usage):
        self.energy_usage = energy_usage

class EnergyUsage:
    def __init__(self, json, time):
        self.energy_in_kwh = json["EnergyKWattHour"]
        self.time = time

class MyThermostatApi:
    
    def __init__(self, session: aiohttp.ClientSession, username: str, password: str):
        # body of the constructor
        self.session = session
        self.username = username
        self.password = password
        self.session_id = ""
        self.thermostats = []

    async def __apiCall(self, method, url, request_body=None):
        """the actual API caller"""
        resp = None
        if method == "GET":
            resp = await self.session.get(url)

        elif method == "POST":
            _LOGGER.debug("BODY%s", request_body)
            resp = await self.session.post(
                url=url,
                json=request_body
            )
        
        _LOGGER.debug("RESPONSE")
        _LOGGER.debug("%s", resp)
        json = await resp.json()
        _LOGGER.debug("JSON RESULT")
        _LOGGER.debug("%s", json)
        return json

    # all starts here
    async def login(self):
        """logs in to API"""
        request_body = {
            "Email": self.username,
            "Password": self.password,
            "Application": 8,
            "Confirm": ""
        }
        json = await self.__apiCall("POST",
         f"{BASE_API_URL}/authenticate/user",
         request_body
        )

        self.session_id = json["SessionId"]
        return json

    async def _get_thermostats(self):
        """test"""
        try:
            result = await self.__apiCall(
                "GET",
                f"{BASE_API_URL}/thermostats?sessionId={self.session_id}",
            )
            _LOGGER.debug("summary result")
            _LOGGER.debug(result)
            tstats_json = result["Groups"][0]["Thermostats"]
            tstats = []
            for tstat_json in tstats_json:
                tstats.append(Thermostat(tstat_json))

            self.thermostats = tstats
            return tstats
        except Exception as err:
            return "no data"
        
    async def get_energy_usage(self):
        """test"""
        await self._get_thermostats()

        today = date.today()
        today_param = today.strftime("%d/%m/%Y,")
        for thermostat in self.thermostats:
            try:
                result = await self.__apiCall(
                    "GET",
                    f"{BASE_API_URL}/energyusage?sessionId={self.session_id}&serialnumber={thermostat.serial_number}&view=day&date={today_param}&history={DAYS_OF_HISTORY}&calc=false&weekstart=monday"
                )
                _LOGGER.debug("summary result")
                _LOGGER.debug(result)
                energy_usage_jsons = result["EnergyUsage"]
                energy_usages = []
                for json in energy_usage_jsons:
                    usage_jsons = json["Usage"]
                    for index, usage_json in enumerate(usage_jsons):
                        energy_usages.append(EnergyUsage(usage_json, index))

                thermostat.update_energy_usage(energy_usages)
            except Exception as err:
                return "no data"
            
        return self.thermostats

class ApiAuthError(Exception):
    """just a custom error"""
