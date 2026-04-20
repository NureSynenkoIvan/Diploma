from app.executor.execution.Order import Order


class Signal:
    def __init__(self, side):
        self.side = side

    def to_order(self):
        raise NotImplementedError("To be implemented in subclass")

class SimpleSignal(Signal):
    def __init__(self, symbol, quantity = 0.0, price=0.0, side="buy", order_type="market"):
        super().__init__(side)
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.order_type = order_type

    def to_order(self) -> Order:
        return Order(self.symbol, self.quantity, self.price, self.side, self.order_type)
