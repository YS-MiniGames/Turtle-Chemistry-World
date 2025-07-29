from dataclasses import dataclass

from typing import Final, Iterable

from .substance import Substance
from .matter import Matter
from .reaction import Reaction

AMOUNT_CLEAR: Final = 1e-10

MIN_SEE_VOLUME: Final = 1e-2


@dataclass(eq=False)
class ChemicalSystem:
    matters: dict[Substance, Matter]

    def reaction_multiplier(self, reaction: Reaction, tick: float):
        multiplier = tick * reaction.speed_multiplier(reaction, self.matters)
        return multiplier

    def reaction_handler(self, reaction: Reaction, multiplier: float):
        change: list[tuple[Substance, Matter]] = []

        heat = 0.0
        for reactant, count in reaction.left.items():
            current_matter = self.matters[reactant]
            change_matter = Matter(
                reactant, -count * multiplier, current_matter.temperature
            )
            heat -= change_matter.heat
            change.append((reactant, change_matter))

        heat += reaction.energy * multiplier

        product_specific_heat = 0.0
        for product, count in reaction.right.items():
            product_specific_heat += product.specific_heat * count * multiplier
        product_temperature = heat / product_specific_heat
        for product, count in reaction.right.items():
            change_matter = Matter(product, count * multiplier, product_temperature)
            change.append((product, change_matter))
        return change

    def apply_changes(self, change: list[tuple[Substance, Matter]]):
        for substance, matter in change:
            if substance not in self.matters:
                self.matters[substance] = matter
            else:
                self.matters[substance].merge(matter)

            if self.matters[substance].amount <= AMOUNT_CLEAR:
                self.matters.pop(substance)

    def transfer_heat(self, tick: float, environment_temperature):
        heat: dict[Substance, float] = {}
        for substance, matter in self.matters.items():
            heat[substance] = 0
            for other_substance, other_matter in self.matters.items():
                if substance == other_substance:
                    continue
                heat[substance] += matter.transfer_heat(tick, other_matter)
            if environment_temperature is not None:
                heat[substance] += matter.transfer_heat_environment(
                    tick, environment_temperature
                )
        for substance, h in heat.items():
            self.matters[substance].add_heat(-h)

    def simulate(
        self,
        reactions: Iterable[Reaction],
        tick: float = 0.01,
        environment_temperature: float | None = 20.0,
    ):
        change: list[tuple[Substance, Matter]] = []
        for reaction in reactions:
            multiplier = self.reaction_multiplier(reaction, tick)
            if multiplier == 0:
                continue
            change.extend(self.reaction_handler(reaction, multiplier))

        self.apply_changes(change)

        self.transfer_heat(tick, environment_temperature)

    def check(self) -> str:
        result: dict[str, float] = {}
        for matter in self.matters.values():
            desc, volume = matter.check()
            result[desc] = result.get(desc, 0) + volume
        str_list: list[str] = []
        for desc, volume in result.items():
            if volume < MIN_SEE_VOLUME:
                continue
            str_list.append(desc)
            if volume <= 1:
                str_list.append("a little")
                continue
            str_list.append(": about ")
            str_list.append(str(round(volume / 5) * 5))
            str_list.append("mL")
            str_list.append("\n")
        str_list.pop()
        return "".join(str_list)
