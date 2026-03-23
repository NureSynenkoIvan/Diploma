class PortfolioProvider:

    def get_portfolio(self, strategy):
        # In a real implementation, this would fetch the portfolio from the exchange or a database.
        # Here we return a dummy portfolio for demonstration purposes.
        pass

    def apply(self, order, result):
        # In a real implementation, this would update the portfolio based on the executed order and its result.
        pass

class BacktestPortfolioProvider(PortfolioProvider):
    def __init__(self):
        self.portfolio = {}

    def get_portfolio(self, strategy):
        return self.portfolio
    
    def apply(self, order, result):
        self.portfolio.apply(order, result)