"""Sonnen Batterie API V2 module."""

import logging
from collections.abc import Awaitable
from collections import namedtuple
from typing import Any #, Dict, Optional, Union, Tuple

from sonnen_api_v2.sonnen import Sonnen as Batterie, BatterieError, BatterieAuthError, BatterieHTTPError, BatterieSensorError
from .const import DEFAULT_PORT

__version__ = '0.5.15' # HA 2025.8

# A build is each time dev work has passed its tests
# and could be a release candidate.
__build__ = '59'

__all__ = (
    "Batterie",
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
            "package_build",
            "sensor_values"
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
        self._attr_available:bool = False # not availble until token validated
        self._response:BatterieResponse = None

    @property
    def available(self) -> bool:
        """Device availability."""

        return self._attr_available

    @property
    def url(self) -> str:
        """Device url."""

        return self._battery.url

    @property
    def package_version(self) -> str:
        """Package version"""

        return __version__

    @property
    def package_build(self) -> str:
        """Package build"""

        return __build__

    def get_sensor_value(self, sensor_name:str) -> Any:
        """Get sensor value by name from battery property or class property.
            refresh_response must have been called at least once before any sensor value is retrieved.
        """

        try:
            sensor_value = getattr(self._battery, sensor_name)
        except AttributeError:
            try:
                sensor_value = getattr(self, sensor_name)
            except AttributeError as error:
                raise BatterieSensorError(f"BatterieBackup: Device has no sensor called '{sensor_name}'. Update sonnen_api_v2 package.") from error
            except Exception as error:
                _LOGGER.error("Error getting sensor %s from class: %s", sensor_name, repr(error))
                raise BatterieError(f'Error getting sensor {sensor_name} from class: {repr(error)}') from error
        except Exception as error:
            _LOGGER.error("Error getting sensor %s from class: %s", sensor_name, repr(error))
            raise BatterieError(f'Error getting sensor {sensor_name} from battery: {repr(error)}') from error

        return sensor_value

    async def refresh_response(self) -> Awaitable[BatterieResponse]:
        """Query the real time API."""

        success = await self._battery.async_update()

        self._attr_available = success
        if success is False:
            _LOGGER.error("BatterieBackup: Error updating batterie data! from: %s", self._battery.hostname)
            raise BatterieError(f'BatterieBackup: Error updating batterie data! from: {self._battery.hostname}')

        self._response = BatterieResponse(
            version = __version__,
            last_updated = self._battery.last_updated,
            package_build = __build__,
            sensor_values = {},
        )
        return self._response

    async def validate_token(self) -> Awaitable[BatterieResponse]:
        """Query the real time API."""

        success = await self._battery.async_validate_token()

        self._attr_available = success
        if success is not True:
            _LOGGER.error("BatterieBackup: Error validating API token! (%s)", self._battery.api_token)
            raise BatterieAuthError(f'BatterieBackup: Error validating API token! ({self._battery.api_token})')

        self._response = BatterieResponse(
            version = __version__,
            last_updated = self._battery.last_configurations,
            package_build = __build__,
            sensor_values = {},
        )
        return self._response

    def validate_token_sync(self) -> BatterieResponse:
        """Query the real time API."""

        success = self._battery.sync_validate_token()

        self._attr_available = success
        if success is not True:
            _LOGGER.error("BatterieBackup: Error validating API token! (%s)", self._battery.api_token)
            raise BatterieAuthError(f'BatterieBackup: Error validating API token! ({self._battery.api_token})')

        self._response = BatterieResponse(
            version = __version__,
            last_updated = self._battery.last_configurations,
            package_build = __build__,
            sensor_values = {},
        )
        return self._response
