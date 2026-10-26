import math
import operator

class Calculator:
    INT32_MIN = -2147483648       # -2**31
    INT32_MAX = 2147483647        # 2**31 - 1

    def _valid_inputs(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            print("Invalid input: both arguments must be numbers.")
            return False
        return True

    def _calculate(self, operation, a, b):
        try:
            c = operation(a, b)
            if isinstance(c, float) and math.isinf(c):
                raise OverflowError("the result is too large.")
            if isinstance(c, int) and (c < self.INT32_MIN or c > self.INT32_MAX):
                raise OverflowError("the result is too large.")
        except OverflowError:
            print("Overflow error: the result is too large.")
            return None

        return c

    def add(self, a, b):
        if not self._valid_inputs(a, b):
            return None

        return self._calculate(operator.add, a, b)

    def subtract(self, a, b):
        if not self._valid_inputs(a, b):
            return None

        return self._calculate(operator.sub, a, b)

    def multiply(self, a, b):
        if not self._valid_inputs(a, b):
            return None

        return self._calculate(operator.mul, a, b)

    def divide(self, a, b):
        if not self._valid_inputs(a, b):
            return None

        if b == 0:
            raise ValueError("Cannot divide by zero")

        return self._calculate(operator.truediv, a, b)

    def modulo(self, a, b):
        if not self._valid_inputs(a, b):
            return None

        if b == 0:
            raise ValueError("Cannot modulo by zero")

        return math.fmod(a, b)

    def power(self, a, b):
        if not self._valid_inputs(a, b):
            return None

        if a == 0 and b < 0:
            raise ValueError("Cannot raise zero to a negative power")

        c = self._calculate(operator.pow, a, b)
        if isinstance(c, complex):
            raise ValueError("The result is not a real number")

        return c
