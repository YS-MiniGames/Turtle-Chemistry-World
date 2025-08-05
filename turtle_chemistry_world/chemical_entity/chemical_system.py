from dataclasses import dataclass, field

from .substance import Substance
from .matter import Matter
from .reaction import Reaction

from .constant import (
    ENVIRONMENT_TEMPERATURE,
    DEFAULT_TICK_TIME,
    CHEMICAL_SYSTEM_CLEAR_AMOUNT,
)


@dataclass(eq=False)
class ChemicalSystem:
    matters: dict[Substance, list[Matter]] = field(default_factory=dict)
    environment_temperature: float | None = ENVIRONMENT_TEMPERATURE

    def transfer_heat(self, tick_time: float):
        gen = list(m for li in self.matters.values() for m in li)
        heat = []
        for m1 in gen:
            h = 0.0
            for m2 in gen:
                if m1 is m2:
                    continue
                h += m1.transfer_heat(m2) * tick_time
            if self.environment_temperature is not None:
                h += (
                    m1.transfer_heat_environment(self.environment_temperature)
                    * tick_time
                )
            heat.append(h)

        for m1, h in zip(gen, heat):
            m1.add_heat(h)

    def final_tidy(self):
        rm = []
        for s, ml in self.matters.items():
            if not ml:
                rm.append(s)
            Matter.tidy_matter_list(ml)
        for s in rm:
            self.matters.pop(s)

    def run(self, reactions: list[Reaction], tick_time: float = DEFAULT_TICK_TIME):
        for reaction in reactions:
            amount = reaction.get_amount(self.matters, tick_time)
            reaction.run(self.matters, amount)

        self.transfer_heat(tick_time)

        self.final_tidy()
        
    @property
    def avg_temperature(self) -> float:
        """计算平均温度"""
        return Matter.avg_temperature(m for ml in self.matters.values() for m in ml)
