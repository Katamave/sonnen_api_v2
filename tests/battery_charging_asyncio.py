import os
import logging
import pytest
from asyncmock import AsyncMock

from sonnen_api_v2 import Batterie
from dotenv import load_dotenv

from . mock_sonnenbatterie_v2_charging import __mock_status_charging, __mock_latest_charging, __mock_configurations, __mock_battery, __mock_powermeter, __mock_inverter

load_dotenv()

BATTERIE_1_HOST = os.getenv('BATTERIE_1_HOST','X')
API_READ_TOKEN_1 = os.getenv('API_READ_TOKEN_1')
BATTERIE_HOST_PORT = os.getenv('BATTERIE_HOST_PORT')

LOGGER_NAME = "sonnenapiv2"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if BATTERIE_1_HOST == 'X':
    raise ValueError('Set BATTERIE_1_HOST & API_READ_TOKEN_1 in .env See env.example')

@pytest.fixture(name="battery_charging")
async def fixture_battery_charging(mocker) -> Batterie:
    if LOGGER_NAME is not None:
        logging.basicConfig(filename=(f'/tests/logs/{LOGGER_NAME}.log'), level=logging.DEBUG)
        logger = logging.getLogger(LOGGER_NAME)
        logger.info('Sonnen mock data battery_charging_asyncio test.')

    mocker.patch.object(Batterie, "async_fetch_status", AsyncMock(return_value=__mock_status_charging()))
    mocker.patch.object(Batterie, "async_fetch_latest_details", AsyncMock(return_value=__mock_latest_charging()))
    mocker.patch.object(Batterie, "async_fetch_configurations", AsyncMock(return_value=__mock_configurations()))
    mocker.patch.object(Batterie, "async_fetch_battery_status", AsyncMock(return_value=__mock_battery()))
    mocker.patch.object(Batterie, "async_fetch_powermeter", AsyncMock(return_value=__mock_powermeter()))
    mocker.patch.object(Batterie, "async_fetch_inverter_data", AsyncMock(return_value=__mock_inverter()))

    battery_charging = Batterie(API_READ_TOKEN_1, BATTERIE_1_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)  # Working and charging
    success = await battery_charging.async_update()
    assert success is True

    return battery_charging
