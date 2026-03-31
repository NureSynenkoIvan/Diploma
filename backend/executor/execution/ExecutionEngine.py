import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        self.trade_history = []  # List of closed trade PnLs: [50.5, -20.0, ...]
        self.open_positions = {}  # Tracks {symbol: {'price': float, 'qty': float, 'side': str}}
        logger.info("Backtest execution engine initialized with trade tracking.")

    def execute(self, order):
        """Simulate execution and record trade performance."""
        symbol = order.symbol

        if symbol in self.open_positions:
            prev_order = self.open_positions[symbol]

            if prev_order['side'] != order.side:
                # Calculate PnL: (Exit Price - Entry Price) * Quantity
                # Note: This logic assumes 'Buy Low, Sell High'
                entry_price = prev_order['price']
                exit_price = order.price

                if prev_order['side'] == 'buy':
                    pnl = (exit_price - entry_price) * order.quantity
                else:  # shorting logic
                    pnl = (entry_price - exit_price) * order.quantity

                self.trade_history.append(pnl)
                logging.info(f"TRADE CLOSED: {symbol} | PnL: {pnl:.2f}")

                # Remove from open positions
                del self.open_positions[symbol]
            else:
                # Logic for adding to an existing position could go here
                pass
        else:
            # 2. Open a new position
            self.open_positions[symbol] = {
                'price': order.price,
                'quantity': order.quantity,
                'side': order.side
            }
            logging.info(f"TRADE OPENED: {order.side.upper()} {symbol} at {order.price}")

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
        raise NotImplementedError("Binance execution logic not implemented yet.")

