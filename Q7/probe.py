"""Question 7: run both calculators on inputs that the Q1 tests never use.

1. Fresh inputs: does the agent's Calc only work for the inputs in CalcTest.py?
2. Differential cases: where do the agent's Calc and my Q1 Calc disagree?

Run from the HW2 folder:
    .venv/Scripts/python.exe -m Q7.probe
"""
from Q7.test_properties import Quiet, load_calculator

agent = Quiet(load_calculator("agent_calc"))
mine = Quiet(load_calculator("q1_calc"))


def run(calc, op, a, b):
    try:
        return repr(getattr(calc, op)(a, b))
    except Exception as e:
        return f"raises {type(e).__name__}"


CASES = [
    # Fresh inputs that are not in CalcTest.py
    ("add", 7, 8), ("add", -5, 5), ("subtract", 100, 1), ("subtract", -3, 9),
    ("multiply", -3, 7), ("multiply", 0, 12345), ("divide", 7, 2), ("divide", -9, 3),
    ("add", 0.1, 0.2),
    # Boundaries and cases the Q1 tests leave open
    ("add", 2**31 - 1, 1), ("add", 2**62, 2**62), ("add", 2.0**62, 2.0**62),
    ("subtract", 2**63, 2**63), ("add", 10**20, -10**20),
    ("divide", 1, 0), ("divide", 0, 0),
    ("add", True, 1), ("add", float("nan"), 1), ("add", float("inf"), 1),
]

print(f"{'call':<54}{'agent Calc':<26}{'my Q1 Calc':<26}")
for op, a, b in CASES:
    left, right = run(agent, op, a, b), run(mine, op, a, b)
    mark = "" if left == right else "  <-- differ"
    print(f"{f'{op}({a!r}, {b!r})':<54}{left:<26}{right:<26}{mark}")
