class Order:
    def __init__(self, symbol, quantity=0.0, price=None, side='buy', order_type='market'):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.side = side
        self.order_type = order_type
