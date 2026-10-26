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
