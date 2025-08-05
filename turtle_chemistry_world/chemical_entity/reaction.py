from dataclasses import dataclass
from itertools import chain

import numpy

from .element import Element
from .substance import Substance
from .matter import Matter

from .constant import REACTION_SPEED_MULTIPLIER


@dataclass(eq=False)
class ReactionChange:
    add_matter: list[Matter]
    remove_matter: list[Matter]
    add_heat: list[tuple[Substance, float]]

    def extend(self, other: "ReactionChange"):
        self.add_matter.extend(other.add_matter)
        self.remove_matter.extend(other.remove_matter)
        self.add_heat.extend(other.add_heat)


@dataclass(frozen=True, eq=False)
class Reaction:
    left: dict[Substance, float]
    right: dict[Substance, float]

    base_speed: float = 1.0  # mol/s
    min_temperature: float | None = None  # K
    max_temperature: float | None = None  # K

    def get_speed(self, matters: dict[Substance, list[Matter]]) -> float:  # mol/s
        # debug=list(matter for substance in self.left for matter in matters[substance])
        for substance in self.left:
            if substance not in matters:
                return 0.0
        
        avgt = Matter.avg_temperature(
            matter for substance in self.left for matter in matters[substance]
        )
        
        if ((self.min_temperature is not None) and (avgt < self.min_temperature)) or (
            (self.max_temperature is not None) and (avgt > self.max_temperature)
        ):
            return 0.0

        speed: float = self.base_speed * REACTION_SPEED_MULTIPLIER

        reactant_surface_area_list: list[float] = [
            sum(matter.surface_area for matter in matters[substance])
            for substance in self.left
        ]
        reactant_surface_area = min(reactant_surface_area_list)
        speed *= reactant_surface_area
        speed *= avgt

        return speed

    def get_amount(self, matters: dict[Substance, list[Matter]], tick_time: float):
        amount = self.get_speed(matters) * tick_time
        if amount <= 0.0:
            return 0.0
        for substance, count in self.left.items():
            if substance not in matters:
                return 0.0
            amount = min(
                amount, sum(matter.amount for matter in matters[substance]) / count
            )
        return amount

    def run(self, matters: dict[Substance, list[Matter]], amount: float) -> None:
        if amount <= 0.0:
            return

        reactant_avgt = Matter.avg_temperature(
            matter for substance in self.left for matter in matters[substance]
        )

        energy: float = 0.0
        for substance, count in self.left.items():
            total_amount = sum(matter.amount for matter in matters[substance])
            reactant_amount = amount * count
            for matter in matters[substance]:
                splitted_matter = matter.split(
                    reactant_amount * matter.amount / total_amount
                )
                energy += splitted_matter.energy

        for substance, count in self.right.items():
            if substance in matters:
                total_amount = sum(matter.amount for matter in matters[substance])
                product_amount = amount * count
                for matter in matters[substance]:
                    a = product_amount * matter.amount / total_amount
                    add_matter = Matter(
                        substance,
                        a,
                        matter.phasedata,
                        matter.specific_heat * a * matter.temperature,
                    )
                    matter.add(add_matter)
                    energy -= add_matter.energy
            else:
                product_amount = amount * count
                add_matter = Matter(
                    substance,
                    product_amount,
                    substance.default_phasedata,
                    substance.default_phasedata.specific_heat
                    * product_amount
                    * reactant_avgt,
                )
                matters[substance] = [add_matter]
                energy -= add_matter.energy

        for substance in self.left:
            Matter.tidy_matter_list(matters[substance])
        for substance in self.right:
            Matter.tidy_matter_list(matters[substance])

        total_amount = sum(
            matter.amount * count
            for substance, count in chain(self.left.items(), self.right.items())
            for matter in matters[substance]
        )
        for substance, count in chain(self.left.items(), self.right.items()):
            for matter in matters[substance]:
                ratio = matter.amount * count / total_amount
                matter.add_heat(energy * ratio)

    @classmethod
    def Balance(cls, *substances: Substance):
        if not substances:
            raise ValueError("反应物与生成物不能为空")

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

            return left, right

        except numpy.linalg.LinAlgError as e:
            raise ValueError("无法平衡方程式") from e

    @classmethod
    def Reverse(cls, reaction: "Reaction"):
        return reaction.right, reaction.left
