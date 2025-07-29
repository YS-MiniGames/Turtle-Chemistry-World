import math
from dataclasses import dataclass, field

from .element import Element


@dataclass(frozen=True, eq=False)
class Formula:
    element_count: dict[Element, int]
    valence: int = 0
    relative_mass: float = field(init=False)  # g/mol

    def __post_init__(self) -> None:
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
