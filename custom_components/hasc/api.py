import json
import logging
from datetime import datetime
import aiohttp
from .const import BASE_API_URL

_LOGGER = logging.getLogger(__name__)

class MyThermostatApi:
    
    def __init__(self, session: aiohttp.ClientSession, username: str, password: str):
        # body of the constructor
        self.session = session
        self.username = username
        self.password = password
        self.session_id = ""
        self.thermostat_ids = []

    async def __apiCall(self, request_body, url):
        """the actual API caller"""
        resp = await self.session.post(
            url=url,
            data=request_body,
            headers={"content-type": "application/json"},
        )
        _LOGGER.debug("RESPONSE %s", resp)
        jsonstr = await resp.text()
        _LOGGER.debug("call result: %s", jsonstr)
        result = json.loads(jsonstr)
        return result

    # all starts here
    async def login(self):
        """logs in to API"""
        request_body = {
            "Username": self.username,
            "Password": self.password,
            "Confirm": "",
            "Application": 8
        }
        data = await self.__apiCall(
            request_body, f"{BASE_API_URL}/view/registration/user/checkUser"
        )

        if data["message"] == "Invalid Request":
            raise ApiAuthError("Failed to authenticate")
        if data["message"] != "Succeed to login":
            raise ApiAuthError("Unknown error occured")

        self.session_id = data["SessionId"]
        return data

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

    # async def get_summary(self):
    #     """fetches summarized statistics"""

    #     try:
    #         request_body = {
    #             "access_token": self.accessToken,
    #             "openId": self.openId,
    #             "language": "en_US",
    #             "apiuser": API_USER,
    #             "userId": self.login_result["system"]["user_id"],
    #         }
    #         result = await self.__apiCall(
    #             request_body,
    #             f"{BASE_API_URL}/view/production/user/getSummaryProductionForEachSystem",
    #         )
    #         _LOGGER.debug("summary result")
    #         _LOGGER.debug(result)
    #         if result.get("data", False) is False:
    #             return "no data"
    #         return list(result["data"].values())[0]
    #     except Exception as err:
    #         return "no data"

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
