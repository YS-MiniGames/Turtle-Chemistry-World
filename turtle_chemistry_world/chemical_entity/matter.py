from dataclasses import dataclass

from .substance import Substance, State


@dataclass(eq=False)
class Matter:
    substance: Substance
    amount: float
    temperature: float = 20.0
    surface_area_multiplier: float = 1.0

    @property
    def heat(self):
        return self.amount * self.temperature * self.substance.specific_heat

    @property
    def mass(self):  # kg
        return self.amount * self.substance.relative_mass / 1000

    @property
    def volume(self):
        return self.mass / self.substance.density

    def merge(self, other: "Matter"):
        if other.substance != self.substance:
            raise ValueError("Cannot add different substances")

        total_amount = self.amount + other.amount
        if self.temperature != other.temperature:
            energy = self.heat + other.heat
            self.temperature = energy / (total_amount * self.substance.specific_heat)
        self.amount = total_amount

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
        )
        return coefficient * area * delta_temperature * tick

    def transfer_heat_environment(
        self, tick: float, environment_temperature: float
    ) -> float:
        delta_temperature = self.temperature - environment_temperature
        area = self.surface_area_multiplier * self.volume
        coefficient = self.substance.heat_transfer_coefficient
        coefficient **= 2
        return coefficient * area * delta_temperature * tick

    def check(self) -> tuple[str, float]:
        result: list[str] = []

        result.append(self.substance.color)
        result.append(" ")
        if self.substance.state == State.LIQUID:
            result.append("liquid")
        elif self.substance.state == State.GAS:
            result.append("gas")
        elif self.substance.state == State.SOLID:
            result.append("soild")

        return "".join(result), self.volume * 1e6
