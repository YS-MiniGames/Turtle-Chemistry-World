from dataclasses import dataclass
from enum import Enum

from .formula import Formula
from .constant import SPECIFIC_HEAT_CONSTANT


class Phase(Enum):
    GAS = 0
    LIQUID = 1
    SOLID = 2
    AQUA = 3
    G = 0
    L = 1
    S = 2
    AQ = 3


@dataclass(frozen=True, eq=False)
class PhaseData:
    phase: Phase = Phase.SOLID

    phase_energy: float = 0.0  # J/mol

    density: float = 1.0  # g/cm**3
    specific_heat: float = SPECIFIC_HEAT_CONSTANT  # J/(mol*K)
    heat_transfer_coefficient: float = 1.0  # W/(m**2*K)

    default_surface_area_multiplier: float = 1.0
    external_surface_area_multiplier: float = 6.0


@dataclass(frozen=True, eq=False, unsafe_hash=True)
class Substance:
    """纯净物，表示一种物质分子共有特性的类
    即一个Formula对应一个Substance"""

    formula: Formula
    default_phasedata: PhaseData
    chemical_energy: float = 0.0  # J/mol

    name: str | None = None

    @property
    def charge(self):
        return self.formula.valence

    @property
    def relative_mass(self):
        return self.formula.relative_mass

    def __repr__(self):
        if self.name is None:
            return f"Substance({id(self)})"
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Substance):
            return False
        return self.formula == other.formula
