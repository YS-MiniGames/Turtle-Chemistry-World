from turtle_chemistry_world.chemical_entity import *

fee = Element(56)
se = Element(32)

fef = Formula({fee: 1})
sf = Formula({se: 1})
fesf = Formula({fee: 1, se: 1})

fep = PhaseData(Phase.S, 0, 8, heat_transfer_coefficient=10)
fes = Substance(fef, fep, 0, "Fe")
sp = PhaseData(Phase.S, 0, 2)
ss = Substance(sf, sp, 0, "S")
fesp = PhaseData(Phase.S, 0, 5, heat_transfer_coefficient=1)
fess = Substance(fesf, fesp, -1000, "FeS")

"""
s_subs = Substance(
    s_form, 2300, State.S, 0, heat_transfer_coefficient=100, color="yellow", name="S"
)
fes_subs = Substance(
    fes_form, 5000, State.S, heat_transfer_coefficient=500, color="black", name="FeS"
)

reac = Reaction.BalanceReaction(
    fe_subs, s_subs, fes_subs, speed_multiplier=speed_multiplier_factory(1.0, 100)
)"""

R = [Reaction(*Reaction.Balance(fes, ss, fess))]

beaker = ChemicalSystem(
    {
        fes: [Matter(fes, 10)],
        ss: [Matter(ss, 10)],
    }
)

T = 0.01

while True:
    cmd_tup = input(">>> ").split()
    cmd = cmd_tup[0]
    if cmd == "run":
        t = float(cmd_tup[1])
        n = int(t / T)
        for i in range(n):
            beaker.run(R, T)
    elif cmd == "temp":
        print(beaker.avg_temperature - 274.15, "Celcius")
    elif cmd == "stop":
        break
    elif cmd == "display":
        print(beaker)
