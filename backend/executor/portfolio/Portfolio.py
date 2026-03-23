
from backend.executor.execution import Order
from backend.executor.execution.ExecutionEngine import ExecutionResult
from backend.executor.portfolio.Position import Position
from backend.executor.portfolio.PortfolioProvider import PortfolioProvider

class Portfolio:
    def __init__(self, base_token_amount=0.0, base_token_symbol='USDT', positions=None):
        self.base_token_amount = base_token_amount
        self.base_token_symbol = base_token_symbol
        self.positions = positions if positions is not None else []
    
    def apply(self, order : Order, execution_result : ExecutionResult):
        if (execution_result.success):
            # This is a simplified example; real logic would be more complex
            if order.side == 'buy':
                self.base_token_amount -= order.quantity * (order.price or 0)
                self.positions.append(Position(order.symbol, order.quantity, order.price))
            elif order.side == 'sell':
                self.base_token_amount += order.quantity * (order.price or 0)
                if order.symbol in [p.symbol for p in self.positions]:
                    # For simplicity, we just remove the position; real logic would handle partial sells
                    self.positions.remove(next(p for p in self.positions if p.symbol == order.symbol and p.quantity >= order.quantity))
        pass