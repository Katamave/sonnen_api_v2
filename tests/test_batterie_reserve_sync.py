"""pytest tests/test_batterie_reserve_sync.py -s -v -x
3. Sync update called from sync method
"""
#import datetime
import logging
import pytest
from freezegun import freeze_time
import responses
from sonnen_api_v2 import Batterie, BatterieError

from .battery_discharging_reserve_sync import fixture_battery_discharging_reserve

LOGGER_NAME = "sonnenapiv2"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@responses.activate
@pytest.mark.usefixtures("battery_discharging_reserve")
@freeze_time("20-11-2023 17:00:59")
def test_sync_methods(battery_discharging_reserve: Batterie) -> None:
    if LOGGER_NAME is not None:
        logging.basicConfig(filename=(f'/tests/logs/{LOGGER_NAME}.log'), level=logging.DEBUG)
        logger = logging.getLogger(LOGGER_NAME)
        logger.info('Sonnen mock data sync test suite.')

    assert battery_discharging_reserve.discharging > 0
    assert battery_discharging_reserve.charging == 0
    assert battery_discharging_reserve.fully_discharged_at.strftime('%d.%b.%Y %H:%M') == '20.Nov.2023 18:27'

    # sync wrapped methods used by ha component
    status_data = battery_discharging_reserve.sync_get_status()
    latest_data = battery_discharging_reserve.sync_get_latest_data()
    #print(f'status: {status_data}')
    assert status_data.get('Timestamp') == latest_data.get('Timestamp')
    assert status_data.get('GridFeedIn_W') == latest_data.get('GridFeedIn_W')
    assert status_data.get('Consumption_W') == latest_data.get('Consumption_W')
    assert status_data.get('Production_W') == latest_data.get('Production_W')
    assert status_data.get('Pac_total_W') == latest_data.get('Pac_total_W')

    assert status_data.get('Timestamp') == '2023-11-20 17:00:59'
    assert status_data.get('GridFeedIn_W') == 0
    assert status_data.get('Consumption_W') == 1563
    assert status_data.get('Production_W') == 125
    assert status_data.get('Pac_total_W') == 1438


    powermeter = battery_discharging_reserve.sync_get_powermeter()
    assert powermeter[0]['direction'] == 'production'
    assert powermeter[1]['direction'] == 'consumption'

    battery_status =  battery_discharging_reserve.sync_get_battery()
    assert battery_status.get('cyclecount') == 30
    assert battery_status.get('remainingcapacity') == 36.3564
    assert battery_status.get('usableremainingcapacity') == 22.2178

    inverter_data = battery_discharging_reserve.sync_get_inverter()
    assert  int(inverter_data.get('pac_total')) == status_data.get('Pac_total_W')
    assert inverter_data.get('pac_total') == 1438.67
    assert inverter_data.get('uac') == 233.55

    configurations = battery_discharging_reserve.sync_get_configurations()
    assert configurations.get('DE_Software') == '1.14.5'
    assert configurations.get('EM_USOC') == 20

    assert battery_discharging_reserve.battery_rsoc == 18.0
    assert battery_discharging_reserve.battery_usoc == 11.0

    from .check_results import check_reserve_results

    check_reserve_results(battery_discharging_reserve)
