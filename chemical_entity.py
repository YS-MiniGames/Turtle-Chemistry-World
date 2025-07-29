import math
from dataclasses import dataclass, field
from enum import Enum
import numpy

from typing import Iterable, Final


@dataclass(frozen=True, eq=False)
class Element:
    relative_mass: float


@dataclass(frozen=True, eq=False)
class Formula:
    element_count: dict[Element, int]
    valence: int
    relative_mass: float = field(init=False)

    def __post_init__(self):
        relative_mass: float = 0.0
        for element, count in self.element_count.items():
            relative_mass += element.relative_mass * count
        object.__setattr__(self, "relative_mass", relative_mass)

    def __mul__(self, t: int):
        element_count = {
            element: count * t for element, count in self.element_count.items()
        }
        return Formula(element_count, self.valence * t)

    def __add__(self, other: "Formula"):
        element_count = self.element_count.copy()
        for element, count in other.element_count.items():
            if element in element_count:
                element_count[element] += count
            else:
                element_count[element] = count
        return Formula(element_count, self.valence + other.valence)

    def __and__(self, other: "Formula"):
        if self.valence * other.valence >= 0:
            raise ValueError("Cannot combine formulas with different valence signs")
        valence_lcm = math.lcm(self.valence, other.valence)
        t1 = valence_lcm // abs(self.valence)
        t2 = valence_lcm // abs(other.valence)
        return self * t1 + other * t2


class State(Enum):
    G = 0
    L = 1
    S = 2
    AQ = 3


@dataclass(frozen=True, eq=False)
class Substance:
    formula: Formula
    state: State
    density: float  # kg/m**3
    name: str | None = None
    charge: int = field(init=False)
    relative_mass: float = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "charge", self.formula.valence)
        object.__setattr__(self, "relative_mass", self.formula.relative_mass)

    def __repr__(self):
        if self.name is None:
            return super().__repr__()
        return self.name


@dataclass(frozen=True, eq=False)
class Reaction:
    left: dict[Substance, float]
    right: dict[Substance, float]

    @classmethod
    def BalanceReaction(cls, *substances: Substance):
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

            return Reaction(left, right)

        except numpy.linalg.LinAlgError as e:
            raise ValueError("The reaction cannot be balanced.") from e

    @classmethod
    def ReversedReaction(cls, reaction: "Reaction"):
        return Reaction(reaction.right, reaction.left)


@dataclass(eq=False)
class Matter:
    substance: Substance
    amount: float
    # temperature: float


AMOUNT_CLEAR: Final = 1e-10


@dataclass(eq=False)
class System:
    matters: dict[Substance, Matter]

    def reaction_multiplier(self, reaction: Reaction, tick: float):
        multiplier = tick
        for reactant, count in reaction.left.items():
            if reactant not in self.matters:
                return 0
            multiplier = min(multiplier, self.matters[reactant].amount / count)
        return multiplier

    def reaction_handler(self, reaction: Reaction, multiplier: float):
        change: list[tuple[Substance, float]] = []
        for reactant, count in reaction.left.items():
            change.append((reactant, -count * multiplier))
        for product, count in reaction.right.items():
            change.append((product, count * multiplier))
        return change

    def simulate(self, reactions: Iterable[Reaction], tick: float = 0.01):
        """模拟反应。

        Args:
            reactions (Iterable[Reaction]): 要模拟的反应
            tick (float, optional): 每次模拟的间隔时间。默认为0.01
        """
        change: list[tuple[Substance, float]] = []
        for reaction in reactions:
            multiplier = self.reaction_multiplier(reaction, tick)
            if multiplier == 0:
                continue
            change.extend(self.reaction_handler(reaction, multiplier))

        for substance, amount in change:
            if substance not in self.matters:
                self.matters[substance] = Matter(substance, amount)
                continue
            self.matters[substance].amount += amount
            if self.matters[substance].amount <= AMOUNT_CLEAR:
                self.matters.pop(substance)
