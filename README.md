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
    @pytest.mark.asyncio
    async def test_get_powermeter(mocker):
    """Batterie powermeter test using mock data"""
    mocker.patch.object(Batterie, "async_fetch_powermeter", AsyncMock(return_value=__mock_powermeter()))


2. Async update called from sync method
        def sync_caller()
            batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
            success = batterie.sync_update()

    Test:
    same as for async_update, above


3. Sync update called from sync method or coroutine passed to asyncio.run_in_executor
        async def _async_update_data(self):
            result = await asyncio.async_add_executor_job(
                self.sync_caller
            )

        def sync_caller()
            batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
            success = batterie.update()

    Test:

    battery1_powermeter_data = responses.Response(
        method='GET',
        url=(f'http://{BATTERIE_1_HOST}:{BATTERIE_HOST_PORT}/api/v2/powermeter'),
        status=200,
        json=__mock_powermeter()
    )
    responses.add(battery1_powermeter_data)
    success = batterie.sync_update()


Variation #3 use case is Home Assistant custom_component sonnenbatterie
