"""Sonnen Batterie API V2 module."""

import logging
from collections.abc import Awaitable
from collections import namedtuple
from typing import Any #, Dict, Optional, Union, Tuple

from sonnen_api_v2.sonnen import Sonnen as Batterie, BatterieError, BatterieAuthError, BatterieHTTPError, BatterieSensorError
from .const import DEFAULT_PORT

__version__ = '0.5.14'

__all__ = (
    "Batterie"
    "BatterieError",
    "BatterieAuthError",
    "BatterieHTTPError",
    "BatterieSensorError",
    "BatterieResponse",
    "BatterieBackup",
)

_LOGGER = logging.getLogger(__name__)

class BatterieResponse(
    namedtuple(
        "BatterieResponse",
        [
            "version",
            "last_updated",
#            "configurations",
            "sensor_values"
#            "status",
#            "latestdata",
#            "battery",
#            "powermeter",
#            "inverter"
        ],
    )
):
    """Sonnen Batterie response for ha component."""


class BatterieBackup:
    """Sonnen Batterie real time API.

        Used by home assistant component sonnenbackup
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, auth_token:str , ip_address:str, port=DEFAULT_PORT) -> None:
        """Initialize the API client."""

        self._battery = Batterie(auth_token, ip_address, port)
        self._attr_available:bool = False

    @property
    def available(self) -> bool:
        """Device availability."""
        return self._attr_available

    @property
    def url(self) -> str:
        """Device url."""
        return self._battery.url

    def get_sensor_value(self, sensor_name:str) -> Any:
        """Get sensor value by name from battery property.
            refresh_response must have been called at least once before any sensor value is retrieved.
        """
        try:
            sensor_value =  getattr(self._battery, sensor_name)
        except AttributeError as error:
            raise BatterieSensorError(f"BatterieBackup: Device has no sensor called '{sensor_name}'. Update sonnen_api_v2 package.") from error

        return sensor_value

    async def refresh_response(self) -> Awaitable[BatterieResponse]:
        """Query the real time API."""

        success = await self._battery.async_update()

        self._attr_available = success
        if success is False:
            _LOGGER.error(f'BatterieBackup: Error updating batterie data! from: {self._battery.hostname}')
            raise BatterieError(f'BatterieBackup: Error updating batterie data! from: {self._battery.hostname}')

        return BatterieResponse(
            version = self._battery.configuration_de_software,
            last_updated = self._battery.last_updated,
            sensor_values = {},
        )

    async def validate_token(self) -> Awaitable[BatterieResponse]:
        """Query the real time API."""

        success = await self._battery.async_validate_token()

        self._attr_available = success
        if success is not True:
            _LOGGER.error(f'BatterieBackup: Error validating API token! ({self._battery.api_token})')
            raise BatterieAuthError(f'BatterieBackup: Error validating API token! ({self._battery.api_token})')

        return BatterieResponse(
            version = self._battery.configuration_de_software,
            last_updated = self._battery.last_configurations,
            sensor_values = {},
        )
