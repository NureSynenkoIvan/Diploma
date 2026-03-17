
class Requirement:
    def validate(self, strategy, bot):
        pass

class MustHaveSufficientAmountOfSymbols(Requirement):
    def validate(self, strategy, bot):
        if (len(bot.symbols) < strategy.required_symbols):
            raise Exception(f"Strategy requires at least {strategy.required_symbols} symbols, got only {len(bot.symbols)}")