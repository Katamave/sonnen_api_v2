# API latestdata System-Status Groups
IC_STATUS = 'ic_status'
DC_SHUTDOWN_REASON = 'DC Shutdown Reason'
IC_ECLIPSE_LED = 'Eclipse Led'
MICROGRID_STATUS = 'Microgrid Status'

# API Item keys
BATTERY_CYCLE_COUNT = 'cyclecount'
BATTERY_FULL_CHARGE_CAPACITY_AH = 'fullchargecapacity'
BATTERY_FULL_CHARGE_CAPACITY_WH = 'fullchargecapacitywh'
BATTERY_MAX_CELL_TEMP = 'maximumcelltemperature'
BATTERY_MAX_CELL_VOLTAGE = 'maximumcellvoltage'
BATTERY_MAX_MODULE_CURRENT = 'maximummodulecurrent'
BATTERY_MAX_MODULE_VOLTAGE = 'maximummoduledcvoltage'
BATTERY_MAX_MODULE_TEMP = 'maximummoduletemperature'
BATTERY_MIN_CELL_TEMP = 'minimumcelltemperature'
BATTERY_MIN_CELL_VOLTAGE = 'minimumcellvoltage'
BATTERY_MIN_MODULE_CURRENT = 'minimummodulecurrent'
BATTERY_MIN_MODULE_VOLTAGE = 'minimummoduledcvoltage'
BATTERY_MIN_MODULE_TEMP = 'minimummoduletemperature'
BATTERY_REMAINING_CAPACITY = 'remainingcapacity'
BATTERY_NOMINAL_MODULE_VOLTAGE = 'nominalmoduledcvoltage'
BATTERY_RSOC = 'relativestateofcharge'
BATTERY_SYSTEM_CURRENT = 'systemcurrent'
BATTERY_AVERAGE_CURRENT = 'systemaveragecurrent'
BATTERY_SYSTEM_VOLTAGE = 'systemdcvoltage'
BATTERY_USABLE_REMAINING_CAPACITY = 'usableremainingcapacity'
CONFIGURATION_EM_OPERATINGMODE = "EM_OperatingMode"
CONFIGURATION_EM_RE_ENABLE_MICROGRID = "EM_RE_ENABLE_MICROGRID"
CONFIGURATION_EM_USER_INPUT_TIME_ONE = "EM_USER_INPUT_TIME_ONE"
CONFIGURATION_EM_USER_INPUT_TIME_TWO = "EM_USER_INPUT_TIME_TWO"
CONFIGURATION_EM_USER_INPUT_TIME_THREE = "EM_USER_INPUT_TIME_THREE"
CONFIGURATION_DE_SOFTWARE = "DE_Software"
CONFIGURATION_EM_USOC = "EM_USOC"
CONFIGURATION_MODULECAPACITY = "CM_MarketingModuleCapacity"
CONFIGURATION_BATTERYMODULES = "IC_BatteryModules"
DETAIL_USOC = 'USOC'
DETAIL_RSOC = 'RSOC'
DETAIL_FULL_CHARGE_CAPACITY = 'FullChargeCapacity'
DETAIL_PAC_TOTAL_W = 'Pac_total_W'
DETAIL_PRODUCTION_W = 'Production_W'
DETAIL_STATE_CORECONTROL_MODULE = "statecorecontrolmodule"
DETAIL_SECONDS_SINCE_FULLCHARGE = 'secondssincefullcharge'
DETAIL_TIMESTAMP = 'Timestamp'
DETAIL_STATE_BMS = 'statebms'
DETAIL_STATE_INVERTER = 'stateinverter'
DC_MINIMUM_RSOC_REACHED = 'Minimum rSOC of System reached'
MG_ENABLED = 'Microgrid Enabled'
MG_MINIMUM_SYSTEM_SOC = 'Min System SOC'
POWERMETER_KWH_IMPORTED = 'kwh_imported'
POWERMETER_AMPERE_L1 = 'a_l1' # bug: a_total is always zero
POWERMETER_VOLT_L1 = 'v_l1_n'
POWERMETER_WATT_L1 = 'w_l1'
POWERMETER_REACTIVE_POWER = 'var_total'
POWERMETER_WATTS_TOTAL = 'w_total'
STATUS_APPARENT_OUTPUT = 'Apparent_output'
STATUS_BACKUPBUFFER = "BackupBuffer"
STATUS_BATTERY_CHARGING = 'BatteryCharging'
STATUS_BATTERY_DISCHARGING = 'BatteryDischarging'
STATUS_CONSUMPTION_W = 'Consumption_W'
STATUS_CONSUMPTION_AVG = 'Consumption_Avg'
STATUS_DISCHARGE_NOT_ALLOWED = 'dischargeNotAllowed'
STATUS_FLOW_CONSUMPTION_BATTERY = 'FlowConsumptionBattery'
STATUS_FLOW_CONSUMPTION_GRID = 'FlowConsumptionGrid'
STATUS_FLOW_CONSUMPTION_PRODUCTION = 'FlowConsumptionProduction'
STATUS_FLOW_GRID_BATTERY = 'FlowGridBattery'
STATUS_FLOW_PRODUCTION_BATTERY = 'FlowProductionBattery'
STATUS_FLOW_PRODUCTION_GRID = 'FlowProductionGrid'
STATUS_FREQUENCY = 'Fac'
STATUS_GRIDFEEDIN_W = 'GridFeedIn_W'
STATUS_MODULES_INSTALLED = 'nrbatterymodules'
STATUS_PAC_TOTAL_W = 'Pac_total_W'
STATUS_PRODUCTION_W = 'Production_W'
STATUS_REMAININGCAPACITY_WH = 'RemainingCapacity_Wh'
STATUS_RSOC = 'RSOC'
STATUS_USOC = 'USOC'
STATUS_SYSTEMSTATUS = 'SystemStatus'
STATUS_TIMESTAMP = 'Timestamp'
INVERTER_PAC_TOTAL = 'pac_total'        #OnGrid
INVERTER_PAC_MICROGRID = 'pac_microgrid' #OffGrid
INVERTER_UAC = 'uac'
INVERTER_UBAT = 'ubat'

# BMS use is not part of charging power
# varies 22W-31W inc. cooling fan
BATTERY_BMS_MAX32_W = -31
BATTERY_BMS_MAX30_W = -29
BATTERY_BMS_MAX28_W = -27
BATTERY_BMS_MAX_W = -24
BATTERY_BMS_MIN_W = -22

# default timeout (seconds)
TIMEOUT = 20
TIMEOUT_CONNECT=0
TIMEOUT_REQUEST=1

RATE_LIMIT = 3 #seconds
DEFAULT_PORT = 80
DEFAULT_PORT = 80

# Manufacturer reserve

BATTERY_BLACKSTART_RESERVE = .07