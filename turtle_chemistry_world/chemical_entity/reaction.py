from dataclasses import dataclass, field

from typing import Callable

import numpy

from .element import Element
from .substance import Substance
from .matter import Matter

type SpeedFunc = Callable[[float, "Reaction", dict[Substance, Matter]], float]


def speed_multiplier_factory(
    base: float = 1.0, min_temperature: float = -200.0, max_temperature: float = 1e6
) -> SpeedFunc:
    # base mol/s

    def speed_multiplier(
        tick: float, reaction: "Reaction", matters: dict[Substance, Matter]
    ) -> float:
        # tick时间内reaction进行的mol数
        multiplier = base * tick

        for reactant in reaction.left:
            if reactant not in matters:
                return 0.0
            if (
                matters[reactant].temperature < min_temperature
                or matters[reactant].temperature > max_temperature
            ):
                return 0.0
            multiplier *= matters[reactant].surface_area_multiplier

        for reactant, count in reaction.left.items():
            multiplier = min(multiplier, matters[reactant].amount / count)
        return multiplier

    return speed_multiplier


default_speed_multiplier = speed_multiplier_factory()


@dataclass(frozen=True, eq=False)
class Reaction:
    left: dict[Substance, float]
    right: dict[Substance, float]
    speed_multiplier: SpeedFunc = default_speed_multiplier
    chemical_energy: float = field(init=False)  # J/mol

    def __post_init__(self):
        chemical_energy = 0.0
        for substance, count in self.left.items():
            chemical_energy += substance.chemical_energy * count
        for substance, count in self.right.items():
            chemical_energy -= substance.chemical_energy * count
        object.__setattr__(self, "chemical_energy", chemical_energy)

    @classmethod
    def BalanceReaction(
        cls,
        *substances: Substance,
        speed_multiplier: SpeedFunc = default_speed_multiplier,
    ):
        if not substances:
            raise ValueError("Reaction cannot be empty")

        all_elements: set[Element] = set()
        for substance in substances:
            for element in substance.formula.element_count:
                all_elements.add(element)

        # left_li: 1,x1,x2,x3...
        # right_li: y1,y2,y3...
        # 1*cnt0+x1*cnt1+x2*cnt2+x3*cnt3...==y1*cntn+y2*cnt(n+1)+y3*cnt(n+2)
        mat_a: list[list[int]] = []
        vec_b: list[int] = []
        for element in all_elements:
            mat_a_newline: list[int] = []
            for i, substance in enumerate(substances):
                if i == 0:
                    vec_b.append(-substance.formula.element_count.get(element, 0))
                    continue
                mat_a_newline.append(substance.formula.element_count.get(element, 0))
            mat_a.append(mat_a_newline)

        mat_a_lastline: list[int] = []
        for i, substance in enumerate(substances):
            if i != 0:
                mat_a_lastline.append(substance.charge)
        if mat_a_lastline.count(0) != len(mat_a_lastline):
            mat_a.append(mat_a_lastline)
            vec_b.append(0)

        try:
            solution: list[float] = list(numpy.linalg.solve(mat_a, vec_b))
            solution.insert(0, 1)
            left: dict[Substance, float] = {}
            right: dict[Substance, float] = {}
            for sol, substance in zip(solution, substances):
                if sol > 0:
                    left[substance] = sol
                elif sol < 0:
                    right[substance] = -sol

            return Reaction(left, right, speed_multiplier)

        except numpy.linalg.LinAlgError as e:
            raise ValueError("The reaction cannot be balanced.") from e

    @classmethod
    def ReversedReaction(
        cls,
        reaction: "Reaction",
        speed_multiplier: SpeedFunc = default_speed_multiplier,
    ):
        return Reaction(reaction.right, reaction.left, speed_multiplier)
