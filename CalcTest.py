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


if __name__ == "__main__":
    unittest.main()