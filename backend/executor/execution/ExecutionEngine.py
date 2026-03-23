class ExecutionEngine:
    def __init__(self):
        pass
    
    def execute(self, order):
        raise NotImplementedError("Must be implemented by subclasses.")
    

class ExecutionResult:
    def __init__(self, success, order=None, error_message=None):
        self.success = success
        self.order = order
        self.error_message = error_message


class BacktestExecutionEngine(ExecutionEngine):
    def __init__(self):
        super().__init__()
        print("Backtest execution engine initialized")

    def execute(self, order):
        """Execute a single tick for the given bot."""
        # In a backtest, we would simulate order execution based on historical data.
        # For simplicity, we assume all orders are executed successfully at the next tick's price.
        return ExecutionResult(success=True, order=order)
    

class BinanceExecutionEngine(ExecutionEngine):
    def __init__(self, api_key, api_secret):
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        print("Binance execution engine initialized with API key")

    def execute(self, order):
        """Execute the given order on Binance."""
        # Here we would implement the logic to send the order to Binance's API and handle the response.
        # For simplicity, we will just return a successful execution result.
        raise NotImplementedError("Binance execution logic not implemented yet.")

