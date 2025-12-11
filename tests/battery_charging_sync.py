"""Fixture to load batterie charging responses
    using all sync methods
"""
import logging
import pytest
from freezegun import freeze_time
import responses

from sonnen_api_v2 import Batterie

from . mock_sonnenbatterie_v2_charging import __mock_status_charging, __mock_latest_charging, __mock_configurations, __mock_battery, __mock_powermeter, __mock_inverter

LOGGER_NAME = "sonnenapiv2"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@pytest.fixture(name="battery_charging")
@freeze_time("20-11-2023 17:00:00.54321") # charging time
def fixture_battery_charging(mocker) -> Batterie:
    if LOGGER_NAME is not None:
        logging.basicConfig(filename=(f'/tests/logs/{LOGGER_NAME}.log'), level=logging.DEBUG)
        logger = logging.getLogger(LOGGER_NAME)
        logger.info('Sonnen mock data battery_charging_sync test.')

    battery_charging = Batterie('fakeToken', 'fakeHost')
    urlHost = battery_charging.url

    mocker.patch.object(Batterie, "fetch_status", __mock_status_charging)
    mocker.patch.object(Batterie, "fetch_latest_details", __mock_latest_charging)
#    mocker.patch.object(Batterie, "fetch_configurations", __mock_configurations)
    mocker.patch.object(Batterie, "fetch_battery_status", __mock_battery)
    mocker.patch.object(Batterie, "fetch_powermeter", __mock_powermeter)
    mocker.patch.object(Batterie, "fetch_inverter", __mock_inverter)

    with responses.RequestsMock() as rsps:

        url = urlHost + '/api/v2/configurations'

        rsps.add(
            responses.GET,
            url,
            json=__mock_configurations(),
        )
        success = battery_charging.sync_update()

    assert success is not False

    return battery_charging
