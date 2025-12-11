"""pytest tests/test_batterie_charge_sync.py -s -v -x
    3. Sync update called from sync method

    Fixture for charging tests has extra attributes in 'Eclipse Led'
    to test extra attributes in firmware 1.25.6 update decemeber 2025.
    This has been refactored to prevent crashes with such firmware updates in the past.
"""

import datetime
import logging
import pytest
from freezegun import freeze_time
from freezegun.api import FakeDatetime
import tzlocal
import responses

#from sonnen_api_v2.sonnen import Sonnen as Batterie, BatterieError
from sonnen_api_v2 import Batterie, BatterieError

from .battery_charging_sync import fixture_battery_charging

LOGGER_NAME = "sonnenapiv2"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@responses.activate
@pytest.mark.usefixtures("battery_charging")
@freeze_time("20-11-2023 17:00:00.54321")
def test_sync_methods(battery_charging: Batterie) -> None:
    if LOGGER_NAME is not None:
        logging.basicConfig(filename=(f'/tests/logs/{LOGGER_NAME}.log'), level=logging.DEBUG)
        logger = logging.getLogger(LOGGER_NAME)
        logger.info('Sonnen mock data sync test suite.')


    status = battery_charging.sync_get_update() # data already cached by fixture (testing cache)
    assert status is True

    assert battery_charging.led_state == "Pulsing White 100%"
    assert battery_charging.led_state_text == "Normal Operation."
    assert battery_charging.led_status == "0x01 - ONGRID_READY"

    assert battery_charging.charging > 0
    assert battery_charging.discharging == 0

    assert battery_charging.last_configurations == FakeDatetime(2023, 11, 20, 17, 0, 0, 543210, tzlocal.get_localzone()) #'20-11-2023 17:00:00.54321+10:00'
    assert battery_charging.last_updated ==  FakeDatetime(2023, 11, 20, 17, 0, 0, 543210, tzinfo=tzlocal.get_localzone()) #'20-11-2023 17:00:00.54321+10:00'
    assert battery_charging.last_get_updated == FakeDatetime(2023, 11, 20, 17, 0, 0, 543210, tzinfo=tzlocal.get_localzone()) # '20-11-2023 17:00:00.54321+10:00'
    assert battery_charging.microgrid_enabled is False

    # sync wrapped methods used by ha component
    status_data = battery_charging.sync_get_status()
    #print(f'status: {status_data}')
    assert status_data.get('Timestamp') == '2023-11-20 17:00:55'
    assert status_data.get('GridFeedIn_W') == 0
    assert status_data.get('Consumption_W') == 1578
    assert status_data.get('Production_W') == 2972
    assert status_data.get('Pac_total_W') == -1394

    latest_data = battery_charging.sync_get_latest_data()
    assert latest_data.get('Timestamp') == '2023-11-20 17:00:55'
    assert latest_data.get('GridFeedIn_W') == 0
    assert latest_data.get('Consumption_W') == 1578
    assert latest_data.get('Production_W') == 2972
    assert latest_data.get('Pac_total_W') == -1394

    powermeter = battery_charging.sync_get_powermeter()
    assert powermeter[0]['direction'] == 'production'
    assert powermeter[1]['direction'] == 'consumption'

    battery_status =  battery_charging.sync_get_battery()
    assert battery_status.get('cyclecount') == 30
    assert battery_status.get('remainingcapacity') == 177.74

    inverter_data = battery_charging.sync_get_inverter()
    assert  int(inverter_data.get('pac_total')) == status_data.get('Pac_total_W')
    assert inverter_data.get('pac_total') == -1394.33
    assert inverter_data.get('uac') == 233.55

    configurations = battery_charging.sync_get_configurations()
    assert configurations.get('DE_Software') == '1.14.5'
    assert configurations.get('EM_USOC') == 20

    assert configurations.get('EM_RE_ENABLE_MICROGRID') == '1'
    assert configurations.get('EM_USER_INPUT_TIME_ONE') == "08:00"
    assert configurations.get('EM_USER_INPUT_TIME_TWO') == "09:05"
    assert configurations.get('EM_USER_INPUT_TIME_THREE') == "10:10"

    from .check_results import check_charge_results

    check_charge_results(battery_charging)
