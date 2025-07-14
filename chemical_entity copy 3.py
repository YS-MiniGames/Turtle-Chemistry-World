import copy
from dataclasses import dataclass

import typing
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

    def generate(self, element_table: ElementTable) -> "FormulaData":
        if self.relative_mass is not ...:
            return FormulaData(self.element_count, self.valence, self.relative_mass)
        for element, count in self.element_count.items():
            element_relative_mass_check = element_table.get_element(
                element
            ).relative_mass
            if element_relative_mass_check is None:
                return FormulaData(self.element_count, self.valence, None)
        new_relative_mass: float = 0.0
        for element, count in self.element_count.items():
            element_relative_mass: float = typing.cast(
                float, element_table.get_element(element).relative_mass
            )
            new_relative_mass += element_relative_mass * count
        return FormulaData(self.element_count, self.valence, new_relative_mass)

    def merge(self, other: "FormulaData"):
        new_element_count = self.element_count
        for element, count in other.element_count.items():
            if element in new_element_count:
                new_element_count[element] += count
            else:
                new_element_count[element] = count
        new_valence: int | None = None
        if self.valence is not None and other.valence is not None:
            new_valence = self.valence + other.valence
        new_relative_mass: float | None | EllipsisType = None
        if self.relative_mass is None or other.relative_mass is None:
            new_relative_mass = None
        elif self.relative_mass is ... or other.relative_mass is ...:
            new_relative_mass = ...
        else:
            new_relative_mass = self.relative_mass + other.relative_mass
        return FormulaData(new_element_count, new_valence, new_relative_mass)

    def __add__(self, other: "FormulaData") -> "FormulaData":
        return self.merge(other)
    
