from chemical_entity import *

K = Element(39)
Mn = Element(55)
O = Element(16)

oxygen = Formula({O: 2}, 0)
MnO2 = Formula({Mn: 1, O: 2}, 0)
MnO4_high = Formula({Mn: 1, O: 4}, -1)
MnO4 = Formula({Mn: 1, O: 4}, -2)
K_ion = Formula({K: 1}, 1)

KMnO4 = K_ion & MnO4_high
K2MnO4 = K_ion & MnO4

oxygen_substance = Substance(oxygen, State.G, 1, "O2")
KMnO4_substance = Substance(KMnO4, State.S, 2700, "KMnO4")
K2MnO4_substance = Substance(K2MnO4, State.S, 2700, "K2MnO4")
MnO2_substance = Substance(MnO2, State.S, 5000, "MnO2")

reac = Reaction.BalanceReaction(
    KMnO4_substance, oxygen_substance, K2MnO4_substance, MnO2_substance
)

print(reac.left)
print(reac.right)

beaker = System(
    {
        oxygen_substance: Matter(oxygen_substance, 10),
        KMnO4_substance: Matter(KMnO4_substance, 10),
    }
)

print(beaker.matters)


R = [reac]
n = int(input("How many times? "))
n = int(n / 0.01)
for i in range(n):
    beaker.simulate(R)
beaker.simulate(R)

print(beaker.matters)
