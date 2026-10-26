import unittest
from Calc import Calculator  # The class we are going to implement

class TestCalculator(unittest.TestCase):
    def test_add(self):
        calc = Calculator()
        result = calc.add(2, 3)
        self.assertEqual(result, 5)  # Expect 2 + 3 = 5
        
        result = calc.add('2', 3)
        self.assertEqual(result, None) 

        result = calc.add('2', '3')
        self.assertEqual(result, None)

        result = calc.add(1e308, 1e308)
        self.assertEqual(result, None)

        result = calc.add(10**100, 10**100)
        self.assertEqual(result, None)




    def test_subtract(self):
        calc = Calculator()
        result = calc.subtract(5, 3)
        self.assertEqual(result, 2)  # Expect 5 - 3 = 2

        result = calc.subtract('2', 3)
        self.assertEqual(result, None) 

        result = calc.subtract('2', '3')
        self.assertEqual(result, None)

    def test_multiply(self):
        calc = Calculator()
        result = calc.multiply(4, 3)
        self.assertEqual(result, 12)  # Expect 4 * 3 = 12

        result = calc.multiply('2', '3')
        self.assertEqual(result, None)

        result = calc.multiply('2', 3)
        self.assertEqual(result, None)

        result = calc.multiply(1e308, 1e308)
        self.assertEqual(result, None)

        result = calc.multiply(10**100, 10**100)
        self.assertEqual(result, None)

    def test_divide(self):
        calc = Calculator()
        result = calc.divide(10, 2)
        self.assertEqual(result, 5)  # Expect 10 / 2 = 5

        result = calc.divide(2, '3')
        self.assertEqual(result, None)

        result = calc.divide("documents" , "report.txt")
        self.assertEqual(result, None)

        result = calc.divide(1e308, 1e-308)
        self.assertEqual(result, None)

    def test_modulo(self):
        calc = Calculator()
        self.assertEqual(calc.modulo(7, 3), 1)  # Expect 7 % 3 = 1
        self.assertEqual(calc.modulo(6, 3), 0)

        # Decision (c): floored modulo, the result takes the sign of the divisor
        self.assertEqual(calc.modulo(-7, 3), 2)
        self.assertEqual(calc.modulo(7, -3), -2)
        self.assertEqual(calc.modulo(-7, -3), -1)

    def test_modulo_by_zero(self):
        calc = Calculator()
        # Decision (c): same as divide, modulo by zero raises ValueError
        with self.assertRaises(ValueError):
            calc.modulo(7, 0)
        with self.assertRaises(ValueError):
            calc.modulo(7, 0.0)

    def test_modulo_invalid_input(self):
        calc = Calculator()
        # Same as the other operations: non-numbers return None
        self.assertEqual(calc.modulo('7', 3), None)
        self.assertEqual(calc.modulo(7, '3'), None)
        self.assertEqual(calc.modulo('7', '3'), None)
        # Like divide, input type is checked before the zero divisor
        self.assertEqual(calc.modulo('7', 0), None)

    def test_power(self):
        calc = Calculator()
        self.assertEqual(calc.power(2, 3), 8)  # Expect 2 ** 3 = 8
        self.assertEqual(calc.power(-2, 3), -8)
        self.assertEqual(calc.power(5, 0), 1)

        # Decision (c): power(0, 0) is 1
        self.assertEqual(calc.power(0, 0), 1)

    def test_power_negative_exponent(self):
        calc = Calculator()
        # Decision (c): a negative exponent returns a float
        result = calc.power(2, -1)
        self.assertEqual(result, 0.5)
        self.assertIsInstance(result, float)
        self.assertEqual(calc.power(-2, -2), 0.25)

        # 0 to a negative power is a division by zero, so it raises ValueError like divide
        with self.assertRaises(ValueError):
            calc.power(0, -1)

    def test_power_invalid_input(self):
        calc = Calculator()
        # Same as the other operations: non-numbers return None
        self.assertEqual(calc.power('2', 3), None)
        self.assertEqual(calc.power(2, '3'), None)
        self.assertEqual(calc.power('2', '3'), None)
        # Input type is checked before the zero-base rule
        self.assertEqual(calc.power(0, '-1'), None)

    def test_power_overflow(self):
        calc = Calculator()
        # Same int32 result range as add/subtract/multiply
        self.assertEqual(calc.power(2, 30), 1073741824)
        self.assertEqual(calc.power(-2, 31), -2147483648)  # INT32_MIN still fits
        self.assertEqual(calc.power(2, 31), None)          # INT32_MAX + 1
        self.assertEqual(calc.power(10, 100), None)

        # Float overflow returns None (Python raises OverflowError here)
        self.assertEqual(calc.power(10.0, 400), None)
        self.assertEqual(calc.power(1e308, 2), None)

    def test_power_no_real_result(self):
        calc = Calculator()
        # A negative base with a fractional exponent has no real result
        # (Python would return a complex number), so it raises ValueError
        with self.assertRaises(ValueError):
            calc.power(-8, 0.5)
        with self.assertRaises(ValueError):
            calc.power(-2.0, 1.5)
        # A negative base with a whole-number float exponent is still real
        self.assertEqual(calc.power(-2, 2.0), 4.0)


if __name__ == "__main__":
    unittest.main()