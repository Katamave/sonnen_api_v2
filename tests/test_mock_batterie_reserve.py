"""pytest tests/test_mock_batterie_reserve.py -s -v -x
    1. Async update called from an async method.
"""
#import datetime
import os
import sys
import json

import logging
import urllib3

#for tests only
import pytest
from unittest.mock import patch
#from asyncmock import AsyncMock
from freezegun import freeze_time

from sonnen_api_v2 import Batterie, BatterieAuthError, BatterieHTTPError, BatterieError

from .mock_battery_responses import (
    __battery_auth200,
)

from .battery_discharging_reserve_asyncio import fixture_battery_discharging_reserve
#import battery_discharging_reserve_asyncio

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
    logger.info ('Asyncio mock batterie reserve tests')


@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_discharging_reserve")
@patch.object(urllib3.HTTPConnectionPool, 'urlopen', __battery_auth200)
@freeze_time("20-11-2023 17:00:59") # disharging reserve time
async def test_batterie_discharging_reserve(battery_discharging_reserve: Batterie):
    """package using mock reserve data"""

    success = await battery_discharging_reserve.async_validate_token()
    assert success is not False
    success = await battery_discharging_reserve.async_update()
    assert success is not False

    assert battery_discharging_reserve.system_status_timestamp.strftime('%d.%b.%Y %H:%M:%S') == '20.Nov.2023 17:00:59' #correct test data loaded

    discharging_flows = battery_discharging_reserve.status_flows
#    print(f'discharging_flows: {discharging_flows}')
    assert discharging_flows == {'FlowConsumptionBattery': True, 'FlowConsumptionGrid': False, 'FlowConsumptionProduction': True, 'FlowGridBattery': True, 'FlowProductionBattery': False, 'FlowProductionGrid': False}

    assert battery_discharging_reserve.fully_discharged_at.strftime('%d.%b.%Y %H:%M') == '20.Nov.2023 18:27'
    #common tests for all fixture methods
    from . check_results import check_reserve_results

    check_reserve_results(battery_discharging_reserve)
