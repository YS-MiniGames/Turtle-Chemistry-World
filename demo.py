import random

from chemical_entity import (
    ElementRef,
    ElementData,
    ElementTable,
    FormulaRef,
    FormulaData,
    FormulaTable,
)

random.seed(0)

elements = ElementTable()
metal: list[ElementRef] = []
non_metal: list[ElementRef] = []
for i in range(10):
    ref = elements.add_element(ElementData(random.randint(1, 100)))
    metal.append(ref)
for i in range(10):
    ref = elements.add_element(ElementData(random.randint(1, 100)))
    non_metal.append(ref)

formulas = FormulaTable(elements)
# gen valence
metal_valence: list[FormulaRef] = []
non_metal_valence: list[FormulaRef] = []
for ele in metal:
    li = [1, 2, 3]
    random.shuffle(li)
    for i in li[: random.randint(1, len(li))]:
        fref = formulas.add_formula(FormulaData({ele: 1}, i))
        metal_valence.append(fref)
for ele in non_metal:
    li = [-1, -2, -3]
    random.shuffle(li)
    for i in li[: random.randint(1, len(li))]:
        fref = formulas.add_formula(FormulaData({ele: 1}, i))
        non_metal_valence.append(fref)

compound: list[FormulaRef] = []
compound_generate: list[tuple[FormulaRef, FormulaRef]] = []
for i in range(10):
    for j in range(10):
        compound_generate.append(
            (random.choice(metal_valence), random.choice(non_metal_valence))
        )
compound_generate = list(set(compound_generate))
for form1, form2 in compound_generate:
    fref = formulas.add_formula(
        formulas.get_formula(form1)&formulas.get_formula(form2)
    )
    compound.append(fref)

print(compound)
print(formulas)
