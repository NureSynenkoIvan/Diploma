from app.execution.context import Context
from app.strategies.rules.strategy_requirements import Requirement, DataRequirement
import inspect

class Strategy:
    def __init__(self, 
                 name, 
                 description):
        self.name = name
        self.description = description
        self.requirements : list[Requirement] = []
        self.data_requirements : list[DataRequirement] = []

    def validate(self, bot):
        for requirement in self.requirements:
            requirement.validate(self, bot)

    def validate_data_requirements(self, historical_data):
        for requirement in self.data_requirements:
            requirement.validate(historical_data)

    def on_start(self, context : Context):
        pass

    def on_tick(self, context : Context):
        pass
    
    def on_stop(self, context : Context):
        pass

    @classmethod
    def get_parameters_schema(self):
        sig = inspect.signature(self.__init__)
        skip = {'self'}
        params = []
        for name, p in sig.parameters.items():
            if name in skip:
                continue
            default = p.default if p.default is not inspect.Parameter.empty else None
            params.append({
                "key": name,
                "label": name.replace('_', ' ').title(),
                "type": "float" if isinstance(default, float) else "int",
                "default": default,
            })
        return params

    def to_dict(self):
        params = self.get_parameters_schema()
        strategy_dict = {}
        for param in params:
            strategy_dict[param["key"]] = getattr(self, param["key"])
        return strategy_dict
