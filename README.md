# Sonnen API v2
Sonnenbatterie API v2 fetcher

Requires API read token generated by Sonnen batterie management portal.

Does not use the default user login to authenticate API, only the token.

Parameters to run tests for batterie IP address and API token are specified in .env file. See env.example for template.

There are three ways to update from the Batterie:

1. Async update called from an async method.
        def async async_caller()
            batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
            success = batterie.async_update()

    Test:
    from asyncmock import AsyncMock
    from . mock_sonnenbatterie_v2_charging import __mock_status_charging, __mock_latest_charging, __mock_configurations, __mock_battery, __mock_powermeter, __mock_inverter

    @pytest.mark.asyncio
    async def test_asyncio_update(mocker):
    """Batterie asyncio test using mock data"""
    mocker.patch.object(Batterie, "async_fetch_status", AsyncMock(return_value=__mock_status_charging()))
    mocker.patch.object(Batterie, "async_fetch_latest_details", AsyncMock(return_value=__mock_latest_charging()))
    mocker.patch.object(Batterie, "async_fetch_configurations", AsyncMock(return_value=__mock_configurations()))
    mocker.patch.object(Batterie, "async_fetch_battery_status", AsyncMock(return_value=__mock_battery()))
    mocker.patch.object(Batterie, "async_fetch_powermeter", AsyncMock(return_value=__mock_powermeter()))
    mocker.patch.object(Batterie, "async_fetch_inverter_data", AsyncMock(return_value=__mock_inverter()))

    battery_charging = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
    success = await battery_charging.async_update()
    assert success is True

    assert battery_charging.status_battery_charging is True
    assert battery_charging.status_battery_discharging is False
    assert battery_charging.system_status == 'OnGrid'


2. Async update called from sync method
        def sync_caller()
            batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
            success = batterie.update()

    Test:
    from asyncmock import AsyncMock
    from . mock_sonnenbatterie_v2_charging import __mock_status_charging, __mock_latest_charging, __mock_configurations, __mock_battery, __mock_powermeter, __mock_inverter

    @pytest.mark.asyncio
    def test_async_update(mocker):
    """Batterie sync test using asyncio mock data"""
    mocker.patch.object(Batterie, "async_fetch_status", AsyncMock(return_value=__mock_status_charging()))
    mocker.patch.object(Batterie, "async_fetch_latest_details", AsyncMock(return_value=__mock_latest_charging()))
    mocker.patch.object(Batterie, "async_fetch_configurations", AsyncMock(return_value=__mock_configurations()))
    mocker.patch.object(Batterie, "async_fetch_battery_status", AsyncMock(return_value=__mock_battery()))
    mocker.patch.object(Batterie, "async_fetch_powermeter", AsyncMock(return_value=__mock_powermeter()))
    mocker.patch.object(Batterie, "async_fetch_inverter_data", AsyncMock(return_value=__mock_inverter()))

    battery_charging = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
    success = battery_charging.update()
    assert success is True

    assert battery_charging.status_battery_charging is True
    assert battery_charging.status_battery_discharging is False
    assert battery_charging.system_status == 'OnGrid'


3. Sync update called from sync method or coroutine passed to asyncio.run_in_executor
        async def _async_update_data(self):
            result = await asyncio.async_add_executor_job(
                self.sync_caller
            )

        def sync_caller()
            batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
            success = batterie.sync_update()

    Test:
    from . mock_sonnenbatterie_v2_charging import __mock_status_charging, __mock_latest_charging, __mock_configurations, __mock_battery, __mock_powermeter, __mock_inverter

    mocker.patch.object(Batterie, "fetch_status", __mock_status_charging)
    mocker.patch.object(Batterie, "fetch_latest_details", __mock_latest_charging)
    mocker.patch.object(Batterie, "fetch_configurations", __mock_configurations)
    mocker.patch.object(Batterie, "fetch_battery_status", __mock_battery)
    mocker.patch.object(Batterie, "fetch_powermeter", __mock_powermeter)
    mocker.patch.object(Batterie, "fetch_inverter_data", __mock_inverter)

    battery_charging = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
    success = battery_charging.sync_update()
    assert success is True

    assert battery_charging.status_battery_charging is True
    assert battery_charging.status_battery_discharging is False
    assert battery_charging.system_status == 'OnGrid'



Variation #3 use case is Home Assistant custom_component sonnenbatterie
