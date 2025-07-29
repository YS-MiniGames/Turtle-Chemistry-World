from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class Element:
    relative_mass: float = 1.0  # g/mol
