"""SonnenAPI v2 module."""

from functools import wraps
from typing import Dict, Optional, Union
from collections.abc import Awaitable
import json
import datetime
import logging

import aiohttp
import asyncio
import aiohttp_fast_zlib

import requests
import urllib3 
from urllib3.util.timeout import Timeout

from .const import *   # noqa: F403

def get_item(_type):
    """Decorator factory for getting data from the api dictionary and casting
    to the right type """
    def decorator(fn):
        @wraps(fn)
        def inner(*args):
            if fn(*args) is None:
                return None
            try:
                result = _type(fn(*args))
            except KeyError:
#                print('Key not found')
                result = None
            except ValueError:
#                print(f'{fn(*args)} is not an {_type} castable!')
                result = None
            return result
        return inner
    return decorator

class BatterieError(Exception):
    """Indicates network error communicating with batterie."""
    pass

class BatterieAuthError(Exception):
    """Indicates error authorising with batterie."""
    pass

class BatterieHTTPError(Exception):
    """Indicates (internal?) HTTP error with batterie."""
    pass

class Sonnen:
    """Class for managing Sonnen API V2 data."""
    from .wrapped import set_request_connect_timeouts, get_request_connect_timeouts
    from .wrapped import get_update, get_latest_data, get_configurations, get_status, get_powermeter, get_battery, get_inverter
    from .wrapped import sync_get_update, sync_get_latest_data, sync_get_configurations, sync_get_status, sync_get_powermeter, sync_get_battery, sync_get_inverter


    def __init__(self, auth_token: str, ip_address: str, ip_port: int = 80, logger_name: str = None) -> None:
        """Cache manager Sonnen API V2 data."""

        self._last_updated = None #rate limiters
        self._last_get_updated = None
        self._last_configurations = None

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if logger_name is not None:
            self.logger = logging.getLogger(logger_name)
        else:
            self.logger = logging.getLogger(__package__)

        self.ip_address = ip_address
        self.auth_token = auth_token
        self._hostname = f'{ip_address}:{ip_port}'
        self.url = f'http://{self._hostname}'
        self.header = {'Auth-Token': self.auth_token}
        self.request_timeouts = (TIMEOUT, TIMEOUT)  # noqa: F405
        self.client_timeouts = aiohttp.ClientTimeout(connect=TIMEOUT, sock_read=TIMEOUT)  # noqa: F405
        # read api endpoints
        self.status_api_endpoint = f'{self.url}/api/v2/status'
        self.latest_details_api_endpoint = f'{self.url}/api/v2/latestdata'
        self.battery_api_endpoint = f'{self.url}/api/v2/battery'
        self.powermeter_api_endpoint = f'{self.url}/api/v2/powermeter'
        self.configurations_api_endpoint = f'{self.url}/api/v2/configurations'
        self.inverter_api_endpoint = f'{self.url}/api/v2/inverter'

        # api data
        self._configurations:Dict = None
        self._status_data:Dict = None
        self._latest_details_data:Dict = None
        self._battery_status:Dict = None
        self._powermeter_data:Dict = None
        self._inverter_data:Dict = None
        # isal is preferred over zlib_ng if it is available
        aiohttp_fast_zlib.enable()

    def _log_error(self, msg):
        """Log message when error logger is present"""
        if self.logger:
            self.logger.error(msg)
        else:
            print(msg)

    def sync_validate_token(self) -> bool:
        """Check valid IP address & token can make connection.
            urllib3 used to access to low level exceptions obfuscated
            by aiohttp exception handler.
        """

        conn = urllib3.connection_from_url(self.configurations_api_endpoint,headers=self.header, retries=False)
        timeouts = Timeout(TIMEOUT, TIMEOUT)
        try:
            # response = conn.request('GET', self.configurations_api_endpoint, None, self.header)
            response = conn.urlopen('GET',
                            self.configurations_api_endpoint,
                            None,
                            self.header,
                            False,
                            timeout=timeouts
                            )

        except urllib3.exceptions.NewConnectionError:
            self._log_error(f'Invalid IP address "{self.configurations_api_endpoint}"')
            raise BatterieAuthError(f'Invalid IP address "{self.configurations_api_endpoint}"')
        except Exception as error:
            self._log_error(f'Sync fetch "{self.configurations_api_endpoint}" fail: {repr(error)}')
            raise BatterieError(f'Sync fetch "{self.configurations_api_endpoint}"  fail: {repr(error)}') from error

#        print(f'resp: {vars(response)}')

        if response.status in [401, 403]:
            raise BatterieAuthError(f'Invalid token "{self.auth_token}" status: {response.status}')
        elif response.status > 299:
            raise BatterieHTTPError(f'HTTP Error fetching endpoint "{self.configurations_api_endpoint}" status: {response.status}')

        self._configurations = json.loads(response._body)
        self._last_configurations = datetime.datetime.now()
        return True

    def _force_HTTPError(self) -> bool:
        """Make a bad GET request to the batterie which it responds to with status 301.
            ONLY to be used for testing!
        """

        conn = urllib3.connection_from_url(self.configurations_api_endpoint,headers=self.header, retries=False)
        try:
            response = conn.request('GET', '/')
        except Exception as error:
            self._log_error(f'Forced HTTP Error.  fail: {repr(error)}')
            raise BatterieError(f'Forced HTTP Error.  fail: {repr(error)}') from error

        if response.status > 299:
            raise BatterieHTTPError(f'HTTP Error fetching bad endpoint.  status: {response.status}')

        return False

    async def async_validate_token(self) -> Awaitable[bool]:
        """Check valid IP address & token can make connection.
            Called from HASS component event loop.
        """

        event_loop = asyncio.get_running_loop()

        return await event_loop.run_in_executor(None, self.sync_validate_token)

    async def async_update(self) -> Awaitable[bool]:
        """Update all battery data from an async caller.
        Returns:
            True when all updates successful or
            called again within rate limit interval.
        """

        now = datetime.datetime.now()
        if self._last_updated is not None:
            diff = now - self._last_updated
            if diff.total_seconds() < RATE_LIMIT:
                return True

        self._latest_details_data = None
        self._status_data = None
        self._battery_status = None
        self._powermeter_data = None
        self._inverter_data = None

        self._configurations = await self.async_fetch_configurations()
    #    print(f'_configurations: {self._configurations}')
        success = (self._configurations is not None)
        if success:
            self._latest_details_data = await self.async_fetch_latest_details()
    #        print(f'_latest_details: {self._latest_details_data}')
            success = (self._latest_details_data is not None)
        if success:
            self._status_data = await self.async_fetch_status()
    #        print(f'status: {self._status_data}')
            success = (self._status_data is not None)
        if success:
            self._battery_status = await self.async_fetch_battery_status()
    #        print(f'_battery: {self._battery_status}')
            success = (self._battery_status is not None)
        if success:
            self._powermeter_data = await self.async_fetch_powermeter()
    #        print(f'_powermeter: {self._powermeter_data}')
            success = (self._powermeter_data is not None)
        if success:
            self._inverter_data = await self.async_fetch_inverter()
    #        print(f'_inverter: {self._inverter_data}')
            success = (self._inverter_data is not None)

        self._last_updated = now if success else None
        return success

    def update(self) -> bool:
        """Update battery details Asyncronously from a sequential caller using async methods.
        Returns:
            True when all updates successful or
            called again within rate limit interval.
        """

        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        try:
            event_loop.run_until_complete(self.async_update())
        finally:
            event_loop.close()

        return (self._last_updated is not None)

    def sync_update(self) -> bool:
        """Update all battery data from a sequential caller using sync methods.
        Returns:
            True when all updates successful or
            called again within rate limit interval
        """

        now = datetime.datetime.now()
        if self._last_updated is not None:
            diff = now - self._last_updated
            if diff.total_seconds() < RATE_LIMIT:
                return True

        self._configurations = None
        self._latest_details_data = None
        self._status_data = None
        self._battery_status = None
        self._powermeter_data = None
        self._inverter_data = None

        self._configurations = self.fetch_configurations()
    #    print(f'_configurations: {self._configurations}')
        success = (self._configurations is not None)
        if success:
            self._latest_details_data = self.fetch_latest_details()
    #        print(f'_latest_details: {self._latest_details_data}')
            success = (self._latest_details_data is not None)
        if success:
            self._status_data = self.fetch_status()
    #        print(f'status: {self._status_data}')
            success = (self._status_data is not None)
        if success:
            self._battery_status = self.fetch_battery_status()
    #        print(f'_battery: {self._battery_status}')
            success = (self._battery_status is not None)
        if success:
            self._powermeter_data = self.fetch_powermeter()
    #        print(f'_powermeter: {self._powermeter_data}')
            success = (self._powermeter_data is not None)
        if success:
            self._inverter_data = self.fetch_inverter()
    #        print(f'_inverter: {self._inverter_data}')
            success = (self._inverter_data is not None)

        self._last_updated = now if success else None
        return success

    async def _async_fetch_api_endpoint(self, url: str) -> Awaitable[Dict]:
        """Fetch API coroutine."""

        try:
            async with aiohttp.ClientSession(headers=self.header, timeout=self.client_timeouts) as session:
                response = await self._async_fetch(session, url)

        except aiohttp.ClientConnectorDNSError as error:
            self._log_error(f'Battery: {self.ip_address} badIP? accessing: "{url}"  error: {error}')
            raise BatterieAuthError(f'Battery {self.ip_address} badIP? accessing: "{url}"  error: {error}') from error
#??        except BatterieError as error:

        except Exception as error:
            self._log_error(f'Coroutine fetch "{url}"  fail: {error}')
            raise BatterieError(f'Coroutine fetch "{url}"  fail: {error}') from error

#        print(f'resp: {response}')

        return response

    async def _async_fetch(self, session: aiohttp.ClientSession, url: str) -> Awaitable[Dict]: #Awaitable[aiohttp.ClientResponse]:
        """Fetch API endpoint with aiohttp client."""

        try:
            async with session.get(url) as response:
#                print(f'resp: {vars(response)}')
                if response.status > 299:
                    self._log_error(f'Error fetching endpoint "{url}" status: {response.status}')
                    if response.status in [401, 403]:
                        raise BatterieAuthError(f'Auth error fetching endpoint "{url}" status: {response.status}')
                    else:
                        raise BatterieHTTPError(f'HTTP error fetching endpoint "{url}" status: {response.status}')
                return await response.json()
        except aiohttp.ClientError as error:
            self._log_error(f'Battery: {self.ip_address} offline? accessing: "{url}"  error: {error}')
            raise BatterieError(f'Battery {self.ip_address} offline? accessing: "{url}"  error: {error}') from error
        except aiohttp.ClientConnectorDNSError as error:
            self._log_error(f'Battery: {self.ip_address} badIP? accessing: "{url}"  error: {error}')
            raise BatterieAuthError(f'Battery {self.ip_address} badIP? accessing: "{url}"  error: {error}') from error
        except asyncio.TimeoutError as error:
            self._log_error(f'Syncio Timeout accessing: "{url}"  error: {error}')
            raise BatterieError(f'Syncio Timeout accessing: "{url}"  error: {error}') from error
        except Exception as error:
            self._log_error(f'Failed Fetching endpoint "{url}"  error: {error}')
            raise BatterieError(f'Failed Fetching endpoint "{url}"  error: {error}') from error

        return None

    # sync for use with run_in_executor in existing event loop
    def _fetch_api_endpoint(self, url: str) -> Dict:
        """Fetch API coroutine."""

        try:
            response = requests.get(
                url,
                headers=self.header, timeout=TIMEOUT
            )
        except requests.ConnectionError as error:
            self._log_error(f'Connection failed to: "{url}"  error: {error}')
            raise BatterieError(f'Connection failed to: "{url}"  error: {error}') from error
        except Exception as error:
            self._log_error(f'Failed Sync fetch "{url}"  error: {error}')
            raise BatterieError(f'Failed Sync fetch "{url}"  error: {error}') from error

        if response.status > 299:
            self._log_error(f'Error fetching endpoint "{url}" status: {response.status}')
            if response.status in [401, 403]:
                raise BatterieAuthError(f'Auth error fetching endpoint "{url}" status: {response.status}')
            else:
                raise BatterieHTTPError(f'HTTP error fetching endpoint "{url}" status: {response.status}')

        return response.json()

    async def async_fetch_configurations(self) -> Awaitable[Dict]:
        """Wait for Fetch Configurations endpoint."""

        now = datetime.datetime.now()
        if self._last_configurations is not None:
            diff = now - self._last_configurations
            if diff.total_seconds() < RATE_LIMIT:
                return self._configurations

        self._last_configurations = now
        return await self._async_fetch_api_endpoint(
            self.configurations_api_endpoint
        )

    def fetch_configurations(self) -> Dict:
        """Fetch Configurations endpoint."""

        now = datetime.datetime.now()
        if self._last_configurations is not None:
            diff = now - self._last_configurations
            if diff.total_seconds() < RATE_LIMIT:
                return self._configurations

        self._configurations = None
        self._last_configurations = now
        return self._fetch_api_endpoint(
            self.configurations_api_endpoint
        )

    async def async_fetch_latest_details(self) -> Awaitable[Dict]:
        """Wait for Fetch Latest_Details endpoint."""
        return await self._async_fetch_api_endpoint(
                self.latest_details_api_endpoint
        )

    def fetch_latest_details(self) -> Dict:
        """Fetch Latest_Details endpoint."""
        return self._fetch_api_endpoint(
                self.latest_details_api_endpoint
        )

    async def async_fetch_status(self) -> Awaitable[Dict]:
        """Wait for Fetch Status endpoint."""
        return await self._async_fetch_api_endpoint(
            self.status_api_endpoint
        )

    def fetch_status(self) -> Dict:
        """Fetch Status endpoint."""
        return self._fetch_api_endpoint(
            self.status_api_endpoint
        )

    async def async_fetch_battery_status(self) -> Awaitable[Dict]:
        """Wait for Fetch Battery endpoint."""
        return await self._async_fetch_api_endpoint(
            self.battery_api_endpoint
        )

    def fetch_battery_status(self) -> Dict:
        """Fetch Battery endpoint."""
        return self._fetch_api_endpoint(
            self.battery_api_endpoint
        )

    async def async_fetch_powermeter(self) -> Awaitable[Dict]:
        """Wait for Powermeter Status endpoint."""
        return await self._async_fetch_api_endpoint(
            self.powermeter_api_endpoint
        )

    def fetch_powermeter(self) -> Dict:
        """Fetch Powermeter endpoint."""
        return self._fetch_api_endpoint(
            self.powermeter_api_endpoint
        )

    async def async_fetch_inverter(self) -> Awaitable[Dict]:
        """Wait for Fetch Inverter endpoint."""
        return await self._async_fetch_api_endpoint(
            self.inverter_api_endpoint
        )

    def fetch_inverter(self) -> Dict:
        """Fetch Inverter endpoint."""
        return self._fetch_api_endpoint(
            self.inverter_api_endpoint
        )

    @property
    def api_token(self) -> Dict:
        """API token to authenticate with batterie."""
        return self.auth_token

    @property
    def hostname(self) -> Dict:
        """Hostname:port of the batterie."""
        return self._hostname

    @property
    def configurations(self) -> Dict:
        """latest Configurations fetched from batterie."""
        return self._configurations

    @property
    def last_configurations(self) -> Optional[datetime.datetime]:
        """Last time configurations fetched (token validated) from batterie."""
        return self._last_configurations

    # @last_configurations.setter
    # def last_configurations(self, last_configurations: datetime.datetime = None):
    #     """Last time configurations fetched (token validated) from batterie."""
    #     self._last_configurations = last_configurations

    @property
    def last_get_updated(self) -> Optional[datetime.datetime]:
        """Last time emulated method sync fetched from batterie."""
        return self._last_get_updated

    @property
    def last_updated(self) -> Optional[datetime.datetime]:
        """Last time data successfully fetched from batterie."""
        return self._last_updated

    # @last_updated.setter
    # def last_updated(self, last_updated: datetime.datetime = None):
    #     """Last time data fetched from batterie."""
    #     self._last_updated = last_updated

    @property
    @get_item(float)
    def kwh_consumed(self) -> float:
        """Consumed kWh"""
        return self._powermeter_data[1][POWERMETER_KWH_CONSUMED]

    @property
    @get_item(float)
    def kwh_produced(self) -> float:
        """Produced kWh"""
        return self._powermeter_data[0][POWERMETER_KWH_CONSUMED]

    @property
    @get_item(float)
    def production_total_w(self) -> float:
        """Produced W"""
        return self._powermeter_data[0][POWERMETER_WATTS_TOTAL]

    @property
    @get_item(float)
    def production_reactive_power(self) -> float:
        """Reactive Produced W"""
        return self._powermeter_data[0][POWERMETER_REACTIVE_POWER]

    @property
    @get_item(float)
    def production_power_factor(self) -> float:
        """Production Power Factor
        Apparent Power = Real Power + Reactive Power
        Power Factor = Real Power / Apparent Power
        """
        apparent_power = self.production_total_w + self.production_reactive_power
        return self.production_total_w / apparent_power if apparent_power > 0 else 0

    @property
    @get_item(float)
    def consumption_total_w(self) -> float:
        """Consumed W"""
        return self._powermeter_data[1][POWERMETER_WATTS_TOTAL]

    @property
    @get_item(float)
    def consumption_reactive_power(self) -> float:
        """Reactive Consumed W"""
        return self._powermeter_data[1][POWERMETER_REACTIVE_POWER]

    @property
    @get_item(float)
    def consumption_power_factor(self) -> float:
        """Consumption Power Factor
        Apparent Power = Real Power + Reactive Power
        Power Factor = Real Power / Apparent Power
        """
        apparent_power = self.consumption_total_w + self.consumption_reactive_power
        return self.consumption_total_w / apparent_power if apparent_power > 0 else 0

    @property
    @get_item(int)
    def consumption(self) -> int:
        """Consumption of the household
            Returns:
                house consumption in Watt
        """
        return self._latest_details_data[STATUS_CONSUMPTION_W]

    @property
    @get_item(int)
    def production(self) -> int:
        """Power production of PV
            Returns:
                PV production in Watts
        """
        return self._latest_details_data[STATUS_PRODUCTION_W]

    @property
    @get_item(int)
    def seconds_since_full(self) -> int:
        """Seconds passed since full charge
            Returns:
                seconds as integer
        """
        return self._latest_details_data[IC_STATUS][DETAIL_SECONDS_SINCE_FULLCHARGE]

    @property
    @get_item(int)
    def installed_modules(self) -> int:
        """Battery modules installed in the system
            Returns:
                Number of modules
        """
        return self._latest_details_data[IC_STATUS][STATUS_MODULES_INSTALLED]

    @property
    @get_item(int)
    def u_soc(self) -> int:
        """Useable state of charge
            Returns:
                Integer Percent
        """
        return self._latest_details_data[DETAIL_USOC]

    @property
    @get_item(int)
    def r_soc(self) -> int:
        """Relative state of charge (actual charge)
            Returns:
                Integer Percent
        """
        return self._latest_details_data[DETAIL_RSOC]

    @property
    @get_item(int)
    def full_charge_capacity(self) -> int:
        """Full charge capacity of the battery
            Returns:
                Capacity in Wh
        """
        return self._latest_details_data[DETAIL_FULL_CHARGE_CAPACITY]

    @property
    def time_since_full(self) -> datetime.timedelta:
        """Calculates time since full charge.
           Returns:
               Time in format days hours minutes seconds
        """
        return datetime.timedelta(seconds=self.seconds_since_full)

    @property
    def last_time_full(self) -> datetime.datetime:
        """Calculates last time at full charge.
           Returns:
               DateTime
        """
        return datetime.datetime.now() - self.time_since_full

    @property
    @get_item(bool)
    def using_reserve(self) -> bool:
        """Is backup reserve being used
            Returns:
                Bool - true when reserve in use
        """
        return self.capacity_until_reserve < 0

    @property
    @get_item(float)
    def capacity_until_reserve(self) -> float:
        """Capacity until reserve is reached (battery goes standby)
            Returns:
                Wh
        """
        return self.battery_remaining_capacity_wh - self.backup_buffer_capacity_wh

    @property
    def backup_reserve_at(self) -> Optional[datetime.datetime]:
        """Time battery charged/discharged to backup reserve
            Returns:
                Datetime charged/discharged to reserve or None when not charging/discharging
        """
        seconds = self.seconds_until_reserve
        if seconds is None:
            return None

        if seconds < 0:
            return (datetime.datetime.now() - datetime.timedelta(seconds=abs(seconds))) if self.discharging else None
        else:
            return (datetime.datetime.now() + datetime.timedelta(seconds=seconds)) if self.discharging else None

    @property
    def state_core_control_module(self) -> str:
        """State of control module: config, ongrid, offgrid, critical error, ...
            Returns:
                String
        """
        return self._latest_details_data[IC_STATUS][DETAIL_STATE_CORECONTROL_MODULE]

    @property
    @get_item(int)
    def pac_total(self) -> int:
        """ Battery inverter load
            Negative is charging
            Positive is discharging
            Returns:
                Inverter load in watt
        """
        return self._latest_details_data[DETAIL_PAC_TOTAL_W]

    @property
    @get_item(int)
    def charging(self) -> int:
        """Actual battery charging value is negative
            Returns:
                Charging value in watt
        """
        return abs(self.pac_total) if self.pac_total < 0 else 0

    @property
    @get_item(int)
    def discharging(self) -> int:
        """Actual battery discharging value
            Returns:
                Discharging value in watt
        """
        return self.pac_total if self.pac_total > 0 else 0

    @property
    def validation_timestamp(self) -> datetime.datetime:
        """Timestamp: "Wed Sep 18 12:26:06 2024"
            Returns:
                datetime
        """
        return  datetime.datetime.strptime(self._latest_details_data[IC_STATUS]["timestamp"], '%a %b %d %H:%M:%S %Y')

    @property
    @get_item(int)
    def battery_cycle_count(self) -> int:
        """Number of charge/discharge cycles
            Returns:
                Int count
        """
        return self._battery_status[BATTERY_CYCLE_COUNT]

    @property
    @get_item(int)
    def battery_dod_limit(self) -> int:
        """Dept Of Discharge limit
            Returns:
                Int percent
        """
        return (1 - BATTERY_UNUSABLE_RESERVE) * 100

    @property
    @get_item(float)
    def battery_max_cell_temp(self) -> float:
        """Max cell temperature
            Returns:
                Maximum cell temperature in ºC
        """
        return self._battery_status[BATTERY_MAX_CELL_TEMP]

    @property
    @get_item(float)
    def battery_max_cell_voltage(self) -> float:
        """Max cell voltage
            Returns:
                Maximum cell voltage in Volt
        """
        return self._battery_status[BATTERY_MAX_CELL_VOLTAGE]

    @property
    @get_item(float)
    def battery_max_module_current(self) -> float:
        """Max module DC current
            Returns:
                Maximum module DC current in Ampere
        """
        return self._battery_status[BATTERY_MAX_MODULE_CURRENT]

    @property
    @get_item(float)
    def battery_max_module_voltage(self) -> float:
        """Max module DC voltage
            Returns:
                Maximum module DC voltage in Volt
        """
        return self._battery_status[BATTERY_MAX_MODULE_VOLTAGE]

    @property
    @get_item(float)
    def battery_max_module_temp(self) -> float:
        """Max module DC temperature
            Returns:
                Maximum module DC temperature in ºC
        """
        return self._battery_status[BATTERY_MAX_MODULE_TEMP]

    @property
    @get_item(float)
    def battery_min_cell_temp(self) -> float:
        """Min cell temperature
            Returns:
                Minimum cell temperature in ºC
        """
        return self._battery_status[BATTERY_MIN_CELL_TEMP]

    @property
    @get_item(float)
    def battery_min_cell_voltage(self) -> float:
        """Min cell voltage
            Returns:
                Minimum cell voltage in Volt
        """
        return self._battery_status[BATTERY_MIN_CELL_VOLTAGE]

    @property
    @get_item(float)
    def battery_min_module_current(self) -> float:
        """Min module DC current
            Returns:
                Minimum module DC current in Ampere
        """
        return self._battery_status[BATTERY_MIN_MODULE_CURRENT]

    @property
    @get_item(float)
    def battery_min_module_voltage(self) -> float:
        """Min module DC voltage
            Returns:
                Minimum module DC voltage in Volt
        """
        return self._battery_status[BATTERY_MIN_MODULE_VOLTAGE]

    @property
    @get_item(float)
    def battery_min_module_temp(self) -> float:
        """Min module DC temperature
            Returns:
                Minimum module DC temperature in ºC
        """
        return self._battery_status[BATTERY_MIN_MODULE_TEMP]

    @property
    @get_item(float)
    def battery_rsoc(self) -> float:
        """Relative state of charge
            Returns:
                Relative state of charge in %
        """
        return self._battery_status[BATTERY_RSOC]

    @property
    @get_item(float)
    def battery_full_charge_capacity(self) -> float:
        """Fullcharge capacity
            Returns:
                Fullcharge capacity in Ah
        """
        return self._battery_status[BATTERY_FULL_CHARGE_CAPACITY_AH]

    @property
    @get_item(float)
    def battery_full_charge_capacity_wh(self) -> float:
        """Full charge capacity
            Returns:
                Fullcharge capacity in Wh
        """
        return self._battery_status[BATTERY_FULL_CHARGE_CAPACITY_WH]

    @property
    @get_item(float)
    def battery_unusable_capacity_wh(self) -> float:
        """Unusable capacity Wh calculated from Ah
            Returns:
                float Wh
        """
        return self.battery_full_charge_capacity_wh * BATTERY_UNUSABLE_RESERVE

    @property
    @get_item(float)
    def battery_remaining_capacity(self) -> float:
        """Remaining capacity
            Returns:
                Remaining capacity in Ah
        """
        return self._battery_status[BATTERY_REMAINING_CAPACITY]

    @property
    @get_item(float)
    def battery_remaining_capacity_wh(self) -> float:
        """Remaining capacity Wh calculated from Ah
            use instead of status RemainingCapacity_Wh which is incorrect
            Returns:
                Wh
        """
        return self.battery_remaining_capacity * self.battery_module_dc_voltage

    @property
    @get_item(float)
    def battery_module_dc_voltage(self) -> float:
        """Battery module voltage
            value is consistent with Ah & Wh values reported

            Returns:
                Voltage in Volt
        """
        return self._battery_status[BATTERY_NOMINAL_MODULE_VOLTAGE]

    @property
    @get_item(float)
    def battery_system_dc_voltage(self) -> float:
        """System battery voltage
            seems to be module voltage * num modules
            Returns:
                Voltage in Volt
        """
        return self._battery_status[BATTERY_SYSTEM_VOLTAGE]

    @property
    @get_item(float)
    def battery_usable_remaining_capacity(self) -> float:
        """Usable Remaining capacity
            Returns:
                Usable Remaining capacity in Ah
        """
        return self._battery_status[BATTERY_USABLE_REMAINING_CAPACITY]

    @property
    @get_item(float)
    def battery_usable_remaining_capacity_wh(self) -> float:
        """Usable Remaining capacity
            Returns:
                Usable Remaining capacity in Wh
        """
        return self.battery_usable_remaining_capacity * self.battery_module_dc_voltage

    @property
    @get_item(float)
    def battery_system_current(self) -> float:
        """System current
            Returns:
                System current in Ampere
        """
        return self._battery_status[BATTERY_SYSTEM_CURRENT]

    @property
    @get_item(int)
    def seconds_until_fully_charged(self) -> Union[int, None]:
        """Time remaining until fully charged
            Returns:
                Time in seconds - None when not charging, zero when fully charged
        """
        remaining_charge = self.battery_full_charge_capacity_wh - self.battery_remaining_capacity_wh
        seconds = int(remaining_charge / self.charging * 3600) if self.charging else None

        return seconds if remaining_charge != 0 else 0

    @property
    @get_item(int)
    def seconds_until_fully_discharged(self) -> Union[int, None]:
        """Time remaining until fully discharged
            Returns:
                Time in seconds - None when not discharging, zero when fully discharged
        """
        remaining_charge = self.battery_remaining_capacity_wh
        seconds = int(remaining_charge / self.discharging * 3600) if self.discharging else None

        return seconds if remaining_charge != 0 else 0

    @property
    def fully_charged_at(self) -> Optional[datetime.datetime]:
        """ Calculate time until fully charged
            Returns:
                Datetime or None when not charging
        """
        return (datetime.datetime.now() + datetime.timedelta(seconds=self.seconds_until_fully_charged)) if self.charging else None

    @property
    def fully_discharged_at(self) -> Optional[datetime.datetime]:
        """Future time battery is fully discharged
            Returns:
                Datetime discharged or None when not discharging
        """
        return (datetime.datetime.now() + datetime.timedelta(seconds=self.seconds_until_fully_discharged)) if self.discharging else None

    @property
    @get_item(int)
    def seconds_until_reserve(self) -> Union[int, None]:
        """Time until battery capacity at backup reserve
            Above reserve:
                Charging - None
                Discharging - seconds to reserve
            Below Reserve
                Charging - seconds to reserve
                Discharging - None (negative seconds since reserve?)
                Standby - None
            Returns:
                Time in seconds or None
        """
        capacity_until_reserve = self.battery_remaining_capacity_wh - self.backup_buffer_capacity_wh
        if capacity_until_reserve > 0:
            seconds = int((capacity_until_reserve / self.discharging) * 3600) if self.discharging else None
        else:
            if self.charging:
                seconds = int(abs(capacity_until_reserve) / self.charging * 3600)
            else:
                seconds = None # int(capacity_until_reserve / self.discharging * 3600)
        return seconds

    @property
    @get_item(int)
    def configuration_em_operatingmode(self) -> int:
        """Operating Mode
            Returns:
                Integer code
        """
        return self._configurations[CONFIGURATION_EM_OPERATINGMODE]

    @property
    def configuration_em_operatingmode_name(self) -> str:
        """Operating Mode code translated
            Returns:
                string
        """
        _EM_OPERATINGMODE = {
            "1": 'Manual',
            "2": 'Automatic - Self Consumption',
            "6": 'Battery-Module-Extension (30%)',
            "10": 'Time-Of-Use'
        }

        return _EM_OPERATINGMODE[self._configurations[CONFIGURATION_EM_OPERATINGMODE]]

    @property
    def configuration_de_software(self) -> str:
        """Software version
            Returns:
                String
        """
        return self._configurations[CONFIGURATION_DE_SOFTWARE]

    @property
    @get_item(int)
    def installed_capacity(self) -> int:
        """Battery modules installed in the system
            Returns:
                total installed capacity Wh
        """
        return self._configurations[CONFIGURATION_MODULECAPACITY] * self.installed_modules

    @property
    @get_item(int)
    def configuration_em_usoc(self) -> int:
        """User State Of Charge - BackupBuffer value (includes unusable reserve)
            Returns:
                Integer Percent
        """
        return self._configurations[CONFIGURATION_EM_USOC]

    @property
    @get_item(int)
    def consumption_average(self) -> int:
        """Average consumption in watt
           Returns:
               average consumption in watt
        """
        return self._status_data[STATUS_CONSUMPTION_AVG]

    @property
    def system_status(self) -> str:
        """System Status: Config, OnGrid, OffGrid, Critical Error, ...
            Returns:
                String
        """
        return self._status_data[STATUS_SYSTEMSTATUS]

    @property
    def system_status_timestamp(self) -> datetime.datetime:
        """Timestamp: "2024-11-20 14:00:07"
            Can be used to check device time is correct.
            Returns:
                datetime
        """
        return  datetime.datetime.fromisoformat(self._status_data[STATUS_TIMESTAMP])

    @property
    @get_item(float)
    def status_frequency(self) -> float:
        """AC Frequency
           Returns:
              Hz
        """
        return self._status_data[STATUS_FREQUENCY]

    @property
    @get_item(int)
    def status_rsoc(self) -> int:
        """Relative state of charge
            Returns:
                state of charge%
        """
        return self._status_data[STATUS_RSOC]

    @property
    @get_item(int)
    def status_usoc(self) -> int:
        """Usable state of charge
            Returns:
                state of charge%
        """
        return self._status_data[STATUS_USOC]

    @property
    @get_item(int)
    def remaining_capacity_wh(self) -> int:
        """ Remaining capacity in watt-hours
        IMPORTANT NOTE: Why is this double as high as it should be???
            use battery_remaining_capacity_wh for calculated value
            Returns:
                Remaining USABLE capacity of the battery in Wh
        """
        return self._status_data[STATUS_REMAININGCAPACITY_WH]

    @property
    @get_item(int)
    def grid_in(self) -> int:
        """Actual grid feed in value
            Returns:
                Value in watt
        """
        return self._status_data[STATUS_GRIDFEEDIN_W] if self._status_data[STATUS_GRIDFEEDIN_W] > 0 else 0

    @property
    @get_item(int)
    def grid_out(self) -> int:
        """Actual grid out value
            Returns:
                Value in watt
        """
        return abs(self._status_data[STATUS_GRIDFEEDIN_W]) if self._status_data[STATUS_GRIDFEEDIN_W] < 0 else 0

    @property
    @get_item(int)
    def status_backup_buffer(self) -> int:
        """BackupBuffer proportion reserved for OffGrid use
            Returns:
                Percent of capacity
        """
        return self._status_data[STATUS_BACKUPBUFFER]

    @property
    @get_item(bool)
    def status_battery_charging(self) -> bool:
        """BatteryCharging
            Returns:
                true when charging
        """
        return self._status_data[STATUS_BATTERY_CHARGING]

    @property
    @get_item(bool)
    def status_battery_discharging(self) -> bool:
        """BatteryDischarging
            Returns:
                true when discharging
        """
        return self._status_data[STATUS_BATTERY_DISCHARGING]

    @property
    @get_item(dict)
    def status_flows(self) -> dict:
        """Status flows: production -> grid , battery
            Returns:
                dict of name:bool
        """
        flows = {
            "FlowConsumptionBattery":self._status_data[STATUS_FLOW_CONSUMPTION_BATTERY],
            "FlowConsumptionGrid":self._status_data[STATUS_FLOW_CONSUMPTION_GRID],
            "FlowConsumptionProduction":self._status_data[STATUS_FLOW_CONSUMPTION_PRODUCTION],
            "FlowGridBattery":self._status_data[STATUS_FLOW_CONSUMPTION_BATTERY],
            "FlowProductionBattery":self._status_data[STATUS_FLOW_PRODUCTION_BATTERY],
            "FlowProductionGrid":self._status_data[STATUS_FLOW_PRODUCTION_GRID],
        }
        return flows

    @property
    @get_item(int)
    def status_grid_feed_in(self) -> int:
        """GridFeedIn_W
            Returns:
                Feed watts, -ve is export (actually float with zero decimal part)
        """
        return int(self._status_data[STATUS_GRIDFEEDIN_W])

    @property
    @get_item(bool)
    def status_discharge_not_allowed(self) -> bool:
        """dischargeNotAllowed - Surplus Fullchage feature in progress
            Returns:
                Bool
        """
        return self._status_data[STATUS_DISCHARGE_NOT_ALLOWED]

    @property
    @get_item(float)
    def backup_buffer_capacity_wh(self) -> float:
        """Backup Buffer capacity (includes 7% unusable)
            Returns:
                Backup Buffer in Wh
        """
        buffer_percent = self.status_backup_buffer / 100 #self.configuration_em_usoc
        full_charge = self.battery_full_charge_capacity_wh

        return full_charge * buffer_percent

    @property
    @get_item(float)
    def backup_buffer_usable_capacity_wh(self) -> float:
        """Backup Buffer usable capacity (excludes BATTERY_UNUSABLE_RESERVE)
            Returns:
                Usable Backup Buffer in Wh
        """
        buffer_percent = self.status_backup_buffer / 100 #configuration_em_usoc

        return self.battery_full_charge_capacity_wh * (buffer_percent - BATTERY_UNUSABLE_RESERVE) if buffer_percent > BATTERY_UNUSABLE_RESERVE else 0

    @property
    def battery_activity_state(self) -> str:
        """Battery current state of activity"""

        if self.configurations is None:
            return "unavailable"

        """ current_state index of: ["standby", "charging", "discharging", "discharging reserve", "charged", "discharged"] """
        if self.status_battery_charging:
            battery_status = "charging"
        elif self.status_battery_discharging:
            if self.battery_remaining_capacity_wh > self.backup_buffer_capacity_wh:
                battery_status = "discharging"
            else:
                battery_status = "discharging reserve"
        elif self.battery_rsoc > 98: # look at usable capacity over long term?
            battery_status = "charged"
        elif self.battery_usable_remaining_capacity < 2:
            battery_status = "discharged"
        else:
            battery_status = "standby"

        return battery_status

    @property
    @get_item(float)
    def inverter_pac_total(self) -> float:
        """Inverter PAC total"
            Returns:
                Watts
        """
        return  self._inverter_data[INVERTER_PAC_TOTAL]

    @property
    def ic_eclipse_led(self) -> str:
        """System-Status:
                "Eclipse Led":{
                    "Blinking Red":false,
                    "Brightness":100,
                    "Pulsing Green":false,
                    "Pulsing Orange":false,
                    "Pulsing White":true,
                    "Solid Red":false
                }
            Returns:
                JSON String
        """
        return self._latest_details_data[IC_STATUS][IC_ECLIPSE_LED]
