import math
from dataclasses import dataclass

from typing import Iterable, SupportsIndex
from types import EllipsisType


@dataclass(frozen=True)
class ElementRef:
    index: int

    def __index__(self):
        return self.index


@dataclass(frozen=True)
class ElementData:
    relative_mass: float | None = None

    def generate(self) -> "ElementData":
        return ElementData(self.relative_mass)


class ElementTable:
    element_list: list[ElementData]

    def __init__(self, initial: Iterable[ElementData] | EllipsisType = ...) -> None:
        if initial is ...:
            self.element_list = []
            return
        self.element_list = list(initial)

    def add_element(self, element_data: ElementData) -> ElementRef:
        self.element_list.append(element_data.generate())
        return ElementRef(len(self.element_list) - 1)

    def get_element(self, index: SupportsIndex) -> ElementData:
        return self.element_list[index]

    def __repr__(self) -> str:
        result = ["ElementTable(\n"]
        for i, v in enumerate(self.element_list):
            result.append(f"\t{i}: {v}\n")
        result.append(")")
        return "".join(result)


@dataclass(frozen=True)
class FormulaRef:
    index: int

    def __index__(self):
        return self.index


@dataclass(frozen=True)
class FormulaData:
    element_count: dict[ElementRef, int]
    valence: int | None = None
    relative_mass: float | None | EllipsisType = ...

    def generate(self, element_table: ElementTable | None) -> "FormulaData":
        if self.relative_mass is not ...:
            return FormulaData(self.element_count, self.valence, self.relative_mass)
        if element_table is None:
            return FormulaData(self.element_count, self.valence, None)

        new_relative_mass: float = 0.0
        for element, count in self.element_count.items():
            element_relative_mass = element_table.get_element(element).relative_mass
            if element_relative_mass is None:
                return FormulaData(self.element_count, self.valence, None)
            new_relative_mass += element_relative_mass * count
        return FormulaData(self.element_count, self.valence, new_relative_mass)

    def merge(self, other: "FormulaData"):
        new_element_count = self.element_count
        for element, count in other.element_count.items():
            if element in new_element_count:
                new_element_count[element] += count
            else:
                new_element_count[element] = count

        new_valence: int | None
        if self.valence is None or other.valence is None:
            new_valence = None
        else:
            new_valence = self.valence + other.valence

        new_relative_mass: float | None | EllipsisType
        if self.relative_mass is None or other.relative_mass is None:
            new_relative_mass = None
        elif self.relative_mass is ... or other.relative_mass is ...:
            new_relative_mass = ...
        else:
            new_relative_mass = self.relative_mass + other.relative_mass
        return FormulaData(new_element_count, new_valence, new_relative_mass)

    def __add__(self, other: "FormulaData") -> "FormulaData":
        return self.merge(other)

    def __mul__(self, t: int) -> "FormulaData":
        new_element_count = {
            element: count * t for element, count in self.element_count.items()
        }

        new_valence: int | None
        if self.valence is None:
            new_valence = None
        else:
            new_valence = self.valence * t

        new_relative_mass: float | None | EllipsisType
        if self.relative_mass is None or self.relative_mass is ...:
            new_relative_mass = self.relative_mass
        else:
            new_relative_mass = self.relative_mass * t
        return FormulaData(new_element_count, new_valence, new_relative_mass)

    def balance_merge(self, other: "FormulaData") -> "FormulaData":
        if (
            self.valence is None
            or self.valence is ...
            or other.valence is None
            or other.valence is ...
        ):
            raise ValueError("Cannot balance merge formulas with unknown valence")
        if self.valence * other.valence >= 0:
            raise ValueError("Cannot balance merge formulas with same valence signs")
        valence_lcm = math.lcm(self.valence, other.valence)
        t1 = valence_lcm // abs(self.valence)
        t2 = valence_lcm // abs(other.valence)
        return self * t1 + other * t2

    def __and__(self, other: "FormulaData") -> "FormulaData":
        return self.balance_merge(other)


class FormulaTable:
    formula_list: list[FormulaData]
    element_table: ElementTable | None

    def __init__(
        self,
        element_table: ElementTable | None = None,
        initial: Iterable[FormulaData] | EllipsisType = ...,
    ) -> None:
        self.element_table = element_table
        if initial is ...:
            self.formula_list = []
            return
        self.formula_list = list(initial)

    def bind_element_table(self, element_table: ElementTable) -> None:
        self.element_table = element_table

    def add_formula(
        self, formula_data: FormulaData, element_table: ElementTable | None = None
    ) -> FormulaRef:
        new_formula: FormulaData
        if element_table is None:
            new_formula = formula_data.generate(self.element_table)
        else:
            new_formula = formula_data.generate(element_table)
        self.formula_list.append(new_formula)
        return FormulaRef(len(self.formula_list) - 1)

    def get_formula(self, index: SupportsIndex) -> FormulaData:
        return self.formula_list[index]

    def __repr__(self) -> str:
        result = ["FormulaTable(\n"]
        for i, v in enumerate(self.formula_list):
            result.append(f"\t{i}: {v}\n")
        result.append(")")
        return "".join(result)
    
    


