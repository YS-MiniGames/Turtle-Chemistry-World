import random

from chemical_entity import (
    Element,
    Formula,
)

random.seed(0)

elements: list[tuple[Element, tuple[str, ...]]] = []

N: int

N = random.randint(10, 30)
for i in range(N):
    E = Element(random.randint(20, 130))
    elements.append((E, ("metal",)))
N = random.randint(10, 30)
for i in range(N):
    E = Element(random.randint(10, 60))
    tags_li: list[str] = ["nonmetal"]
    if random.randint(1, 4) == 1:
        tags_li.append("halogen")
    if E.relative_mass - 20 <= abs(random.normalvariate(0, 15)):
        tags_li.append("gas")
    elements.append((E, tuple(tags_li)))

formulas: list[tuple[Formula, tuple[str, ...]]] = []
formula_metal: list[Formula] = []
formula_nonmetal: list[Formula] = []

for element, tags in elements:
    if "halogen" in tags:
        F = Formula({element: 1}, -1)
        formulas.append((F, tags))
        formula_nonmetal.append(F)
        continue
    if "nonmetal" in tags:
        F = Formula({element: 1}, random.randint(-3, -2))
        formulas.append((F, tags))
        formula_nonmetal.append(F)
        continue
    if "metal" in tags:
        F = Formula({element: 1}, random.randint(1, 3))
        formulas.append((F, tags))
        formula_metal.append(F)
        continue

for f1 in formula_metal:
    for f2 in formula_nonmetal:
        if f2.valence==-1:
            if random.randint(1,10)<=2:
                continue
        else:
            if random.randint(1,10)<=6:
                continue
        formulas.append((f1 & f2, ("compound",)))

print(formulas)