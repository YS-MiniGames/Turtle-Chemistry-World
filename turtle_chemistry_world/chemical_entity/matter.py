from dataclasses import dataclass, field

from typing import Iterable

from .substance import Substance, PhaseData
from .constant import (
    ENVIRONMENT_TEMPERATURE,
    HEAT_TRANSFER_CONSTANT,
    ENVIRONMENT_HEAT_TRANSFER_COEFFICIENT,
    CHEMICAL_SYSTEM_CLEAR_AMOUNT
)


@dataclass(eq=False)
class Matter:
    substance: Substance
    amount: float  # mol

    _phasedata: PhaseData | None = None
    _internal_energy: float | None = None
    _surface_area: float | None = None

    phasedata: PhaseData = field(init=False)
    internal_energy: float = field(init=False)  # J
    surface_area: float = field(init=False)  # m**2

    def __post_init__(self):
        if self._phasedata is not None:
            self.phasedata = self._phasedata
        else:
            self.phasedata = self.substance.default_phasedata

        if self._internal_energy is not None:
            self.internal_energy = self._internal_energy
        else:
            self.internal_energy = (
                self.phasedata.specific_heat * self.amount * ENVIRONMENT_TEMPERATURE
            )

        if self._surface_area is not None:
            self.surface_area = self._surface_area
        else:
            self.surface_area = (
                self.volume * self.phasedata.default_surface_area_multiplier
            )

    @property
    def phase(self):
        return self.phasedata.phase

    @property
    def density(self):
        return self.phasedata.density

    @property
    def specific_heat(self):
        return self.phasedata.specific_heat

    @property
    def heat_transfer_coefficient(self):
        return self.phasedata.heat_transfer_coefficient

    @property
    def relative_mass(self):
        return self.substance.relative_mass

    @property
    def chemical_energy(self):
        return self.substance.chemical_energy * self.amount

    @property
    def phase_energy(self):
        return self.phasedata.phase_energy * self.amount

    @property
    def energy(self):
        return self.chemical_energy + self.phase_energy + self.internal_energy

    @property
    def heat_capacity(self):
        return self.phasedata.specific_heat * self.amount

    @property
    def temperature(self):
        return self.internal_energy / self.heat_capacity

    @property
    def mass(self):
        return self.amount * self.relative_mass

    @property
    def volume(self):
        return self.mass / self.density

    @property
    def size(self) -> float:  # cm
        return self.volume ** (1 / 3)

    @property
    def external_surface_area(self):  # cm^2
        return self.size**2 * self.phasedata.external_surface_area_multiplier

    def add(self, other: "Matter"):
        self.amount += other.amount
        self.internal_energy += other.internal_energy
        self.surface_area += other.surface_area

    def remove(self, other: "Matter"):
        self.amount -= other.amount
        self.internal_energy -= other.internal_energy
        self.surface_area -= other.surface_area

    def split(self, amount: float) -> "Matter":
        ratio = amount / self.amount
        removed = Matter(
            self.substance,
            amount,
            self.phasedata,
            self.internal_energy * ratio,
            self.surface_area * ratio,
        )
        self.remove(removed)
        return removed

    def add_heat(self, heat: float):
        self.internal_energy += heat

    def transfer_heat(self, other: "Matter") -> float:
        delta_temperature = other.temperature - self.temperature
        heat_transfer_coefficient = (
            self.heat_transfer_coefficient * other.heat_transfer_coefficient
        ) ** 0.5
        surface_area = min(self.surface_area, other.surface_area)
        return (
            delta_temperature
            * heat_transfer_coefficient
            * surface_area
            * HEAT_TRANSFER_CONSTANT
        )

    def transfer_heat_environment(
        self, environment_temperature: float = ENVIRONMENT_TEMPERATURE
    ) -> float:
        delta_temperature = environment_temperature - self.temperature
        heat_transfer_coefficient = (
            self.heat_transfer_coefficient * ENVIRONMENT_HEAT_TRANSFER_COEFFICIENT
        ) ** 0.5
        surface_area = self.external_surface_area
        return (
            delta_temperature
            * heat_transfer_coefficient
            * surface_area
            * HEAT_TRANSFER_CONSTANT
        )

    @classmethod
    def tidy_matter_list(cls, matter_list: list["Matter"]):
        d: dict[PhaseData, Matter] = {}
        for matter in matter_list:
            if matter.amount < CHEMICAL_SYSTEM_CLEAR_AMOUNT:
                continue
            psubs = matter.phasedata
            if psubs not in d:
                d[psubs] = matter
            else:
                d[psubs].add(matter)
        matter_list.clear()
        matter_list.extend(d.values())

    @classmethod
    def avg_temperature(cls, matters: Iterable["Matter"]) -> float:
        total_internal_energy: float = 0.0
        total_heat_capacity: float = 0.0
        for matter in matters:
            total_internal_energy += matter.internal_energy
            total_heat_capacity += matter.heat_capacity
        return total_internal_energy / total_heat_capacity
