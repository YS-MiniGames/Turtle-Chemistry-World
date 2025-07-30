from dataclasses import dataclass, field

from typing import Final, Iterable

from .substance import Substance
from .matter import Matter
from .reaction import Reaction

AMOUNT_CLEAR: Final = 1e-12

MIN_SEE_VOLUME: Final = 1e-2


@dataclass(eq=False)
class MatterChange:
    add_matter: list[Matter] = field(default_factory=list)
    remove_matter: list[Matter] = field(default_factory=list)
    add_heat: list[tuple[Substance, float]] = field(default_factory=list)

    def extend(self, other: "MatterChange"):
        self.add_matter.extend(other.add_matter)
        self.remove_matter.extend(other.remove_matter)
        self.add_heat.extend(other.add_heat)


@dataclass(eq=False)
class ChemicalSystem:
    matters: dict[Substance, Matter]

    def reaction_process(self, reaction: Reaction, tick: float):
        multiplier = reaction.speed_multiplier(tick, reaction, self.matters)
        change = MatterChange()
        if multiplier == 0:
            return change

        total_energy = 0.0
        reaction_temperature = 0.0
        amount_sum = 0.0
        for substance, amount in reaction.left.items():
            amount *= multiplier
            # 有amount的substance被移除
            matter = self.matters[substance]
            reaction_temperature += matter.temperature * amount
            amount_sum += amount
            reactant_matter = Matter(
                substance, amount, matter.temperature, matter.surface_area_multiplier
            )
            total_energy += reactant_matter.energy
            change.remove_matter.append(reactant_matter)
        reaction_temperature /= amount_sum

        for substance, amount in reaction.right.items():
            amount *= multiplier
            matter = Matter(substance, amount, reaction_temperature)
            total_energy -= matter.energy
            change.add_matter.append(matter)

        matter_amount = 0.0
        for substance in reaction.left:
            matter_amount += self.matters[substance].amount
        for substance in reaction.left:
            change.add_heat.append(
                (
                    substance,
                    total_energy * self.matters[substance].amount / matter_amount,
                )
            )

        return change

    def apply_changes(self, change: MatterChange):
        for matter in change.add_matter:
            substance = matter.substance
            if substance not in self.matters:
                self.matters[substance] = matter
            else:
                self.matters[substance].merge(matter)
        for substance, heat in change.add_heat:
            self.matters[substance].add_heat(heat)
        for matter in change.remove_matter:
            substance = matter.substance
            self.matters[substance].remove(matter)
            if self.matters[substance].amount <= AMOUNT_CLEAR:
                self.matters.pop(substance)

    def transfer_heat(self, tick: float, environment_temperature: float | None):
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

    def run(
        self,
        reactions: Iterable[Reaction],
        tick: float = 0.01,
        environment_temperature: float | None = 20.0,
    ):
        change = MatterChange()
        for reaction in reactions:
            new_change = self.reaction_process(reaction, tick)
            change.extend(new_change)

        self.apply_changes(change)

        self.transfer_heat(tick, environment_temperature)
