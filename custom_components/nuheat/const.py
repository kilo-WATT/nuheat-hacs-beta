"""Constants for the NuHeat integration."""

from datetime import timedelta

DOMAIN = "nuheat"
CONF_SERIAL_NUMBER = "serial_number"
AUTHORIZE_URL = "https://identity.nam.mynuheat.com/connect/authorize"
TOKEN_URL = "https://identity.nam.mynuheat.com/connect/token"
OAUTH_SCOPES = ("openid", "openapi", "offline_access")

SCAN_INTERVAL = timedelta(minutes=5)
SETPOINT_RECONCILE_DELAY = 2
SETPOINT_RECONCILE_RETRY = 8
SETPOINT_RECONCILE_TIMEOUT = 30

MIN_TEMP_C = 5.0
MAX_TEMP_C = 35.0

PRESET_RUN = "Run Schedule"
PRESET_TEMPORARY_HOLD = "Temporary Hold"
PRESET_PERMANENT_HOLD = "Permanent Hold"
PRESET_ALIASES = {
    "run_schedule": PRESET_RUN,
    "temporary_hold": PRESET_TEMPORARY_HOLD,
    "permanent_hold": PRESET_PERMANENT_HOLD,
}
PRESET_MODES = [
    PRESET_RUN,
    PRESET_TEMPORARY_HOLD,
    PRESET_PERMANENT_HOLD,
    *PRESET_ALIASES,
]
