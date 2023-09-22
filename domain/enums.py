from enum import Enum

class VC_STATE (Enum):
    USER_NOT_IN_VC = 1
    BOT_NOT_IN_SERVER = 2
    BOT_NOT_IN_CHANNEL = 3
    SAME_SERVER_CHANNEL = 4