"""pytest tests/test_mock_batterie_wrapped.py -s -v -x -k test_batterie_charging_async
    1. Async update called from an async method.
    2. Async update called from sync method
"""
#import datetime
import os
import sys
#import json

import logging
import urllib3

#for tests only
import pytest
from unittest.mock import patch
from asyncmock import AsyncMock
from freezegun import freeze_time

from sonnen_api_v2 import Batterie, BatterieAuthError, BatterieHTTPError , BatterieError

from .mock_sonnenbatterie_v2_charging import __mock_status_charging, __mock_latest_charging, __mock_configurations, __mock_battery, __mock_powermeter, __mock_inverter
#from .mock_sonnenbatterie_v2_discharging import __mock_status_discharging, __mock_latest_discharging, __mock_battery_discharging
from .mock_battery_responses import (
    __battery_auth200,
    __battery_AuthError_401,
    __battery_AuthError_403,
    __battery_HTTPError_301,
)

from .battery_charging_asyncio import fixture_battery_charging
#from .battery_charging_sync import fixture_battery_charging
from .battery_discharging_sync import fixture_battery_discharging

LOGGER_NAME = None # "sonnenapiv2" #

logging.getLogger("mock_batterie").setLevel(logging.WARNING)

if LOGGER_NAME is not None:
    filename=f'tests/logs/{LOGGER_NAME}.log'
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
    logger.info ('Asyncio mock batterie tests')


@pytest.mark.asyncio
async def test_batterie_async(mocker):
    """Batterie charging using mock data
        1. Async update called from an async method.
    """
    mocker.patch.object(Batterie, "async_fetch_configurations", AsyncMock(return_value=__mock_configurations()))
    mocker.patch.object(Batterie, "async_fetch_status", AsyncMock(return_value=__mock_status_charging()))
    mocker.patch.object(Batterie, "async_fetch_latest_details", AsyncMock(return_value=__mock_latest_charging()))
    mocker.patch.object(Batterie, "async_fetch_battery_status", AsyncMock(return_value=__mock_battery()))
    mocker.patch.object(Batterie, "async_fetch_powermeter", AsyncMock(return_value=__mock_powermeter()))
    mocker.patch.object(Batterie, "async_fetch_inverter", AsyncMock(return_value=__mock_inverter()))

    battery_charging = Batterie('fakeToken', 'fakeHost')

    success = await battery_charging.async_update()
    assert success is not False

    version = battery_charging.configuration_de_software # mock_configurations
    status = battery_charging.system_status # latest_charging
    backup_buffer = battery_charging.status_backup_buffer # status_charging
    kwh_consumed = battery_charging.kwh_consumed # mock_powermeter
    cycles = battery_charging.battery_cycle_count # mock_battery
    PAC_total = battery_charging.inverter_pac_total # mock_inverter

    print(f'\n\rStatus: {status}  Software Version: {version}   Battery Cycles: {cycles:,}')
    print(f'PAC: {PAC_total:,.2f}W  Consumed: {kwh_consumed:,.2f}  Backup Buffer: {backup_buffer}%')
    assert status == 'OnGrid'
    assert cycles == 30
    assert version == '1.14.5'
    assert PAC_total == -1394.33
    assert backup_buffer == 20
    assert kwh_consumed == 816.5


@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_charging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
@freeze_time("20-11-2023 17:00:00") # charging time
async def test_batterie_charging_async(battery_charging: Batterie):
    """sonnenbatterie Emulator package - using mock data
        Fake good token returns configs data
    """
    success = await battery_charging.async_validate_token()
    assert success is not False

    success = await battery_charging.async_update()
    assert success is not False

    charging_flows = battery_charging.status_flows
    assert charging_flows == {'FlowConsumptionBattery': False, 'FlowConsumptionGrid': False, 'FlowConsumptionProduction': True, 'FlowGridBattery': False, 'FlowProductionBattery': True, 'FlowProductionGrid': False}

    #common tests for all fixture methods
    from . check_results import check_charge_results

    check_charge_results(battery_charging)


@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_discharging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
@freeze_time("20-11-2023 17:00:55") # discharging time
async def test_batterie_discharging_async(battery_discharging: Batterie):
    """sonnenbatterie Emulator package - using mock data
        Fake good token returns configs data
    """

    success = await battery_discharging.async_validate_token()
    assert success is not False

    success = await battery_discharging.async_update()
    assert success is not False

    assert battery_discharging.discharging > 0
    assert battery_discharging.charging == 0

    discharging_flows = battery_discharging.status_flows
    assert discharging_flows == {'FlowConsumptionBattery': True, 'FlowConsumptionGrid': False, 'FlowConsumptionProduction': True, 'FlowGridBattery': True, 'FlowProductionBattery': False, 'FlowProductionGrid': False}

    #common tests for all fixture methods
    from . check_results import check_discharge_results

    check_discharge_results(battery_discharging)


@pytest.mark.usefixtures("battery_charging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
@freeze_time("20-11-2023 17:00:00")
def test_batterie_charging_wrapped(battery_charging: Batterie):
    """sonnenbatterie Emulator package - using mock data
        2. Async update called from sync method
    """

#    battery_charging = Batterie('fakeToken', 'fakeHost')
    success = battery_charging.sync_validate_token()
    assert success is not False
    success = battery_charging.get_update()
    assert success is not False

    latestData = {}
    # code syntax from custom_component coordinator.py
    # latestData["battery_system"] = battery_charging.get_batterysystem()
    # batt_module_capacity = int(
    #     latestData["battery_system"]["battery_system"]["system"][
    #         "storage_capacity_per_module"
    #     ]
    # )
    # assert batt_module_capacity == 5000
    # batt_module_count = int(latestData["battery_system"]["modules"])

    # assert batt_module_count == 4
    latestData["latest_data"] = battery_charging.get_latest_data()
    #print(f'latestData: {latestData["latest_data"]}', flush=True)
    assert latestData["latest_data"]['Timestamp'] == '2023-11-20 17:00:55' #correct test data loaded
    assert latestData["latest_data"].get('RSOC') == 88


    latestData["status"] = battery_charging.get_status()
    assert latestData["status"]['Timestamp'] == '2023-11-20 17:00:55' #correct test data loaded

#    print(f'status type: {type(latestData["status"])}')

    if latestData["status"]["BatteryCharging"]:
        battery_current_state = "charging"
    elif latestData["status"]["BatteryDischarging"]:
        battery_current_state = "discharging"
    else:
        battery_current_state = "standby"
    rsoc = latestData["status"]["RSOC"]
    operatingmode = latestData.get("status", {}).get("OperatingMode")
    print(f'battery_state: {battery_current_state}  RSOC: {rsoc}%  Operating Mode: {operatingmode}', flush=True)

    latestData["powermeter"] = battery_charging.get_powermeter()
    if(isinstance(latestData["powermeter"],dict)):
        newPowerMeters=[]
        for index,dictIndex in enumerate(latestData["powermeter"]):
            newPowerMeters.append(latestData["powermeter"][dictIndex])
        print(f'new powermeters: {newPowerMeters}')

    # batt_reserved_factor = 7.0
#    total_installed_capacity = int(batt_module_count * batt_module_capacity)
    # unusable_reserved_capacity = int(
    #         total_installed_capacity * (batt_reserved_factor / 100.0)
    #     )
    # remaining_capacity = (
    #         int(total_installed_capacity * latestData["status"]["RSOC"]) / 100.0
    #     )
    # remaining_capacity_usable = max(
    #         0, int(remaining_capacity - unusable_reserved_capacity))
#    print(f'total_capacity (calc): {total_installed_capacity:,}Wh')
    # print(f'unusable_reserved (calc): {unusable_reserved_capacity:,}Wh  remaining_capacity:{remaining_capacity}Wh')
    # print(f'remaining_usable (calc): {remaining_capacity_usable:,}Wh')
#    assert total_installed_capacity == 20000
    # assert unusable_reserved_capacity == 1400
    # assert remaining_capacity == 19600
    # assert remaining_capacity_usable == 18200

    latestData["battery_info"] = battery_charging.get_battery()
    # current_state = latestData.get("battery_info", {}).get("current_state")
    # print(f'current_state: {current_state}')
    # assert current_state == 'charging'
    # measurements = latestData["battery_info"]['measurements']
    # print(f'measurements: {measurements}')
    # total_capacity_usable = (latestData.get("battery_info", {}).get(
    #             "total_installed_capacity", 0
    #         )
    #         - latestData.get("battery_info", {}).get("reserved_capacity", 0)
    # )
    BackupBuffer = latestData.get("status", {}).get("BackupBuffer")
    backup_buffer_capacity = latestData.get("battery_info", {}).get("backup_buffer_capacity")
    print(f'BackupBuffer: {BackupBuffer}%  Backup_Usable: {backup_buffer_capacity:,}Wh', flush=True)
    total_capacity_raw = latestData.get("battery_info", {}).get("fullchargecapacitywh")
    reserved_capacity_raw = latestData.get("battery_info", {}).get("dod_reserved_capacity")
    print(f'total_capacity (raw): {total_capacity_raw:,}Wh', flush=True)
#    print(f'Reserved (raw): {reserved_capacity_raw:,}Wh  total_usable (calc): {total_capacity_usable:,}Wh')
    assert total_capacity_raw == 20683.490
#    assert total_capacity_usable == 18553
    assert reserved_capacity_raw == 1448.0
    remaining_capacity = latestData.get("battery_info", {}).get("remaining_capacity")
    remaining_capacity_usable = latestData.get("battery_info", {}).get("remaining_capacity_usable")
    print(f'remaining_capacity (raw): {remaining_capacity:,}Wh  remaining_usable (raw): {remaining_capacity_usable:,}Wh', flush=True)
    assert remaining_capacity == 18200.6
    assert remaining_capacity_usable == 16752.6

    timeouts = battery_charging.get_request_connect_timeouts()
    assert timeouts == (20,20)
    timeouts = battery_charging.set_request_connect_timeouts((15,25))
    assert timeouts == (15,25)

    latestData["inverter"] = battery_charging.get_inverter()
    assert latestData["inverter"] .get("pac_total") == -1394.33

    latestData["configurations"] = battery_charging.get_configurations()
    assert latestData["configurations"] .get("DepthOfDischargeLimit") == 7

    assert battery_charging.used_capacity_wh == 3835.6
    #common tests for all fixture methods
    from . check_results import check_charge_results

    check_charge_results(battery_charging)

@pytest.mark.usefixtures("battery_discharging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
@freeze_time("20-11-2023 17:00:55")
def test_batterie_discharging_wrapped(battery_discharging: Batterie):
    """sonnenbatterie Emulator package - using mock data
        Fake good token returns configs data
    """

#    battery_discharging = Batterie('fakeToken', 'fakeHost')
    success = battery_discharging.sync_validate_token()
    assert success is not False
    success = battery_discharging.update()
    assert success is not False

    discharging_flows = battery_discharging.status_flows
#    print(f'discharging_flows: {discharging_flows}')
    assert discharging_flows == {'FlowConsumptionBattery': True, 'FlowConsumptionGrid': False, 'FlowConsumptionProduction': True, 'FlowGridBattery': True, 'FlowProductionBattery': False, 'FlowProductionGrid': False}

    #common tests for all fixture methods
    from . check_results import check_discharge_results

    check_discharge_results(battery_discharging)


@pytest.mark.usefixtures("battery_discharging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_AuthError_401)
def test_batterie_unauth_token401(battery_discharging: Batterie):
    """sonnenbatterie Emulator package - using mock data.
    """
    with pytest.raises(BatterieAuthError, match='Invalid token "fakeToken" status: 401'):
        success = battery_discharging.sync_validate_token()


@pytest.mark.usefixtures("battery_discharging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_AuthError_403)
def test_batterie_unauth_token403(battery_discharging: Batterie):
    """sonnenbatterie Emulator package - using mock data.
    """
    with pytest.raises(BatterieAuthError, match='Invalid token "fakeToken" status: 403'):
        success = battery_discharging.sync_validate_token()

@pytest.mark.usefixtures("battery_discharging")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_HTTPError_301)
def test_batterie_HTTPerror301(battery_discharging: Batterie):
    """sonnenbatterie Emulator package - using mock data.
    """
    with pytest.raises(BatterieHTTPError, match='HTTP Error fetching endpoint "http://fakeHost:80/api/v2/configurations" status: 301'):
        success = battery_discharging.sync_validate_token()
