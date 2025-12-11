"""Methods to emulate sonnenbatterie (v1) package for sonnenbatterie_v2_api ha component.

home assistant component uses only sync methods called by asyncio.run_in_executor.
"""

from math import ceil
from typing import Dict
import datetime
import aiohttp
import asyncio

from .const import RATE_LIMIT


def set_request_connect_timeouts(self, request_timeouts: tuple[int, int]):
    """set request_timeouts tuple and return them."""

    self.request_timeouts = request_timeouts
    self.client_timeouts = aiohttp.ClientTimeout(
        connect=request_timeouts[0], sock_read=request_timeouts[1]
    )
    return self.request_timeouts


def get_request_connect_timeouts(self) -> tuple[int, int]:
    """return request_timeouts tuple."""

    return self.request_timeouts


def get_update(self) -> bool:
    """Update battery details Asyncronously from a sequential caller using async methods.
        Sync/Async methods named to be compatible with existing HASS integration usage.
    Returns:
        True when all updates successful or
        called again within rate limit interval.
    """

    async def _aync_update(self) -> bool:
        now = datetime.datetime.now()
        if self._last_get_updated is not None:
            diff = now - self._last_get_updated
            if diff.total_seconds() < RATE_LIMIT:
                return True

        self._configurations = await self.async_fetch_configurations()
        success = self._configurations is not None
        if success:
            _aug_configurations(self)
            self._status_data = await self.async_fetch_status()
            success = self._status_data is not None
        if success:
            self._latest_details_data = await self.async_fetch_latest_details()
            success = self._latest_details_data is not None
        if success:
            self._battery_status = await self.async_fetch_battery_status()
            success = self._battery_status is not None
        if success:
            _aug_battery(self)
            self._adjust_current_details()
            self._powermeter_data = await self.async_fetch_powermeter()
            success = self._powermeter_data is not None
        if success:
            self._inverter_data = await self.async_fetch_inverter()
            success = self._inverter_data is not None

        self._last_get_updated = self._last_configurations if success else None
        return success

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    try:
        event_loop.run_until_complete(_aync_update(self))
    finally:
        event_loop.close()
    return self._last_get_updated is not None


def sync_get_update(self) -> bool:
    """Update all battery data from a sequential caller using sync methods
        with extended data needed for ha component.
        Sync/Async methods named to be compatible with existing HASS integration usage.
    Returns:
        True when all updates successful or
        called again within rate limit interval
    """

    #    print ('sync_get_update')
    now = datetime.datetime.now().astimezone()
    if self._last_get_updated is not None:
        diff = now - self._last_get_updated
        if diff.total_seconds() < RATE_LIMIT:
            print(f"cache_get configs: {self._configurations}")
            return True

    self._configurations = self.sync_get_configurations()
    success = self._configurations is not None
    if success:
        self.sync_get_status()
        success = self._status_data is not None
    if success:
        self.sync_get_latest_data()
        success = self._latest_details_data is not None
    if success:
        self.sync_get_battery()
        success = self._battery_status is not None
    if success:
        self._adjust_current_details()
        self.sync_get_powermeter()
        success = self._powermeter_data is not None
    if success:
        self.sync_get_inverter()
        success = self._inverter_data is not None

    self._last_get_updated = self._last_configurations if success else None
    return success


def get_configurations(self) -> Dict:
    """Configuration details for sonnenbatterie wrapper
        for Sync caller with Async fetch.

    Returns:
        json response
    """

    async def _get_configurations(self):
        self._configurations = await self.async_fetch_configurations()

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    try:
        event_loop.run_until_complete(_get_configurations(self))
    finally:
        event_loop.close()

    return _aug_configurations(self)


def sync_get_configurations(self) -> Dict:
    """Configuration details for sonnenbatterie wrapper
        for Sync caller with Sync fetch.

    Returns:
        json response
    """

    #    print ('sync_get_configurations')
    now = datetime.datetime.now().astimezone()
    if self._last_get_updated is not None:
        diff = now - self._last_get_updated
        if diff.total_seconds() < RATE_LIMIT:
            return self._configurations

    self._configurations = self.fetch_configurations()
    return _aug_configurations(self)


def _aug_configurations(self) -> Dict:
    """Augment Configurations for sonnenbatterie wrapper.
        Add DepthOfDischarge percent, as calculated from battery_status
    Returns:
        json response
    """

    if self._configurations is not None:
        self._configurations["DepthOfDischargeLimit"] = self.battery_dod_limit
    return self._configurations


def get_status(self) -> Dict:
    """Status details for sonnenbatterie wrapper
        for Sync caller with Async fetch
    Returns:
        json response
    """

    async def _get_status(self):
        self._status_data = await self.async_fetch_status()

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    try:
        event_loop.run_until_complete(_get_status(self))
    finally:
        event_loop.close()

    return self._status_data


def sync_get_status(self) -> Dict:
    """Status details for sonnenbatterie wrapper
        for Sync caller with Sync fetch
    Returns:
        json response
    """

    now = datetime.datetime.now().astimezone()
    if self._last_get_updated is not None:
        diff = now - self._last_get_updated
        if diff.total_seconds() < RATE_LIMIT:
            return self._status_data

    self._status_data = self.fetch_status()
    return self._status_data


def get_latest_data(self) -> Dict:
    """Latest details for sonnenbatterie wrapper
        for Sync caller with Async fetch
    Returns:
        json response
    """

    async def _get_latest_data(self):
        self._latest_details_data = await self.async_fetch_latest_details()

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    try:
        event_loop.run_until_complete(_get_latest_data(self))
    finally:
        event_loop.close()
    return self._latest_details_data


def sync_get_latest_data(self) -> Dict:
    """Latest details for sonnenbatterie wrapper
        for Sync caller with Sync fetch
    Returns:
        json response
    """

    now = datetime.datetime.now().astimezone()
    if self._last_get_updated is not None:
        diff = now - self._last_get_updated
        if diff.total_seconds() < RATE_LIMIT:
            return self._latest_details_data

    self._latest_details_data = self.fetch_latest_details()
    return self._latest_details_data


def get_battery(self) -> Dict:
    """Battery status for sonnenbatterie wrapper
        Fake V1 API data used by ha sonnenbatterie component
        for Sync caller with Async fetch
    Returns:
        json response
    """

    async def _get_battery(self):
        self._battery_status = await self.async_fetch_battery_status()
        if self._configurations is None:
            self._configurations = await self.async_fetch_configurations()

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    try:
        event_loop.run_until_complete(_get_battery(self))
    finally:
        event_loop.close()

    if self._battery_status is None:
        return None

    return _aug_battery(self)


def sync_get_battery(self) -> Dict:
    """Battery status for sonnenbatterie wrapper
        Fake V1 API data used by ha sonnenbatterie component
        for Sync caller with Sync fetch
    Returns:
        json response
    """

    now = datetime.datetime.now().astimezone()
    if self._last_get_updated is not None:
        diff = now - self._last_get_updated
        if diff.total_seconds() < RATE_LIMIT:
            return self._battery_status

    self._battery_status = self.fetch_battery_status()
    if self._battery_status is None:
        return None

    if self._configurations is None:
        self.sync_get_configurations()

    return _aug_battery(self)


def _aug_battery(self) -> Dict:
    """Augment Battery status for sonnenbatterie wrapper
        Fake V1 API data used by ha sonnenbatterie component
    Returns:
        json response
    """

    if self._configurations is None:
        self._battery_status["total_installed_capacity"] = ceil(
            self.battery_full_charge_capacity_wh
        )
    else:
        self._battery_status["total_installed_capacity"] = int(
            self._configurations.get("IC_BatteryModules")
        ) * int(self._configurations.get("CM_MarketingModuleCapacity"))

    self._battery_status["dod_reserved_capacity"] = self.battery_unusable_capacity_wh
    self._battery_status["remaining_capacity"] = self.battery_remaining_capacity_wh
    self._battery_status["remaining_capacity_usable"] = (
        self.battery_usable_remaining_capacity_wh
    )
    self._battery_status["backup_buffer_capacity"] = self.backup_buffer_capacity_wh
    return self._battery_status


def get_powermeter(self) -> Dict:
    """powermeter details for sonnenbatterie wrapper
        for Sync caller with Async fetch
    Returns:
        json response
    """

    async def _get_powermeter(self):
        self._powermeter_data = await self.async_fetch_powermeter()

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    try:
        event_loop.run_until_complete(_get_powermeter(self))
    finally:
        event_loop.close()

    return self._powermeter_data


def sync_get_powermeter(self) -> Dict:
    """powermeter details for sonnenbatterie wrapper
        for Sync caller with Sync fetch
    Returns:
        json response
    """

    now = datetime.datetime.now().astimezone()
    if self._last_get_updated is not None:
        diff = now - self._last_get_updated
        if diff.total_seconds() < RATE_LIMIT:
            return self._powermeter_data

    self._powermeter_data = self.fetch_powermeter()
    return self._powermeter_data


def get_inverter(self) -> Dict:
    """Inverter details for sonnenbatterie wrapper
        for Sync caller with Async fetch
    Returns:
        json response
    """

    async def _get_inverter(self):
        self._inverter_data = await self.async_fetch_inverter()

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    try:
        event_loop.run_until_complete(_get_inverter(self))
    finally:
        event_loop.close()

    return self._inverter_data


def sync_get_inverter(self) -> Dict:
    """Inverter details for sonnenbatterie wrapper
        for Sync caller with Sync fetch
    Returns:
        json response
    """

    now = datetime.datetime.now().astimezone()
    if self._last_get_updated is not None:
        diff = now - self._last_get_updated
        if diff.total_seconds() < RATE_LIMIT:
            return self._inverter_data

    self._inverter_data = self.fetch_inverter()
    return self._inverter_data
