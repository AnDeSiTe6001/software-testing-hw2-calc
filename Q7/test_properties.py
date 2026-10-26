"""Question 7: property-based and metamorphic tests for Calc.

None of these tests hard-code an expected result. Each one checks a relation
that must hold between several calls to the calculator.

The same tests run against two implementations:
  - AgentCalc: written by a fresh agent session that only saw the Q1 tests
  - Q1Calc:    my own Calc from Question 1 (git commit 00bae58)

Run from the HW2 folder:
    .venv/Scripts/python.exe -m unittest -v Q7.test_properties
"""
import contextlib
import importlib.util
import io
import math
import os
import unittest

from hypothesis import HealthCheck, assume, given, settings, strategies as st

HERE = os.path.dirname(os.path.abspath(__file__))
INT32_MIN, INT32_MAX = -2**31, 2**31 - 1


def load_calculator(folder):
    path = os.path.join(HERE, folder, "Calc.py")
    spec = importlib.util.spec_from_file_location(f"{folder}_Calc", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Calculator()


class Quiet:
    """Calls the calculator with its print() messages hidden."""

    def __init__(self, calc):
        self._calc = calc

    def __getattr__(self, name):
        method = getattr(self._calc, name)

        def call(*args):
            with contextlib.redirect_stdout(io.StringIO()):
                return method(*args)
        return call


int32s = st.integers(INT32_MIN, INT32_MAX)
small_ints = st.integers(-46340, 46340)        # products always fit in int32
wide_ints = st.integers(-2**70, 2**70)         # also beyond int32 and int64
finite_floats = st.floats(allow_nan=False, allow_infinity=False)
# Each test class below binds its own calculator, so sharing the test functions is safe
check = settings(max_examples=500, derandomize=True, deadline=None,
                 suppress_health_check=[HealthCheck.differing_executors])


class CalcProperties:
    calc = None

    # --- Metamorphic relations taken from the assignment ----------------

    @check
    @given(int32s, int32s)
    def test_subtract_undoes_add(self, a, b):
        total = self.calc.add(a, b)
        assume(total is not None)
        self.assertEqual(self.calc.subtract(total, b), a)

    @check
    @given(small_ints, small_ints.filter(lambda b: b != 0))
    def test_divide_undoes_multiply(self, a, b):
        product = self.calc.multiply(a, b)
        assume(product is not None)
        self.assertEqual(self.calc.divide(product, b), a)

    # --- Algebraic properties -------------------------------------------

    @check
    @given(wide_ints, wide_ints)
    def test_add_is_commutative(self, a, b):
        self.assertEqual(self.calc.add(a, b), self.calc.add(b, a))

    @check
    @given(wide_ints, wide_ints)
    def test_multiply_is_commutative(self, a, b):
        self.assertEqual(self.calc.multiply(a, b), self.calc.multiply(b, a))

    @check
    @given(small_ints, small_ints, small_ints)
    def test_multiply_distributes_over_add(self, a, b, c):
        left = self.calc.multiply(a, self.calc.add(b, c))
        right = self.calc.add(self.calc.multiply(a, b), self.calc.multiply(a, c))
        assume(left is not None and right is not None)
        self.assertEqual(left, right)

    @check
    @given(wide_ints, wide_ints)
    def test_add_equals_subtract_negation(self, a, b):
        # a + b and a - (-b) are the same value, so they must also agree on overflow
        self.assertEqual(self.calc.add(a, b), self.calc.subtract(a, -b))

    @check
    @given(wide_ints)
    def test_number_minus_itself_is_zero(self, a):
        # a - a is 0 for every number, so it can never overflow
        self.assertEqual(self.calc.subtract(a, a), 0)

    # --- Same value, different type ---------------------------------------

    @check
    @given(st.integers(-2**52, 2**52), st.integers(-2**52, 2**52))
    def test_int_and_float_inputs_agree(self, a, b):
        # Below 2**53 every int converts to float exactly, so 7 and 7.0 are
        # the same number and must give the same answer (or both overflow).
        as_ints = self.calc.add(a, b)
        as_floats = self.calc.add(float(a), float(b))
        self.assertEqual(as_ints is None, as_floats is None,
                         f"add({a}, {b}) -> {as_ints!r} but add({float(a)}, {float(b)}) -> {as_floats!r}")
        if as_ints is not None:
            self.assertEqual(as_ints, as_floats)

    # --- Floating point --------------------------------------------------

    @check
    @given(finite_floats, finite_floats)
    def test_subtract_undoes_add_for_floats(self, a, b):
        total = self.calc.add(a, b)
        assume(total is not None)
        back = self.calc.subtract(total, b)
        self.assertTrue(math.isclose(back, a, rel_tol=1e-9, abs_tol=1e-9),
                        f"subtract(add({a!r}, {b!r}), {b!r}) = {back!r}, expected about {a!r}")


class AgentCalcProperties(CalcProperties, unittest.TestCase):
    calc = Quiet(load_calculator("agent_calc"))


class Q1CalcProperties(CalcProperties, unittest.TestCase):
    calc = Quiet(load_calculator("q1_calc"))


if __name__ == "__main__":
    unittest.main()
