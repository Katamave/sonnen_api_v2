"""Fixture to load batterie discharging below reserve responses
    using all async methods called from async methods
"""
import logging
import pytest
from freezegun import freeze_time
from asyncmock import AsyncMock

from sonnen_api_v2 import Batterie

from . mock_sonnenbatterie_v2_charging import __mock_configurations, __mock_powermeter
from . mock_sonnenbatterie_v2_discharging_reserve import __mock_status_discharging, __mock_latest_discharging, __mock_battery_discharging, __mock_inverter_discharging


LOGGER_NAME = "sonnenapiv2"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@pytest.fixture(name="battery_discharging_reserve")
@freeze_time("20-11-2023 17:00:59") # disharging reserve time
async def fixture_battery_discharging_reserve(mocker) -> Batterie:
    if LOGGER_NAME is not None:
        logging.basicConfig(filename=(f'/tests/logs/{LOGGER_NAME}.log'), level=logging.DEBUG)
        logger = logging.getLogger(LOGGER_NAME)
        logger.info('Sonnen mock data battery_discharging_reserve_async test.')

    mocker.patch.object(Batterie, "async_fetch_configurations", AsyncMock(return_value=__mock_configurations()))
    mocker.patch.object(Batterie, "async_fetch_status", AsyncMock(return_value=__mock_status_discharging()))
    mocker.patch.object(Batterie, "async_fetch_latest_details", AsyncMock(return_value=__mock_latest_discharging()))
    mocker.patch.object(Batterie, "async_fetch_battery_status", AsyncMock(return_value=__mock_battery_discharging()))
    mocker.patch.object(Batterie, "async_fetch_powermeter", AsyncMock(return_value=__mock_powermeter()))
    mocker.patch.object(Batterie, "async_fetch_inverter", AsyncMock(return_value=__mock_inverter_discharging()))

    battery_discharging_reserve = Batterie('fakeToken', 'fakeHost')

    success = await battery_discharging_reserve.async_update()
    assert success is not False

    return battery_discharging_reserve
