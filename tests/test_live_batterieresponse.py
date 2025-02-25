"""pytest tests/test_live_batterieresponse.py -s -v -x -k test_batterieresponse_works
1. Async update called from an async method.
"""
import os
import sys
import logging

#for tests only
import pytest

from sonnen_api_v2 import Batterie, BatterieBackup, BatterieResponse, BatterieAuthError, BatterieHTTPError, BatterieError

from dotenv import load_dotenv

load_dotenv()

BATTERIE_HOST = os.getenv('BATTERIE_HOST','X')
BATTERIE_PORT = int(os.getenv('BATTERIE_HOST_PORT', '80'))
API_READ_TOKEN = os.getenv('API_READ_TOKEN')
# SonnenBatterie config parameters to check against
BACKUP_BUFFER_USOC = int(os.getenv('BACKUP_BUFFER_USOC'))
OPERATING_MODE = int(os.getenv('OPERATING_MODE'))
FW_VERSION = os.getenv('FW_VERSION')

LOGGER_NAME = None # "sonnenapiv2" #

logging.getLogger("batterieResponse").setLevel(logging.WARNING)

if BATTERIE_HOST == 'X':
    raise ValueError('Set BATTERIE_HOST & API_READ_TOKEN in .env See env.example')

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
    logger.info ('Live Battery Online!')


@pytest.mark.asyncio
async def test_batterieresponse_works() -> None:
    """BackupBatterie Response using live data"""

    _batterie = BatterieBackup(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_PORT)
    assert _batterie.available is False

    response:BatterieResponse = await _batterie.validate_token()

    assert isinstance(response, BatterieResponse) is True
    assert _batterie.available is True

    assert response.version == FW_VERSION

    sensor_value = _batterie.get_sensor_value('configuration_de_software')
    assert sensor_value == FW_VERSION
    assert sensor_value == response.version

    response:BatterieResponse = await _batterie.refresh_response()

#    print(f'resp: {vars(response)}')

    assert isinstance(response, BatterieResponse) is True
    assert _batterie.available is True

    assert response.version == _batterie.get_sensor_value('configuration_de_software')
    assert OPERATING_MODE == _batterie.get_sensor_value('configuration_em_operatingmode')
    last_time_full = _batterie.get_sensor_value('last_time_full')
#    time_since_full = _batterie.get_sensor_value('time_since_full')
    seconds_since_full = _batterie.get_sensor_value('seconds_since_full')
    print(f'last time full {last_time_full.strftime('%d.%b.%Y %H:%M')}  seconds: {seconds_since_full}')


@pytest.mark.asyncio
async def test_batterieresponse_BatterieAuthError() -> None:
    """Batterie response using live data"""

    _batterie = Batterie('fakeToken', BATTERIE_HOST, BATTERIE_PORT)

    with pytest.raises(BatterieAuthError, match='Invalid token "fakeToken" status: 401'):
        await _batterie.async_validate_token()


@pytest.mark.asyncio
async def test_batterieresponse_AuthError() -> None:
    """BackupBatterie Response using live data"""

    _batterie = BatterieBackup('fakeToken', BATTERIE_HOST, BATTERIE_PORT)

    with pytest.raises(BatterieAuthError, match='Invalid token "fakeToken" status: 401'):
        await _batterie.validate_token()


@pytest.mark.asyncio
async def test_batterieresponse_HTTPError() -> None:
    """Batterie Response using live data"""

    _batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_PORT)

    with pytest.raises(BatterieHTTPError, match='HTTP Error fetching bad endpoint.  status: 301'):
        await _batterie._force_HTTPError()


@pytest.mark.asyncio
async def test_batterieresponse_IPAuthError() -> None:
    """BackupBatterie Response using live data.
        Last test has long timeout waiting for IP that doesn't respond.
    """

    _batterie = BatterieBackup('fakeToken', 'fakeHost')

    with pytest.raises(BatterieAuthError, match='Invalid IP address "http://fakeHost:80/api/v2/configurations'):
        await _batterie.validate_token()

    _batterie = BatterieBackup('fakeToken', '192.168.200.100')

    with pytest.raises(BatterieError, match='Sync fetch "http://192.168.200.100:80/api/v2/configurations"  fail: '):
        await _batterie.validate_token()

# @pytest.mark.asyncio
# async def test_batterieresponse_BatterieError() -> None:
#     """BackupBatterie Response using live data"""

#     _batterie = BatterieBackup('fakeToken', '192.168.200.100')

#     with pytest.raises(BatterieError, match='Invalid IP address "http://192.168.200.100:80/api/v2/configurations'):
#         await _batterie.validate_token()
