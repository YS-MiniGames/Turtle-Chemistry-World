from dataclasses import dataclass

from .substance import Substance

HEAT_TRANSFER_CONSTANT = 1e3


@dataclass(eq=False)
class Matter:
    substance: Substance
    amount: float

    temperature: float = 20.0
    surface_area_multiplier: float = 1.0

    @property
    def internal_energy(self):  # J
        return self.amount * self.temperature * self.substance.specific_heat

    @property
    def chemical_energy(self):  # J
        return self.amount * self.substance.chemical_energy

    @property
    def energy(self):
        return self.internal_energy + self.chemical_energy

    @property
    def mass(self):  # kg
        return self.amount * self.substance.relative_mass / 1000

    @property
    def volume(self):  # m**3
        return self.mass / self.substance.density

    def merge(self, other: "Matter"):
        if other.substance != self.substance:
            raise ValueError("Cannot merge different substances")

        amount = self.amount + other.amount
        if self.temperature != other.temperature:
            internal_energy = self.internal_energy + other.internal_energy
            self.temperature = internal_energy / (amount * self.substance.specific_heat)
        self.amount = amount

    def remove(self, other: "Matter"):
        if other.substance != self.substance:
            raise ValueError("Cannot merge different substances")

        amount = self.amount - other.amount
        if amount <= 0:
            self.amount = 0
            return

        if self.temperature != other.temperature:
            internal_energy = self.internal_energy - other.internal_energy
            self.temperature = internal_energy / (amount * self.substance.specific_heat)
        self.amount = amount

    def add_heat(self, heat: float):
        if heat == 0:
            return
        self.temperature += heat / (self.amount * self.substance.specific_heat)

    def transfer_heat(self, tick: float, other: "Matter") -> float:
        delta_temperature = self.temperature - other.temperature
        area = min(
            self.surface_area_multiplier * self.volume,
            other.surface_area_multiplier * other.volume,
        )
        coefficient = (
            self.substance.heat_transfer_coefficient
            * other.substance.heat_transfer_coefficient
        ) ** 0.5
        return coefficient * area * delta_temperature * tick * HEAT_TRANSFER_CONSTANT

    def transfer_heat_environment(
        self, tick: float, environment_temperature: float
    ) -> float:
        delta_temperature = self.temperature - environment_temperature
        area = self.surface_area_multiplier * self.volume
        coefficient = self.substance.heat_transfer_coefficient
        return coefficient * area * delta_temperature * tick * HEAT_TRANSFER_CONSTANT
