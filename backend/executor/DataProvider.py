
from backend.executor import Context


class DataProvider:
    def get_context(self, strategy) -> Context:
        """Build a Context for the given strategy's required symbols/timeframe."""
        pass