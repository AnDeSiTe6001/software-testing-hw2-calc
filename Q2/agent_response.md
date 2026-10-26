CI on `main` passes again. The fix was one line in `Calc.py`: I put the `%` operator back in `modulo`.

**(1) Cause.** The latest commit, `64fe306` ("Change modulo implementation to math.fmod"), replaced `return a % b` with `return math.fmod(a, b)` in `Calculator.modulo`.
- `math.fmod` truncates toward zero, so the result takes the sign of the dividend.
- The project's agreed design decision is floored modulo, where the result takes the sign of the divisor, as in Python's `%`. It is in `CalcTest.py` ("Decision (c): floored modulo, the result takes the sign of the divisor") and in `HW2_Q6_Q7_Report.md`.
- So `calc.modulo(-7, 3)` returned `-1.0` instead of `2`. CI failed on `test_modulo` with `AssertionError: -1.0 != 2` (1 failure out of 12 tests).
- This is the second time this change has gone in. Commit `45c893f` did the same thing, failed CI and was reverted in `04b295a`; `64fe306` then re-applied it. I fixed the code to match the documented decision and did not touch the tests.

**(2) Full diff.** Only `Calc.py` changed:
```
diff --git a/Calc.py b/Calc.py
index d873967..3185e12 100644
--- a/Calc.py
+++ b/Calc.py
@@ -58,7 +58,7 @@ class Calculator:
         if b == 0:
             raise ValueError("Cannot modulo by zero")
 
-        return math.fmod(a, b)
+        return a % b
 
     def power(self, a, b):
         if not self._valid_inputs(a, b):
```
Before pushing, I ran the tests with the Python 3.13 venv: `python -m unittest CalcTest` ran 12 tests, all OK.

**(3) Commit pushed to main:** `fe715180d7dd1dadb74ae238e071c68606e643cf` (fe71518), message "fix: restore floored modulo (a % b) so CI passes". It moved `main` from 64fe306 to fe71518.

**(4) CI result:** run 40347187097 completed with conclusion **success**, and its log shows "Ran 12 tests ... OK".
https://github.com/AnDeSiTe6001/software-testing-hw2-calc/actions/runs/40347187097

If the user actually wants truncated (fmod) semantics, the tests and the report's design decision would have to change as well. Swapping the implementation alone will keep breaking CI.

Repo: C:/Users/josep/AppData/Local/Temp/claude/C--Users-josep-Documents-Software-Testing-2026-HW2/d27258f4-686c-4fcd-859c-756ca0e0bd54/scratchpad/q2_agent/repo (changed file: `Calc.py` in that folder).
