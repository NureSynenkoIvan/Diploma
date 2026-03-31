class BacktestResult:
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.initial_amount = 0
        self.final_amount = 0
        self.overall_profit_percent: float = 0.0
        self.mean_monthly_profit_percent: float = 0.0
        self.max_drawdown_percent: float = 0.0
        self.win_rate_percent: float = 0.0

    def __str__(self):
        return (f"Strategy name: {self.strategy_name} \n"
                f"Initial amount: {self.initial_amount} \n"
                f"Final amount: {self.final_amount} \n"
                f"Overall profit percent: {self.overall_profit_percent} \n"
                f"Mean monthly profit percent: {self.mean_monthly_profit_percent} \n"
                f"Max drawdown percent: {self.max_drawdown_percent} \n"
                f"Win rate: {self.win_rate_percent}")
