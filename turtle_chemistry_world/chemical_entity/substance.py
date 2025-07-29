from dataclasses import dataclass, field
from enum import Enum

from typing import Final

from .formula import Formula


class State(Enum):
    GAS = 0
    LIQUID = 1
    SOLID = 2
    AQUA = 3
    G = 0
    L = 1
    S = 2
    AQ = 3


SPECIFIC_HEAT_CONSTANT: Final = 75.0


@dataclass(frozen=True, eq=False)
class Substance:
    formula: Formula
    density: float  # kg/m**3
    state: State = State.LIQUID
    energy: float = 0.0  # J/mol
    specific_heat: float = SPECIFIC_HEAT_CONSTANT
    heat_transfer_coefficient: float = 1.0  # W/(m**2*K)

    color:str="transparent"

    name: str | None = None
    charge: int = field(init=False)
    relative_mass: float = field(init=False)  # g/mol

    def __post_init__(self):
        object.__setattr__(self, "charge", self.formula.valence)
        object.__setattr__(self, "relative_mass", self.formula.relative_mass)

    def __repr__(self):
        if self.name is None:
            return super().__repr__()
        return self.name
