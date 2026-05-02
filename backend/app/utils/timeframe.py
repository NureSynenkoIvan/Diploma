from datetime import datetime
from enum import Enum

def get_candles_left(since_time, end_time, timeframe):
    if isinstance(since_time, datetime) and isinstance(end_time, datetime):
        duration_seconds = (end_time - since_time).total_seconds()
    elif isinstance(since_time, str) and isinstance(end_time, str):
        """2024-01-01T00:00:00+00:00"""
        since = datetime.fromisoformat(since_time)
        end = datetime.fromisoformat(end_time)
        duration_seconds = (end - since).total_seconds()
    else:
        # 2. Fallback if they are already millisecond timestamps (integers)
        duration_seconds = (end_time - since_time) / 1000

    # Map timeframes to seconds for easy division
    seconds_map = {
        "1s": 1,
        "15s": 15,
        "30s": 30,
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "1h": 3600,
        "4h": 14400,
        "1d": 86400
    }

    divider = seconds_map.get(timeframe, 60)  # Default to 1m if not found
    return int(duration_seconds / divider)