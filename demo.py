from turtle_chemistry_world.chemical_entity import *

fe = Element(56)
s = Element(32)

fe_form = Formula({fe: 1})
s_form = Formula({s: 1})
fes_form = Formula({fe: 1, s: 1})

fe_subs = Substance(
    fe_form, 7800, State.S, 0, heat_transfer_coefficient=1000, color="black", name="Fe"
)
s_subs = Substance(
    s_form, 2300, State.S, 0, heat_transfer_coefficient=100, color="yellow", name="S"
)
fes_subs = Substance(
    fes_form, 5000, State.S, heat_transfer_coefficient=500, color="black", name="FeS"
)

reac = Reaction.BalanceReaction(
    fe_subs, s_subs, fes_subs, speed_multiplier=speed_multiplier_factory(1.0, 100)
)

R = [reac]

beaker = ChemicalSystem(
    {
        fe_subs: Matter(fe_subs, 10),
        s_subs: Matter(s_subs, 10),
    }
)

T = 0.01
envt = 20.0

while True:
    cmd_tup = input(">>> ").split()
    cmd = cmd_tup[0]
    if cmd == "run":
        t = float(cmd_tup[1])
        n = int(t / T)
        for i in range(n):
            beaker.run(R, T, envt)
            # print(envt, beaker)
    elif cmd == "heating":
        if envt == 400.0:
            print("stop heating")
            envt = 20.0
        else:
            print("start heating")
            envt = 400.0
    elif cmd == "cooling":
        if envt == 0.0:
            print("stop cooling")
            envt = 20.0
        else:
            print("start cooling")
            envt = 0.0
    elif cmd == "stop":
        break
    elif cmd == "display":
        print(beaker)
