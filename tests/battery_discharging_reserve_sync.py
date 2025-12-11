"""Fixture to load batterie discharging below reserve responses
    using all sync methods
"""
import logging
import pytest
from freezegun import freeze_time
import responses

from sonnen_api_v2 import Batterie

from . mock_sonnenbatterie_v2_charging import __mock_configurations, __mock_powermeter
from . mock_sonnenbatterie_v2_discharging_reserve import __mock_status_discharging, __mock_latest_discharging, __mock_battery_discharging, __mock_inverter_discharging

LOGGER_NAME = "sonnenapiv2"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@pytest.fixture(name="battery_discharging_reserve")
@freeze_time("20-11-2023 17:00:59") # disharging reserve time
def fixture_battery_discharging_reserve(mocker) -> Batterie:
    if LOGGER_NAME is not None:
        logging.basicConfig(filename=(f'/tests/logs/{LOGGER_NAME}.log'), level=logging.DEBUG)
        logger = logging.getLogger(LOGGER_NAME)
        logger.info('Sonnen mock data battery_discharging_reserve_sync test.')

    mocker.patch.object(Batterie, "fetch_status", __mock_status_discharging)
    mocker.patch.object(Batterie, "fetch_latest_details", __mock_latest_discharging)
#    mocker.patch.object(Batterie, "fetch_configurations", __mock_configurations)
    mocker.patch.object(Batterie, "fetch_battery_status", __mock_battery_discharging)
    mocker.patch.object(Batterie, "fetch_powermeter", __mock_powermeter)
    mocker.patch.object(Batterie, "fetch_inverter", __mock_inverter_discharging)

    battery_discharging_reserve = Batterie('fakeToken', 'fakeHost')
    urlHost = battery_discharging_reserve.url

    with responses.RequestsMock() as rsps:

        url = urlHost + '/api/v2/configurations'

        rsps.add(
            responses.GET,
            url,
            json=__mock_configurations(),
        )
        success = battery_discharging_reserve.sync_update()

    assert success is not False

    return battery_discharging_reserve
