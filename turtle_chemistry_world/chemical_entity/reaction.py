from dataclasses import dataclass, field

from typing import Callable

import numpy

from .element import Element
from .substance import Substance

type SpeedFunc = Callable[..., float]


def speed_multiplier_generator(
    base: float = 1.0, min_temperature: float = -100.0
) -> SpeedFunc:
    def speed_multiplier(**kwargs) -> float:
        temperature = kwargs.get("temperature", 20.0)
        if temperature < min_temperature:
            return 0.0
        return base

    return speed_multiplier


default_speed_multiplier = speed_multiplier_generator()


@dataclass(frozen=True, eq=False)
class Reaction:
    left: dict[Substance, float]
    right: dict[Substance, float]
    speed_multiplier: SpeedFunc = default_speed_multiplier
    energy: float = field(init=False)

    def __post_init__(self):
        energy = 0.0
        for substance, count in self.left.items():
            energy += substance.energy * count
        for substance, count in self.right.items():
            energy -= substance.energy * count
        object.__setattr__(self, "energy", energy)

    @classmethod
    def BalanceReaction(cls, *substances: Substance, **kwargs):
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

            return Reaction(left, right, **kwargs)

        except numpy.linalg.LinAlgError as e:
            raise ValueError("The reaction cannot be balanced.") from e

    @classmethod
    def ReversedReaction(
        cls,
        reaction: "Reaction",
        speed_multiplier: SpeedFunc = default_speed_multiplier,
    ):
        return Reaction(reaction.right, reaction.left, speed_multiplier)
