# Sonnen API v2 package
Sonnenbatterie API v2 fetcher

Requires API read token generated by Sonnen batterie management portal.

Does not use the default user login to authenticate API, only the token.

Parameters to run tests for batterie IP address and API token are specified in .env file. See env.example for template.

There are three ways to update from the Batterie:

1. Async caller uses Async update
        def async async_caller()
            batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
            success = batterie.async_update()

    Test:
    see battery_charging_asyncio & test_common_results_asyncio


2.  Sync caller uses Async update
        def sync_caller()
            batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
            success = batterie.update()

    Test:
    see battery_charging_sync & test_common_results_sync


3. Async caller uses sync update from coroutine passed to asyncio.run_in_executor (ha emulation)
        async def _async_update_data(self):
            result = await asyncio.async_add_executor_job(
                self.sync_caller
            )

        def sync_caller()
            batterie = Batterie(API_READ_TOKEN, BATTERIE_HOST, BATTERIE_HOST_PORT, LOGGER_NAME)
            success = batterie.sync_update()

    Test:
    see battery_charging_coroutine & test_common_results_coroutine



Variation #3 use case is Home Assistant custom_component sonnenbatterie
