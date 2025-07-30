from turtle_chemistry_world.chemical_entity import *

h = Element(1)
o = Element(16)
fe = Element(56)
s = Element(32)


h2o_form = Formula({h: 2, o: 1})
fe_form = Formula({fe: 1})
s_form = Formula({s: 1})
fes_form = Formula({fe: 1, s: 1})

ice_subs = Substance(
    h2o_form,
    1000.0,
    State.S,
    -600.0,
    heat_transfer_coefficient=500,
    color="white",
    name="H2O(s)",
)
h2o_subs = Substance(
    h2o_form, 1000.0, State.L, -285.0, heat_transfer_coefficient=500, name="H2O(l)"
)
h2o_gsubs = Substance(
    h2o_form, 1000.0, State.G, -240.0, heat_transfer_coefficient=10, name="H2O(g)"
)
fe_subs = Substance(
    fe_form, 7800, State.S, 0, heat_transfer_coefficient=1000, color="black", name="Fe"
)
s_subs = Substance(
    s_form, 2300, State.S, 0, heat_transfer_coefficient=100, color="yellow", name="S"
)
fes_subs = Substance(
    fes_form, 5000, State.S, heat_transfer_coefficient=500, color="black", name="FeS"
)

SMG = speed_multiplier_factory
R = [
    Reaction({h2o_subs: 1}, {h2o_gsubs: 1}, SMG(10, 100.1)),
    Reaction({h2o_gsubs: 1}, {h2o_subs: 1}, SMG(10, max_temperature=99.9)),
    Reaction({h2o_subs: 1}, {ice_subs: 1}, SMG(10, max_temperature=-0.1)),
    Reaction({ice_subs: 1}, {h2o_subs: 1}, SMG(10, 0.1)),
    Reaction.BalanceReaction(fe_subs, s_subs, fes_subs, speed_multiplier=SMG(1.0, 70)),
]

beaker = ChemicalSystem(
    {
        ice_subs: Matter(ice_subs, 10, 0),
        #fe_subs: Matter(fe_subs, 1),
       # s_subs: Matter(s_subs, 1),
    }
)

T = 0.001
envt = 20.0

while True:
    cmd_tup = input(">>> ").split()
    cmd = cmd_tup[0]
    if cmd == "check":
        print(beaker.check())
        temp = 0
        v = 0
        for mat in beaker.matters.values():
            temp += mat.temperature * mat.volume
            v += mat.volume
        print("temperature:", str(round(temp / v)) + "℃")
    elif cmd == "run":
        t = float(cmd_tup[1])
        n = int(t / T)
        for i in range(n):
            beaker.simulate(R, T, envt)
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
    elif cmd == "cheat":
        print(beaker)
