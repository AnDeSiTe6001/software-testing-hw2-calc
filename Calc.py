import math

class Calculator:
    INT32_MIN = -2147483648       # -2**31
    INT32_MAX = 2147483647        # 2**31 - 1
    
    def add(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            print("Invalid input: both arguments must be numbers.")
            return None

        try:
            c = a + b
            if isinstance(c, float) and math.isinf(c):
                raise OverflowError("the result is too large.")
            if isinstance(c, int) and (c < self.INT32_MIN or c > self.INT32_MAX):
                raise OverflowError("the result is too large.")
        except OverflowError:
            print("Overflow error: the result is too large.")
            return None
        
        return c
    
    def subtract(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            print("Invalid input: both arguments must be numbers.")
            return None
        
        try:
            c = a - b
            if isinstance(c, float) and math.isinf(c):
                raise OverflowError("the result is too large.")
            if isinstance(c, int) and (c < self.INT32_MIN or c > self.INT32_MAX):
                raise OverflowError("the result is too large.")
        except OverflowError:
            print("Overflow error: the result is too large.")
            return None
        
        return c
    
    def multiply(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            print("Invalid input: both arguments must be numbers.")
            return None

        try:
            c = a * b
            if isinstance(c, float) and math.isinf(c):
                raise OverflowError("the result is too large.")
            if isinstance(c, int) and (c < self.INT32_MIN or c > self.INT32_MAX):
                raise OverflowError("the result is too large.")
        except OverflowError:
            print("Overflow error: the result is too large.")
            return None
        
        return c
    
    def divide(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            print("Invalid input: both arguments must be numbers.")
            return None

        if b == 0:
            raise ValueError("Cannot divide by zero")

        try:
            c = a / b
            if isinstance(c, float) and math.isinf(c):
                raise OverflowError("the result is too large.")
        except OverflowError:
            print("Overflow error: the result is too large.")
            return None

        return c

    def modulo(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            print("Invalid input: both arguments must be numbers.")
            return None

        if b == 0:
            raise ValueError("Cannot modulo by zero")

        return a % b

    def power(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            print("Invalid input: both arguments must be numbers.")
            return None

        if a == 0 and b < 0:
            raise ValueError("Cannot raise zero to a negative power")

        try:
            c = a ** b
            if isinstance(c, float) and math.isinf(c):
                raise OverflowError("the result is too large.")
            if isinstance(c, int) and (c < self.INT32_MIN or c > self.INT32_MAX):
                raise OverflowError("the result is too large.")
        except OverflowError:
            print("Overflow error: the result is too large.")
            return None

        return c
