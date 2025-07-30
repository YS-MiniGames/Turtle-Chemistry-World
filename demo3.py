from turtle_chemistry_world.chemical_entity import *

fe = Element(56)
s = Element(32)
h = Element(1)
o = Element(16)


h2o_form = Formula({h: 2, o: 1})
fe_form = Formula({fe: 1})
s_form = Formula({s: 1})
fes_form = Formula({fe: 1, s: 1})

ice_subs = Substance(
    h2o_form,
    900.0,
    State.S,
    -6000.0,
    heat_transfer_coefficient=150,
    color="white",
    name="H2O(s)",
)
water_subs = Substance(
    h2o_form, 1000.0, State.L, -280.0, heat_transfer_coefficient=100, name="H2O(l)"
)
h2o_gsubs = Substance(
    h2o_form, 1000.0, State.G, 8000, heat_transfer_coefficient=10, name="H2O(g)"
)
fe_subs = Substance(
    fe_form, 7800, State.S, 0, heat_transfer_coefficient=500, color="black", name="Fe"
)
s_subs = Substance(
    s_form, 2300, State.S, 0, heat_transfer_coefficient=100, color="yellow", name="S"
)
fes_subs = Substance(
    fes_form, 5000, State.S, heat_transfer_coefficient=200, color="black", name="FeS"
)


R = [
    Reaction.BalanceReaction(
        fe_subs, s_subs, fes_subs, speed_multiplier=speed_multiplier_factory(1.0, 100)
    ),
    Reaction({ice_subs: 1}, {water_subs: 1}, speed_multiplier_factory(1.0, 0)),
    Reaction(
        {water_subs: 1},
        {ice_subs: 1},
        speed_multiplier_factory(1.0, max_temperature=0),
    ),
    Reaction(
        {h2o_gsubs: 1},
        {water_subs: 1},
        speed_multiplier_factory(1.0, max_temperature=100),
    ),
    Reaction(
        {water_subs: 1},
        {h2o_gsubs: 1},
        speed_multiplier_factory(1.0, 100),
    ),
]

beaker = ChemicalSystem(
    {
        ice_subs: Matter(ice_subs, 1, -5),
    }
)

T = 0.001
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
