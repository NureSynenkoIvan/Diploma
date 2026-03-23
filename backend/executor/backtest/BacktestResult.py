class BacktestResult:
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.overall_profit_percent: float = 0.0
        self.mean_monthly_profit_percent: float = 0.0
        self.max_drawdown_percent: float = 0.0
        self.win_rate_percent: float = 0.0
