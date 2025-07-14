"""化学实体模块，提供元素、公式和反应数据结构的实现。

该模块包含以下主要组件:
- ElementRef/FormulaRef/ReactionRef: 引用标识符类
- ElementData/FormulaData/ReactionData: 基础数据类
- ElementTable/FormulaTable/ReactionTable: 容器类

模块提供了完整的元素、公式和反应的存储、检索和管理功能。
"""

import copy
from dataclasses import dataclassfrom collections import Counter


from typing import Iterable, SupportsIndex
from types import EllipsisType


@dataclass(frozen=True)
class ElementRef:
    """元素的引用标识符，用于在元素表中索引元素。

    属性:
        index: 元素在元素表中的索引位置
    """

    index: int

    def __index__(self):
        """支持将ElementRef直接用作索引。

        返回:
            元素的索引值
        """
        return self.index


@dataclass(frozen=True)
class ElementData:
    """元素的基础数据类，存储元素的物理化学属性。

    属性:
        relative_mass: 元素的相对质量，可选
        valence: 元素的化合价，可选
    """

    relative_mass: float | None = None
    valence: int | None = None

    def generate(self, *_) -> "ElementData":
        """生成元素的深拷贝副本。

        参数:
            _: 忽略的参数

        返回:
            元素数据的新副本
        """
        other = copy.deepcopy(self)
        return other


class ElementTable:
    """元素表容器类，用于存储和管理元素数据。

    属性:
        element_list: 存储元素数据的列表
    """

    element_list: list[ElementData]

    def __init__(self, initial: Iterable[ElementData] | EllipsisType = ...) -> None:
        """初始化元素表。

        参数:
            initial: 初始元素集合，默认为空表
        """
        if initial is ...:
            self.element_list = []
            return
        self.element_list = list(initial)

    def add_element(self, element_data: ElementData) -> ElementRef:
        """向元素表中添加新元素。

        参数:
            element_data: 要添加的元素数据

        返回:
            新元素的引用标识符
        """
        self.element_list.append(element_data.generate(self))
        return ElementRef(len(self.element_list) - 1)

    def get_element(self, index: SupportsIndex) -> ElementData:
        """获取指定索引位置的元素。

        参数:
            index: 元素索引

        返回:
            索引对应的元素数据
        """
        return self.element_list[index]

    def __repr__(self) -> str:
        """生成元素表的可打印表示。

        返回:
            包含所有元素及其索引的格式化字符串
        """
        result = ["ElementTable(\n"]
        for i, v in enumerate(self.element_list):
            result.append(f"\t{i}: {v}\n")
        result.append(")")
        return "".join(result)


@dataclass(frozen=True)
class FormulaRef:
    """公式的引用标识符，用于在公式表中索引公式。

    属性:
        index: 公式在公式表中的索引位置
    """

    index: int

    def __index__(self):
        """支持将FormulaRef直接用作索引.

        返回:
            公式的索引值
        """
        return self.index


@dataclass(frozen=True)
class FormulaComponentPart:
    data: "ElementRef | FormulaComponent"
    count: int = 1
    element_count: dict[ElementRef, int] | EllipsisType = ...

    def __post_init__(self):
        if isinstance(self.data, ElementRef):
            setattr(self, "element_count", {self.data: self.count})
            return
        object.__setattr__(
            self,
            "element_count",
            {i: v * self.count for i, v in self.data.element_count.items()},
        )


@dataclass(frozen=True)
class FormulaComponent:
    parts: list[FormulaComponentPart]
    element_count: dict[ElementRef, int] | EllipsisType = ...

    def __post_init__(self):
        element_count = {}
        for part in self.parts:
            for element, count in part.element_count.items():
                element_count[element] = element_count.get(element, 0) + count
        object.__setattr__(self, "element_count", element_count)


@dataclass(frozen=True)
class FormulaData:
    """公式的基础数据类，存储公式的组成和属性。

    属性:
        components: 公式的组成元素 例：()
    """

    component: FormulaComponent
    valence: int | None = None
    element_count: dict[ElementRef, int] | EllipsisType = ...

    def generate(self, *_) -> "FormulaData":
        """生成公式的深拷贝副本.

        参数:
            _: 忽略的参数

        返回:
            公式数据的新副本
        """
        other = copy.deepcopy(self)
        return other


class FormulaTable:
    """公式表容器类，用于存储和管理公式数据。

    属性:
        formula_list: 存储公式数据的列表
    """

    formula_list: list[FormulaData]

    def __init__(self, initial: Iterable[FormulaData] | EllipsisType = ...) -> None:
        """初始化公式表.

        参数:
            initial: 初始公式集合，默认为空表
        """
        if initial is ...:
            self.formula_list = []
            return
        self.formula_list = list(initial)

    def add_formula(self, formula_data: FormulaData) -> FormulaRef:
        """向公式表中添加新公式.

        参数:
            formula_data: 要添加的公式数据

        返回:
            新公式的引用标识符
        """
        self.formula_list.append(formula_data.generate(self))
        return FormulaRef(len(self.formula_list) - 1)

    def get_formula(self, index: SupportsIndex) -> FormulaData:
        """获取指定索引位置的公式.

        参数:
            index: 公式索引

        返回:
            索引对应的公式数据
        """
        return self.formula_list[index]

    def __repr__(self) -> str:
        """生成公式表的可打印表示.

        返回:
            包含所有公式及其索引的格式化字符串
        """
        result = ["FormulaTable(\n"]
        for i, v in enumerate(self.formula_list):
            result.append(f"\t{i}: {v}\n")
        result.append(")")
        return "".join(result)


@dataclass(frozen=True)
class ReactionRef:
    """反应的引用标识符，用于在反应表中索引反应。

    属性:
        index: 反应在反应表中的索引位置
    """

    index: int

    def __index__(self):
        """支持将ReactionRef直接用作索引.

        返回:
            反应的索引值
        """
        return self.index


@dataclass
class ReactionData:
    """反应的基础数据类，存储反应方程式和属性。

    属性:
        reactants: 反应物及其系数
        products: 生成物及其系数
        energy_change: 反应的能量变化，可选
    """

    reactants: dict[FormulaRef, int]
    products: dict[FormulaRef, int]
    energy_change: float | None = None

    def generate(self, *_) -> "ReactionData":
        """生成反应的深拷贝副本.

        参数:
            _: 忽略的参数

        返回:
            反应数据的新副本
        """
        other = copy.deepcopy(self)
        return other


class ReactionTable:
    """反应表容器类，用于存储和管理反应数据。

    属性:
        reaction_list: 存储反应数据的列表
    """

    reaction_list: list[ReactionData]

    def __init__(self, initial: Iterable[ReactionData] | EllipsisType = ...) -> None:
        """初始化反应表.

        参数:
            initial: 初始反应集合，默认为空表
        """
        if initial is ...:
            self.reaction_list = []
            return
        self.reaction_list = list(initial)

    def add_reaction(self, reaction_data: ReactionData) -> ReactionRef:
        """向反应表中添加新反应.

        参数:
            reaction_data: 要添加的反应数据

        返回:
            新反应的引用标识符
        """
        self.reaction_list.append(reaction_data.generate(self))
        return ReactionRef(len(self.reaction_list) - 1)

    def get_reaction(self, index: SupportsIndex) -> ReactionData:
        """获取指定索引位置的反应.

        参数:
            index: 反应索引

        返回:
            索引对应的反应数据
        """
        return self.reaction_list[index]

    def __repr__(self) -> str:
        """生成反应表的可打印表示.

        返回:
            包含所有反应及其索引的格式化字符串
        """
        result = ["ReactionTable(\n"]
        for i, v in enumerate(self.reaction_list):
            result.append(f"\t{i}: {v}\n")
        result.append(")")
        return "".join(result)
