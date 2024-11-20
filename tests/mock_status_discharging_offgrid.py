import json
def status_discharging()-> json:
    return {
        'Apparent_output': 438,
        'BackupBuffer': '20',
        'BatteryCharging': False,
        'BatteryDischarging': True,
        'Consumption_Avg': 563,
        'Consumption_W': 541,
        'Fac': 50.0167121887207,
        'FlowConsumptionBattery': True,
        'FlowConsumptionGrid': False,
        'FlowConsumptionProduction': True,
        'FlowGridBattery': False,
        'FlowProductionBattery': False,
        'FlowProductionGrid': False,
        'GridFeedIn_W': 0,
        'IsSystemInstalled': 1,
        'OperatingMode': '2',
        'Pac_total_W': 438,
        'Production_W': 102,
        'RSOC': 19,
        'RemainingCapacity_Wh': 3929,
        'Sac1': 438,
        'Sac2': None,
        'Sac3': None,
        'SystemStatus': 'OffGrid',
        'Timestamp': '2023-11-20 10:24:39',
        'USOC': 19,
        'Uac': 237,
        'Ubat': 211,
        'dischargeNotAllowed': False,
        'generator_autostart': False
    }