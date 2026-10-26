All 4 tests pass. I created Calc.py and left CalcTest.py unchanged.

File: C:/Users/josep/AppData/Local/Temp/claude/C--Users-josep-Documents-Software-Testing-2026-HW2/d27258f4-686c-4fcd-859c-756ca0e0bd54/scratchpad/q7_agent/Calc.py

(1) Final contents of Calc.py

```python
import math

# Integer results must fit in a signed 64-bit integer; float results must be finite.
INT_MIN = -(2 ** 63)
INT_MAX = 2 ** 63 - 1


class Calculator:
    """A simple calculator that returns None for invalid input or out-of-range results."""

    @staticmethod
    def _is_valid_number(value):
        # Accept only real ints and floats; bool is a subclass of int but is not a number here.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        if isinstance(value, float):
            return math.isfinite(value)
        return INT_MIN <= value <= INT_MAX

    @classmethod
    def _check_result(cls, result):
        return result if cls._is_valid_number(result) else None

    def _compute(self, a, b, operation):
        if not (self._is_valid_number(a) and self._is_valid_number(b)):
            return None
        try:
            result = operation(a, b)
        except (OverflowError, ZeroDivisionError):
            return None
        return self._check_result(result)

    def add(self, a, b):
        return self._compute(a, b, lambda x, y: x + y)

    def subtract(self, a, b):
        return self._compute(a, b, lambda x, y: x - y)

    def multiply(self, a, b):
        return self._compute(a, b, lambda x, y: x * y)

    def divide(self, a, b):
        return self._compute(a, b, lambda x, y: x / y)
```

(2) Test output from the last run (`python.exe -m unittest -v CalcTest`, run inside the working folder)

```
test_add (CalcTest.TestCalculator.test_add) ... ok
test_divide (CalcTest.TestCalculator.test_divide) ... ok
test_multiply (CalcTest.TestCalculator.test_multiply) ... ok
test_subtract (CalcTest.TestCalculator.test_subtract) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

(3) Design decisions

- **None means error.** The tests expect `None` instead of an exception for bad input, so every invalid case returns `None`. That covers non-numbers, overflow, and division by zero.
- **Type check.** Only `int` and `float` are accepted. Strings like `'2'` or `"documents"` give `None`. I also chose to reject `bool`, because Python treats `True`/`False` as ints, which isn't what a calculator user means.
- **Range limits.** The tests need `10**100 + 10**100` and `10**100 * 10**100` to return `None`. Python ints never overflow by themselves, so the class has to set a limit. I picked the signed 64-bit integer range for both inputs and results. This is my own choice: the tests only say a limit is needed, not which one.
- **Float limits.** Float inputs and results must be finite, so NaN and infinity give `None`. This handles `1e308 + 1e308`, `1e308 * 1e308` and `1e308 / 1e-308`, which all overflow to infinity. `OverflowError` is also caught in case Python raises it instead.
- **Divide by zero.** It returns `None`, which is consistent with the rest. The tests don't check this case.
- **Division result type.** `divide` uses true division, so `10 / 2` returns `5.0`. That passes `assertEqual(..., 5)`.
- **Shared code.** All four operations go through one `_compute` helper, so the checks are written once and behave the same for each operation.
