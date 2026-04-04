from enum import Enum

class Timeframe(Enum):
    ONE_SECOND = 1
    ONE_MINUTE = 60
    FIVE_MINUTES = 300
    FIFTEEN_MINUTES = 900
    THIRTY_MINUTES = 1800
    ONE_HOUR = 3600
    FOUR_HOURS = 14400
    ONE_DAY = 86400
    ONE_WEEK = 604800

