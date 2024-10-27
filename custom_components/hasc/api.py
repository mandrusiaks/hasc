import json
import logging
from datetime import date
import aiohttp
from .const import BASE_API_URL

_LOGGER = logging.getLogger(__name__)
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
            resp = await self.session.post(
                url=url,
                data=request_body,
                headers={"content-type": "application/json; charset=utf-8"},
            )
        
        json = await resp.json()
        return json

    # all starts here
    async def login(self):
        """logs in to API"""
        request_body = {
            "Email": self.username,
            "Password": self.password,
        }
        json = await self.__apiCall("POST",
         f"{BASE_API_URL}/authenticate/user",
         request_body
        )

        # if json["message"] == "Invalid Request":
        #     raise ApiAuthError("Failed to authenticate")
        # if json["message"] != "Succeed to login":
        #     raise ApiAuthError("Unknown error occured")

        self.session_id = json["SessionId"]
        return json

    # necessary calls: login -> this
    # async def get_ecu_info(self):
    #     """fetches ecu info (we need ecu ID)"""
    #     request_body = {
    #         "access_token": self.accessToken,
    #         "openId": self.openId,
    #         "language": "en_US",
    #         "userId": self.login_result["system"]["user_id"],
    #         "apiuser": API_USER,
    #     }
    #     data = await self.__apiCall(
    #         request_body, f"{BASE_API_URL}/view/registration/ecu/getEcuInfoBelowUser"
    #     )
    #     return list(data["data"].values())[0]

    async def get_thermostats(self):
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
                    f"{BASE_API_URL}/energyusage?sessionId={self.session_id}&serialnumber={thermostat.serial_number}&view=day&date={today_param}&history=10&calc=false&weekstart=monday"
                )
                _LOGGER.debug("summary result")
                _LOGGER.debug(result)
                energy_usage_jsons = result["EnergyUsage"]
                energy_usages = []
                for index, energy_usage_json in enumerate(energy_usage_jsons):
                    energy_usages.append(EnergyUsage(energy_usage_json, index))

                thermostat.update_energy_usage(energy_usages)
            except Exception as err:
                return "no data"
            
        return self.thermostats

#     # necessary calls: login -> getEcuInfo -> this
#     async def get_production_for_day(self):
#         """fetches production data for a day"""
#         datestring = datetime.now().strftime("%Y%m%d")
#         ecudata = await self.get_ecu_info()
#         request_body = {
#             "date": datestring,
#             "access_token": self.accessToken,
#             "systemId": self.login_result["system"]["system_id"],
#             "openId": self.openId,
#             "language": "en_US",
#             "ecuId": ecudata["ecuId"],
#             "apiuser": API_USER,
#         }
#         result = await self.__apiCall(
#             request_body, f"{BASE_API_URL}/view/production/ecu/getPowerOnCurrentDay"
#         )
#         _LOGGER.debug("productionForDay result")
#         _LOGGER.debug(result)
#         return result.get("data", "no data")
#         # "data":{
#         #     "duration":123, # ???
#         #     "total":"12.3456", # kwh
#         #     "max":"1234.5", # watts
#         #     ...
#         #     ],
#         #     "co2":"12.3456", # kgs
#         #     "time":[ # timestamp-string[]
#         #     ...
#         #     ],
#         #     "power":[ # watts-string[]
#         #     ...
#         #     ],
#         #     "energy":[ # kwh-string[] (from the last 5 minutes?)
#         #     ...
#         #     ]
#         # },


class ApiAuthError(Exception):
    """just a custom error"""
