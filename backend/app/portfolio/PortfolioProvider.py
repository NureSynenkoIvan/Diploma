from app.executor.portfolio.Portfolio import Portfolio


class PortfolioProvider:

    def get_portfolio(self, strategy):
        # In a real implementation, this would fetch the portfolio from the exchange or a database.
        # Here we return a dummy portfolio for demonstration purposes.
        pass

    def apply(self, order):
        # In a real implementation, this would update the portfolio based on the executed order and its result.
        pass

class BacktestPortfolioProvider(PortfolioProvider):
    def __init__(self, quantity):
        self.portfolio = Portfolio(base_token_amount=quantity)

    def get_portfolio(self, strategy):
        return self.portfolio
    
    def apply(self, order):
        self.portfolio.apply(order)