import logging
from datetime import date
import aiohttp
from .const import BASE_API_URL

_LOGGER = logging.getLogger(__name__)
DAYS_OF_HISTORY = 29 # 29 + today, so 30 days total including today

class Thermostat:
    def __init__(self, json):
        self.serial_number = json["SerialNumber"]
        self.room = json["Room"]
        self.day_energy_usages = []

    def update_energy_usage(self, day_energy_usages):
        self.day_energy_usages = day_energy_usages

class DayEnergyUsage:
    def __init__(self, json):
        usage_jsons = json["Usage"]
        hour_usages = []
        for index, usage_json in enumerate(usage_jsons):
            hour_usages.append(HourEnergyUsage(usage_json, index))
        self.hour_usages = hour_usages

class HourEnergyUsage:
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
            resp = await self.session.post(
                url=url,
                json=request_body
            )
        
        json = await resp.json()
        return json

    # all starts here
    async def login(self):
        """logs in to API."""
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

                energy_usage_jsons = result["EnergyUsage"]
                day_energy_usages = []
                for json in energy_usage_jsons:
                    day_energy_usages.append(DayEnergyUsage(json))

                thermostat.update_energy_usage(day_energy_usages)
            except Exception as err:
                _LOGGER.debug("THERMOST ERRORs")
                _LOGGER.debug(err)
                return "no data"
            
        return self.thermostats

class ApiAuthError(Exception):
    """just a custom error"""
