"""pytest tests/test_batterie_discharge_offgrid_async.py -s -v -x

    pytest tests --ignore tests/test_batterie_discharge_offgrid_async.py

3. Sync update called from async method
"""
import datetime
import logging
import pytest
from freezegun import freeze_time
from freezegun.api import FakeDatetime
import tzlocal
#import responses
#from aioresponses import aioresponses

from sonnen_api_v2 import Batterie, BatterieError

from .battery_discharging_offgrid_asyncio import fixture_battery_discharging_offgrid

LOGGER_NAME = "sonnenapiv2"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# #@responses.activate
# @pytest.mark.usefixtures("battery_discharging_offgrid")
# @freeze_time("20-11-2023 17:00:59.54321")
# @pytest.mark.asyncio
# #@aioresponses()
# #async def test_async_methods(battery_discharging: Batterie) -> None:
# async def test_async_methods(battery_discharging_offgrid) -> None:
#     if LOGGER_NAME is not None:
#         logging.basicConfig(filename=(f'/tests/logs/{LOGGER_NAME}.log'), level=logging.DEBUG)
#         logger = logging.getLogger(LOGGER_NAME)
#         logger.info('Sonnen mock data OffGrid async test suite.')

#     print(type(battery_discharging_offgrid).__name__)
#     battery_discharging = Batterie('fakeToken', 'fakeHost')

# ### Need to mock aiohttp.client_reqrep.ClientRequest
#     success = await battery_discharging.async_update()

# #    success = battery_discharging_offgrid.get_update() # data already cached by fixture (testing cache)
#     assert success is True

#     assert battery_discharging.led_state == "Pulsing Green 100%"
#     assert battery_discharging.led_state_text == "Off Grid."

    # assert battery_discharging_offgrid.discharging > 0
    # assert battery_discharging_offgrid.charging == 0
    # assert battery_discharging_offgrid.fully_discharged_at.strftime('%d.%b.%Y %H:%M') == '21.Nov.2023 03:28'

    # assert battery_discharging_offgrid.last_configurations == FakeDatetime(2023, 11, 20, 17, 0, 0, 543210, tzlocal.get_localzone()) #'20-11-2023 17:00:00.54321+10:00'
    # assert battery_discharging_offgrid.last_updated ==  FakeDatetime(2023, 11, 20, 17, 0, 0, 543210, tzinfo=tzlocal.get_localzone()) #'20-11-2023 17:00:00.54321+10:00'
    # assert battery_discharging_offgrid.last_get_updated == FakeDatetime(2023, 11, 20, 17, 0, 0, 543210, tzinfo=tzlocal.get_localzone()) # '20-11-2023 17:00:00.54321+10:00'

    # sync wrapped methods used by ha component
    # status_data = battery_discharging_offgrid.sync_get_status()
    # latest_data = battery_discharging_offgrid.sync_get_latest_data()
    #print(f'status: {status_data}')
    # assert status_data.get('Timestamp') == latest_data.get('Timestamp')
    # assert status_data.get('GridFeedIn_W') == latest_data.get('GridFeedIn_W')
    # assert status_data.get('Consumption_W') == latest_data.get('Consumption_W')
    # assert status_data.get('Production_W') == latest_data.get('Production_W')
    # assert status_data.get('Pac_total_W') == latest_data.get('Pac_total_W')

    # assert status_data.get('Timestamp') == '2023-11-20 17:00:59'
    # assert status_data.get('GridFeedIn_W') == 0
    # assert status_data.get('Consumption_W') == 1541
    # assert status_data.get('Production_W') == 103
    # assert status_data.get('Pac_total_W') == 1438

    # assert latest_data.get('Timestamp') == '2023-11-20 17:00:59'
    # assert latest_data.get('GridFeedIn_W') == 0
    # assert latest_data.get('Consumption_W') == 1541
    # assert latest_data.get('Production_W') == 103
    # assert latest_data.get('Pac_total_W') == 1438

    # assert latest_data.get('microgrid_enabled') is True

    # powermeter = battery_discharging_offgrid.sync_get_powermeter()
    # assert powermeter[0]['direction'] == 'production'
    # assert powermeter[1]['direction'] == 'consumption'

    # battery_status =  battery_discharging_offgrid.sync_get_battery()
    # assert battery_status.get('cyclecount') == 30
    # assert battery_status.get('remainingcapacity') == 177.74

    # inverter_data = battery_discharging_offgrid.sync_get_inverter()
    # assert  int(inverter_data.get('pac_microgrid')) == status_data.get('Pac_total_W')
    # assert inverter_data.get('pac_microgrid') == 1438.67
    # assert inverter_data.get('uac') == 233.55

    # configurations = battery_discharging_offgrid.sync_get_configurations()
    # assert configurations.get('DE_Software') == '1.14.5'
    # assert configurations.get('EM_USOC') == 20
