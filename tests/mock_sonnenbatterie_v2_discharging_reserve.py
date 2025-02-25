"""Mock batterie data also used in package sonnenbatterie_api_v2 & ha component sonnenenbatterie
    Discharging below reserve (OffGrid)
"""
import json
def __mock_status_discharging(*args)-> json:
    return {
        'Apparent_output': 1438,
        'BackupBuffer': '20',
        'BatteryCharging': False,
        'BatteryDischarging': True,
        'Consumption_Avg': 1541,
        'Consumption_W': 1563,
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
        'Pac_total_W': 1438,
        'Production_W': 125,
        'RSOC': 18,
        'RemainingCapacity_Wh': 6723,
        'Sac1': 438,
        'Sac2': None,
        'Sac3': None,
        'SystemStatus': 'OffGrid',
        'Timestamp': '2023-11-20 17:00:59',
        'USOC': 11,
        'Uac': 237,
        'Ubat': 211,
        'dischargeNotAllowed': False,
        'generator_autostart': False
    }

def __mock_latest_discharging(*args)-> json:
    return {
        'FullChargeCapacity': 20187.086,
        'GridFeedIn_W': 0,
        'Pac_total_W': 1438,
        'Consumption_W': 1563,
        'Production_W': 125,
        'RSOC': 18,
        'SetPoint_W': 439,
        'Timestamp': '2023-11-20 17:00:59',
        'USOC': 11,
        'UTC_Offet': 2,
        'ic_status': {
            'DC Shutdown Reason': {
                'Critical BMS Alarm': False,
                'Electrolyte Leakage': False,
                'Error condition in BMS initialization': False,
                'HW_Shutdown': False,
                'HardWire Over Voltage': False,
                'HardWired Dry Signal A': False,
                'HardWired Under Voltage': False,
                'Holding Circuit Error': False,
                'Initialization Timeout': False,
                'Initialization of AC contactor failed': False,
                'Initialization of BMS hardware failed': False,
                'Initialization of DC contactor failed': False,
                'Initialization of Inverter failed': False,
                'Invalid or no SystemType was set': False,
                'Inverter Over Temperature': False,
                'Inverter Under Voltage': False,
                'Inverter Version Too Low For Dc-Module': False,
                'Manual shutdown by user': False,
                'Minimum rSOC of System reached': False,
                'Modules voltage out of range': False,
                'No Setpoint received by HC': False,
                'Odd number of battery modules': False,
                'One single module detected and module voltage is out of range': False,
                'Only one single module detected': False,
                'Shutdown Timer started': False,
                'System Validation failed': False,
                'Voltage Monitor Changed': False
            },
            'Eclipse Led': {
                'Blinking Red': False,
                'Pulsing Green': False,
                'Pulsing Orange': False,
                'Pulsing White': True,
                'Solid Red': False
            },
            'MISC Status Bits': {
                'Discharge not allowed': False,
                'F1 open': False,
                'Min System SOC': False,
                'Min User SOC': False,
                'Setpoint Timeout': False
            },
            'Microgrid Status': {
                'Continious Power Violation': False,
                'Discharge Current Limit Violation': False,
                'Low Temperature': False,
                'Max System SOC': False,
                'Max User SOC': False,
                'Microgrid Enabled': False,
                'Min System SOC': False,
                'Min User SOC': False,
                'Over Charge Current': False,
                'Over Discharge Current': False,
                'Peak Power Violation': False,
                'Protect is activated': False,
                'Transition to Ongrid Pending': True
            },
            'Setpoint Priority': {
                'BMS': False,
                'Energy Manager': True,
                'Full Charge Request': False,
                'Inverter': False,
                'Min User SOC': False,
                'Trickle Charge': False
            },
            'System Validation': {
                'Country Code Set status flag 1': False,
                'Country Code Set status flag 2': False,
                'Self test Error DC Wiring': False,
                'Self test Postponed': False,
                'Self test Precondition not met': False,
                'Self test Running': False,
                'Self test successful finished': False
            },
            'nrbatterymodules': 4,
            'secondssincefullcharge': 2574,
            'statebms': 'ready',
            'statecorecontrolmodule': 'offgrid',
            'stateinverter': 'running',
            'timestamp': 'Mon Nov 20 17:00:59 2023'
        }
    }

def __mock_battery_discharging(*args)-> json:
    return {
        "balancechargerequest":0.0,
        "chargecurrentlimit":39.97,
        "cyclecount":30.0,
        "dischargecurrentlimit":39.97,
        "fullchargecapacity":201.98,
        "fullchargecapacitywh":20683.490,
        "maximumcelltemperature":19.95,
        "maximumcellvoltage":3.257,
        "maximumcellvoltagenum":0.0,
        "maximummodulecurrent":0.0,
        "maximummoduledcvoltage":104.15,
        "maximummoduletemperature":-273.15,
        "minimumcelltemperature":18.95,
        "minimumcellvoltage":3.251,
        "minimumcellvoltagenum":0.0,
        "minimummodulecurrent":0.0,
        "minimummoduledcvoltage":104.15,
        "minimummoduletemperature":-273.15,
        "nominalmoduledcvoltage":102.4,
        "relativestateofcharge":18.0,
        "remainingcapacity":36.3564,
        "systemalarm":0.0,
        "systemaveragecurrent":0.035,
        "systemcurrent":0.0,
        "systemdcvoltage":208.3,
        "systemstatus":49,
        "systemtime":0.0,
        "systemwarning":0.0,
        "usableremainingcapacity":22.2178
    }

def __mock_inverter_discharging(*args)-> json:
    return {
        "fac": 0.0,
        "iac_total": 0.39,
        "ibat": 0.01,
        "ipv": 0.0,
        "pac_microgrid": 0.0,
        "pac_total": 1438.67,
        "pbat": -0.14,
        "phi": -0.82,
        "ppv": 0.0,
        "sac_total": 0.0,
        "tmax": 55.53,
        "uac": 233.55,
        "ubat": 209.18,
        "upv": 0.0
    }