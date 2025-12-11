"""pytest tests/test_batterieresponse.py -s -v -x -k test_batterieresponse_works

1. Async update called from an async method.
"""
import datetime
import os
import sys
import logging
import urllib3
import tzlocal
import aiohttp
from aiohttp import ConnectionTimeoutError

#for tests only
import pytest
from freezegun import freeze_time
from unittest.mock import patch

from sonnen_api_v2 import Batterie, BatterieBackup, BatterieResponse, BatterieAuthError, BatterieHTTPError, BatterieSensorError, BatterieError

from .battery_charging_asyncio import fixture_battery_charging
#from .mock_sonnenbatterie_v2_charging import __mock_configurations
from .mock_battery_responses import (
    __battery_auth200,
    __battery_AuthError_401,
    __battery_HTTPError_301,
)

LOGGER_NAME = None # "sonnenapiv2" #

logging.getLogger("batterieResponse").setLevel(logging.WARNING)

if LOGGER_NAME is not None:
    filename=f'/tests/logs/{LOGGER_NAME}.log'
    logging.basicConfig(filename=filename, level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(LOGGER_NAME)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs debug messages
    fh = logging.FileHandler(filename=filename, mode='a')
    fh.setLevel(logging.DEBUG)
    # console handler display logs messages to console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info ('BatterieResponse for HA mock data tests')


@pytest.mark.asyncio
#@pytest.mark.usefixtures("battery_charging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
@freeze_time("20-11-2023 17:00:00.543210")
async def test_batterieresponse_works(battery_charging: Batterie) -> None:
    """BackupBatterie Response using mock data"""

    _batterie = BatterieBackup('fakeToken', 'fakeHost')

    response = await _batterie.validate_token()

    assert isinstance(response, BatterieResponse) is True
    assert response == BatterieResponse(
        version='0.5.15',
        last_updated=datetime.datetime(2023, 11, 20, 17, 0, 0, 543210, tzinfo=tzlocal.get_localzone()),
        package_build='59',
        sensor_values={}
)

    response:BatterieResponse = await _batterie.refresh_response()

    #print(f'response: {response}')

    assert isinstance(response, BatterieResponse) is True
    assert response == BatterieResponse(
        version='0.5.15',
        last_updated=datetime.datetime(2023, 11, 20, 17, 0, 0, 543210, tzinfo=tzlocal.get_localzone()),
        package_build='59',
        sensor_values={}
        )

    assert response.version == '0.5.15'
    assert _batterie.get_sensor_value('package_version') == response.version
    assert response.package_build == '59'
    assert _batterie.get_sensor_value('package_build') == response.package_build

    assert _batterie.get_sensor_value('configuration_de_software') == '1.14.5'
    assert _batterie.get_sensor_value('led_state') == 'Pulsing White 100%'
    assert _batterie.get_sensor_value('led_state_text') == 'Normal Operation.'
    assert _batterie.get_sensor_value('inverter_uac') == 233.55
    assert _batterie.get_sensor_value('battery_full_charge_capacity_wh') == 20683.49
    assert _batterie.get_sensor_value('full_charge_capacity_wh') == 20187.09
    assert _batterie.get_sensor_value('usable_remaining_capacity_wh') == 16351.5
    assert _batterie.get_sensor_value('used_capacity_wh') == 3835.6 # (20187.1 - 16351.5)
    assert _batterie.get_sensor_value('battery_average_current') == 0.035
    assert _batterie.get_sensor_value('remaining_capacity_wh') == 18201.5
    assert _batterie.get_sensor_value('battery_min_cell_temp') == 18.95
    assert _batterie.get_sensor_value('battery_max_cell_temp') == 19.95
    assert _batterie.get_sensor_value('battery_dod_limit') == 7
    assert _batterie.get_sensor_value('production_total_w') == 609.5
    assert _batterie.get_sensor_value('consumption_total_w') == 59.30
    assert _batterie.get_sensor_value('state_bms') == 'ready'
    assert _batterie.get_sensor_value('state_inverter') == 'running'
    assert _batterie.get_sensor_value('microgrid_enabled') is False
    assert _batterie.get_sensor_value('mg_minimum_soc_reached') is False
    assert _batterie.get_sensor_value('dc_minimum_rsoc_reached') is False


@pytest.mark.asyncio
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
async def test_batterieresponse_bad_sensor(battery_charging: Batterie) -> None:
    """BackupBatterie Response for unknown property name"""

    _batterie = BatterieBackup('fakeToken', 'fakeHost')
    assert _batterie.available is False

    response:BatterieResponse = await _batterie.validate_token()

    assert isinstance(response, BatterieResponse) is True
    assert _batterie.available is True

    assert _batterie.get_sensor_value('configuration_de_software') == '1.14.5'

    response:BatterieResponse = await _batterie.refresh_response()

#    print(f'resp: {vars(response)}')

    assert isinstance(response, BatterieResponse) is True
    assert _batterie.available is True

    with pytest.raises(BatterieSensorError, match="BatterieBackup: Device has no sensor called 'bad_sensor_name'"):
        _batterie.get_sensor_value('bad_sensor_name')



async def __mock_async_validate_token(self):
    """Mock validation failed."""
    return False

@pytest.mark.asyncio
@patch.object(Batterie, 'async_validate_token', __mock_async_validate_token)
async def test_batterieresponse_AuthError(battery_charging: Batterie) -> None:
    """BackupBatterie Response using mock coroutine"""

    _batterie = BatterieBackup('fakeToken', 'fakeHost')

    with pytest.raises(BatterieAuthError, match='BatterieBackup: Error validating API token!'):
        await _batterie.validate_token()


async def __mock_async_update(self):
    """Mock update failed."""
    return False

def __mock_sync_update(self):
    """Mock update failed."""
    return False

@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_charging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
@patch.object(Batterie, 'async_update', __mock_async_update)
@freeze_time("20-11-2023 17:00:00.543210")
async def test_batterieresponse_BatterieError(battery_charging: Batterie) -> None:
    """BackupBatterie Response using mock data"""

    _batterie = BatterieBackup('fakeToken', 'fakeHost')

    response = await _batterie.validate_token()

    assert isinstance(response, BatterieResponse) is True
    assert response == BatterieResponse(
        version='0.5.15',
        last_updated=datetime.datetime(2023, 11, 20, 17, 0, 0, 543210, tzinfo=tzlocal.get_localzone()),
        sensor_values={},
        package_build='59'
    )

    with pytest.raises(BatterieError, match='BatterieBackup: Error updating batterie data!'):
        response = await _batterie.refresh_response()


@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_charging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_AuthError_401)
async def test_batterie_AuthError401(battery_charging: Batterie) -> None:
    """Batterie 401 Response using mock data"""

    _batterie = Batterie('fakeToken', 'fakeHost')

    with pytest.raises(BatterieAuthError, match='Invalid token "fakeToken" status: 401'):
        await _batterie.async_validate_token()


@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_charging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_HTTPError_301)
async def test_batterie_BatterieHTTPError(battery_charging: Batterie) -> None:
    """Batterie 301 Response using mock data"""

    _batterie = Batterie('fakeToken', 'fakeHost')

    with pytest.raises(BatterieHTTPError, match='HTTP Error fetching endpoint "http://fakeHost:80/api/v2/configurations" status: 301'):
        await _batterie.async_validate_token()

@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_charging")
async def test_batterie_ConnectionError(battery_charging: Batterie) -> None:
    """Batterie connection error"""

    _batterie = BatterieBackup('fakeToken', 'fakeHost')

    with patch(
        "aiohttp.ClientSession.get",
        side_effect=ConnectionTimeoutError,
    ):
#        with pytest.raises(BatterieError, match='Connection timeout to endpoint '):
        await _batterie.refresh_response()

@pytest.mark.usefixtures("battery_charging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_AuthError_401)
@freeze_time("20-11-2023 17:00:00.543210")
def test_batterieresponse_sync_BatterieAuthError(battery_charging: Batterie) -> None:
    """BackupBatterie sync Response using mock data"""

    _batterie = BatterieBackup('fakeToken', 'fakeHost')

#    with pytest.raises(BatterieAuthError, match='Auth error fetching endpoint "http://fakeHost:80/api/v2/configurations" status: 401'):
    with pytest.raises(BatterieAuthError, match='Invalid token "fakeToken" status: 401'):
        success = _batterie.validate_token_sync()
        assert success is False

# @pytest.mark.usefixtures("battery_charging")
# @patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
# #@patch.object(Batterie, 'sync_update', __mock_sync_update)
# @freeze_time("20-11-2023 17:00:00.543210")
# def test_batterieresponse_sync_BatterieHTTPError(battery_charging: Batterie) -> None:
#     """BackupBatterie sync Response using mock data"""

#     _batterie = BatterieBackup('fakeToken', 'fakeHost')

#     response  = _batterie.validate_token_sync()
#     assert isinstance(response, BatterieResponse) is True

    # with patch(
    #     "custom_components.sonnenbackup.config_flow._validate_api",
    #     return_value=True,
    # ):

#     with patch(
#         "urllib3.HTTPConnectionPool.urlopen",
#         new_callable=__battery_HTTPError_301,
#     ):
#         success = _batterie._battery.sync_update()
#         assert success is False

    # with pytest.raises(BatterieHTTPError, match='Auth error fetching endpoint "http://fakeHost:80/api/v2/configurations" status: 401'):
    #     success = _batterie._battery.sync_update()
    #     assert success is False
