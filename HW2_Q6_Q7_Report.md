# Software Testing HW2：第 6、7 題報告（CalcTDD with AI agent）

## 0. 環境與工具

| 項目 | 內容 |
|---|---|
| 語言／測試框架 | Python 3.13.7、`unittest` |
| Property-based testing | `hypothesis` 6.170.11（僅第 7 題使用） |
| AI coding agent | Claude Code 2.1.274（Claude 桌面應用程式 Code 分頁） |
| 模型 | Claude Opus 5.5（model ID `claude-opus-5-5`） |
| 版本控制 | git 2.51.0（本機 repo，branch `main`） |
| 起點 | 第 1 題自行完成、未使用 AI 的 `Calc.py` / `CalcTest.py`，提交為 baseline commit `00bae58` |

專案結構：

```
HW2/
├── Calc.py                 # 第 6 題最終版本
├── CalcTest.py             # 第 1 題 + 第 6 題所有測試
├── evidence/q6/            # 每個 cycle 的紅燈／綠燈輸出、git log
├── evidence/q7_*.txt       # 第 7 題的測試與探測輸出
└── Q7/
    ├── agent_calc/         # 新 agent session 只看測試寫出的 Calc
    ├── q1_calc/            # 我第 1 題的 Calc（取自 commit 00bae58）
    ├── test_properties.py  # property-based / metamorphic 測試
    ├── probe.py            # 新輸入探測與差異比較
    ├── agent_prompt.txt    # 給新 agent 的提示（原文）
    └── agent_response.md   # 新 agent 的完整回應（原文）
```

---

## 第 6 題：Agentic TDD（modulo 與 power）

### 6.1 工作流程

每個 cycle 都照下列順序進行，git 歷史可以驗證這個順序（見 6.6）：

1. **Red**：agent 在 `CalcTest.py` 新增**一個**測試方法，只執行該測試，並把失敗輸出存進 `evidence/q6/cycleN_red.txt`。此時 `Calc.py` 裡還沒有該行為的實作。
2. **Review**：agent 用選擇題把測試內容與失敗原因交給我審查；我核准後才繼續。
3. **Commit test**：`test(cycle N): ...`，commit 訊息註記「Reviewed and approved by AnDeSiTe6001 before commit」。
4. **Green**：agent 只修改 `Calc.py`，跑完整測試套件（輸出存進 `cycleN_green.txt`）。
5. **Commit implementation**：`feat(cycle N): ...`，不含任何測試檔變更。
6. **Refactor**：全部 cycle 結束後，另做一個 `refactor:` commit，測試前後都全綠。

> 註：`cycleN_green.txt` 過濾掉了 Calc 自己印出的 `Invalid input...`、`Overflow error...` 訊息，方便閱讀。未過濾的完整輸出在 `evidence/q6/final_all_tests.txt`。

### 6.2 (c) 規定的決策：寫測試前先問我

agent 在寫任何 modulo/power 測試**之前**，用一次四題的選擇題詢問這四個決策。每題都附上候選語意與範例，agent 也標出它建議的選項（Recommended）。我四題都選了建議選項：

| 決策 | 我的選擇 | 編碼在哪個測試 |
|---|---|---|
| modulo 遇到負數運算元 | **Floored**（餘數正負號跟除數，與 Python 相同）：`modulo(-7, 3) == 2`、`modulo(7, -3) == -2` | `test_modulo`（cycle 1） |
| modulo 除以零 | **raise `ValueError`**（與第 1 題 `divide` 一致） | `test_modulo_by_zero`（cycle 2） |
| `power(0, 0)` | **回傳 1** | `test_power`（cycle 4） |
| 負指數 | **回傳 float**（`power(2, -1) == 0.5`）；`power(0, -1)` 視同除以零，raise `ValueError` | `test_power_negative_exponent`（cycle 5） |

此外，agent 在 cycle 8 之前發現第五個問題：`power(-8, 0.5)` 在 Python 會回傳**複數**。這不在 (c) 的範圍內，agent 也先停下來問我；我選擇 raise `ValueError`。

### 6.3 各 Cycle 敘述

#### Cycle 1：`test_modulo`（基本餘數 + floored 負數規則）

- **測試**：`modulo(7,3)==1`、`modulo(6,3)==0`、`modulo(-7,3)==2`、`modulo(7,-3)==-2`、`modulo(-7,-3)==-1`。
- **紅燈**：`AttributeError: 'Calculator' object has no attribute 'modulo'`。
- **我的審查意見**：核准。負數案例三種正負號組合都涵蓋到了。
- **Agent 的修改**：新增 `def modulo(self, a, b): return a % b`。Python 的 `%` 本來就是 floored 語意，所以一行就讓測試通過。
- **重構**：無。
- **設計說明**：如果先只測 `modulo(7,3)` 再另開一個負數 cycle，負數測試在 `a % b` 下會直接通過，無法先看到紅燈。所以 agent 把決策跟基本案例放進同一個測試，讓決策在實作前就寫成測試。
- Commits：`b9cc7d1`（test）→ `409b1b3`（feat）

#### Cycle 2：`test_modulo_by_zero`

- **測試**：`modulo(7, 0)` 與 `modulo(7, 0.0)` 都要 raise `ValueError`。
- **紅燈**：`ZeroDivisionError: integer modulo by zero`。Python 預設丟的是另一種例外。
- **我的審查意見**：核准。另外測了 float 的 `0.0`，可以確保 `b == 0` 的判斷對 int 與 float 都成立。
- **Agent 的修改**：在 `modulo` 開頭加上 `if b == 0: raise ValueError("Cannot modulo by zero")`。
- **重構**：無。
- Commits：`7665751` → `f2efb6e`

#### Cycle 3：`test_modulo_invalid_input`

- **測試**：`modulo('7',3)`、`modulo(7,'3')`、`modulo('7','3')` 都回傳 `None`；另外 `modulo('7', 0)` 也回傳 `None`，代表**先檢查型別、再檢查除數為零**。
- **紅燈**：`TypeError: not all arguments converted during string formatting`。`'7' % 3` 被 Python 當成字串格式化運算子，這是 Python 特有的陷阱。
- **我的審查意見**：核准，也同意「先檢查型別」的順序（agent 在審查時有明確指出這是它自己加的決策）。
- **Agent 的修改**：加入與其他運算相同的 `isinstance` 檢查，非數字時印出訊息並回傳 `None`。
- **重構**：無。
- Commits：`6b55792` → `2e3043c`

> 第 2 題結束時，Claude Code 的自動安全審查外掛提醒 `modulo` 缺少型別檢查（`%` 對字串會變成格式化）。這正是 cycle 3 的內容，agent 沒有提前修，而是照 TDD 規則先寫失敗的測試。

#### Cycle 4：`test_power`（基本次方 + `power(0,0)`）

- **測試**：`power(2,3)==8`、`power(-2,3)==-8`、`power(5,0)==1`、`power(0,0)==1`。
- **紅燈**：`AttributeError: 'Calculator' object has no attribute 'power'`。
- **我的審查意見**：核准。
- **Agent 的修改**：新增 `def power(self, a, b): return a ** b`。
- **重構**：無。
- Commits：`d8205d7` → `b831c69`

#### Cycle 5：`test_power_negative_exponent`

- **測試**：`power(2,-1) == 0.5` 且型別為 `float`、`power(-2,-2) == 0.25`、`power(0,-1)` raise `ValueError`。
- **紅燈**：`ZeroDivisionError: 0.0 cannot be raised to a negative power`。
- **我的審查意見**：核准。agent 在審查時主動說明：「回傳 float」那幾行在 cycle 4 的 `a ** b` 下**已經會通過**，真正造成紅燈的只有 `power(0, -1)`。我同意保留那幾行，作為決策 (c) 的明確編碼。
- **Agent 的修改**：加上 `if a == 0 and b < 0: raise ValueError(...)`。
- **重構**：無。
- Commits：`9bb80f2` → `a404ff6`

#### Cycle 6：`test_power_invalid_input`

- **測試**：`power('2',3)`、`power(2,'3')`、`power('2','3')` 回傳 `None`；`power(0,'-1')` 也回傳 `None`，代表型別檢查排在「0 的負次方」規則之前。
- **紅燈**：`TypeError: unsupported operand type(s) for ** or pow(): 'str' and 'int'`。
- **我的審查意見**：核准，同意檢查順序。
- **Agent 的修改**：加入 `isinstance` 檢查。
- **重構**：無。
- Commits：`e8ccfc1` → `e167a92`

#### Cycle 7：`test_power_overflow`

- **測試**：沿用第 1 題的 int32 結果範圍，並測試邊界：`power(2,30)==1073741824`、`power(-2,31)==-2147483648`（剛好等於 INT32_MIN，仍可表示）、`power(2,31)` 與 `power(10,100)` 回傳 `None`；float 溢位的 `power(10.0,400)`、`power(1e308,2)` 也回傳 `None`。
- **紅燈**：`AssertionError: 2147483648 != None`。
- **我的審查意見**：核准。測到 INT32_MIN 與 INT32_MAX+1 兩個邊界。
- **Agent 的修改**：把 `a ** b` 包進與 add/multiply 相同的 `try/except OverflowError` 區塊，並加上 int32 與 `isinf` 檢查。Python 的 float `**` 溢位時會直接 raise `OverflowError`，不會回傳 `inf`，所以 except 區塊是必要的。
- **重構**：無（重複的程式碼留到最後的重構步驟一起處理）。
- Commits：`43abd8a` → `c20110a`

#### Cycle 8：`test_power_no_real_result`（額外決策）

- **測試**：`power(-8, 0.5)` 與 `power(-2.0, 1.5)` raise `ValueError`；對照案例 `power(-2, 2.0) == 4.0`（指數是 float 但為整數值，結果仍是實數）。
- **紅燈**：`AssertionError: ValueError not raised`（實際回傳 `(1.7e-16+2.83j)` 這種複數）。
- **我的審查意見**：核准。
- **Agent 的修改**：計算後若結果為 `complex`，raise `ValueError("The result is not a real number")`。
- **重構**：無。
- Commits：`c77bf55` → `9dfafdc`

### 6.4 重構（commit `dfc95c6`）

完成 8 個 cycle 後，`add/subtract/multiply/divide/power` 有五份幾乎一樣的程式碼：

- `isinstance` 型別檢查，加上印訊息、回傳 `None`
- `try` → 計算 → 檢查 `isinf` 與 int32 範圍 → `except OverflowError` → 印訊息、回傳 `None`

agent 把它們抽成兩個 helper：`_valid_inputs(a, b)` 與 `_calculate(operation, a, b)`，運算本身改用 `operator.add/sub/mul/truediv/pow` 傳入。`Calc.py` 從 107 行變成 74 行（+29/−61）。

注意事項：

- `modulo` **刻意不套用** `_calculate`。int32 檢查會讓 `modulo(10**99, 10**100)` 從回傳 `10**99` 變成回傳 `None`，這是行為改變，不是重構。
- 重構前後都跑完整 12 個測試，全數通過；測試檔沒有任何變更。

### 6.5 違規自我檢查

逐項對照規則 (a)(b)(c)：

| 規則 | 結果 | 證據 |
|---|---|---|
| (a) 每個 cycle 先寫一個失敗的測試，並展示失敗輸出 | **遵守**。8 個 cycle 的測試在實作前都是紅燈 | `evidence/q6/cycle1..8_red.txt` |
| (a) 不可先寫實作 | **遵守**。每個 `feat` commit 都在對應的 `test` commit 之後 | `git log`（6.6） |
| (b) 測試先經我審查才實作 | **遵守**。每個測試都經過選擇題審查並核准 | 本對話紀錄（附錄 G） |
| (b) 測試與實作分開 commit | **遵守** | `evidence/q6/git_numstat.txt`：`test` commit 只改 `CalcTest.py`，`feat`/`refactor` commit 只改 `Calc.py` |
| (b) 已 commit 的測試不得修改 | **遵守**。每個 `test` commit 對 `CalcTest.py` 只有新增、沒有刪除（numstat 的刪除欄全為 0） | `evidence/q6/git_numstat.txt` |
| 弱化或刪除測試 | **無** | 同上 |

需要誠實揭露的灰色地帶：

1. **Cycle 5 的部分斷言一開始就會通過**：「負指數回傳 float」在 cycle 4 的 `a ** b` 下已成立，真正驅動實作的只有 `power(0,-1)`。agent 在審查時主動說明了這點，不算違規，但代表這部分測試只有「記錄決策」的作用，沒有驅動程式碼。
2. **agent 自己做、但有在審查時標示出來的小決策**：
   - cycle 2：除數為 float `0.0` 也算除以零
   - cycle 3 / 6：先檢查型別，再處理除以零與 0 的負次方
   - cycle 7：power 沿用第 1 題的 int32 範圍與「溢位回傳 `None`」規則
   - 重構：modulo 不做溢位檢查
   - 錯誤訊息文字（測試沒有檢查訊息內容）
3. **重構動到第 1 題的 add/subtract/multiply/divide**：重構不在 (b) 的審查範圍內，agent 沒有先問我就做了。行為不變、測試全綠，但這是 agent 自行判斷的。
4. **Baseline commit 的作者標註**：agent 第一次建立 baseline commit 時，依它預設的習慣在訊息加上 `Co-Authored-By: Claude`。但第 1 題是我自己手寫的，所以 agent 隨即用 `--amend` 移除該行（當時只有這一個 commit，也還沒推送到任何地方）。

**(c) 的決策中，有哪些是 agent 沒問我就決定的？** 沒有。四個決策都在寫測試前以選擇題詢問。不過選項與「建議」都是 agent 提出的，我四題都採用了它的建議，因此最後的語意實際上受 agent 的建議框架影響很大。`power(0,-1)` 的處理寫在「負指數」那題的建議選項說明中，我選擇該選項時一併同意。

### 6.6 Git log

```text
* dfc95c6 AnDeSiTe6001 2026-10-26 22:24:56
|     refactor: extract shared input validation and overflow check
* 9dfafdc AnDeSiTe6001 2026-10-26 22:24:26
|     feat(cycle 8): power raises ValueError instead of returning a complex number
* c77bf55 AnDeSiTe6001 2026-10-26 22:24:18
|     test(cycle 8): power raises ValueError when the result is not a real number
* c20110a AnDeSiTe6001 2026-10-26 22:19:41
|     feat(cycle 7): power applies the int32/float overflow check used by the other operations
* 43abd8a AnDeSiTe6001 2026-10-26 22:19:33
|     test(cycle 7): power returns None on int32 or float overflow
* e167a92 AnDeSiTe6001 2026-10-26 22:19:03
|     feat(cycle 6): power validates that both inputs are numbers
* e8ccfc1 AnDeSiTe6001 2026-10-26 22:18:56
|     test(cycle 6): power returns None for non-number input, checked before zero-base rule
* a404ff6 AnDeSiTe6001 2026-10-26 22:18:27
|     feat(cycle 5): power raises ValueError for zero to a negative power
* 9bb80f2 AnDeSiTe6001 2026-10-26 22:18:21
|     test(cycle 5): negative exponent returns float; power(0, -1) raises ValueError
* b831c69 AnDeSiTe6001 2026-10-26 22:17:40
|     feat(cycle 4): add power using Python's ** operator
* d8205d7 AnDeSiTe6001 2026-10-26 22:17:32
|     test(cycle 4): power basic results and power(0, 0) == 1
* 2e3043c AnDeSiTe6001 2026-10-26 22:17:12
|     feat(cycle 3): modulo validates that both inputs are numbers
* 6b55792 AnDeSiTe6001 2026-10-26 22:17:04
|     test(cycle 3): modulo returns None for non-number input, checked before zero divisor
* f2efb6e AnDeSiTe6001 2026-10-26 22:14:41
|     feat(cycle 2): modulo raises ValueError when the divisor is zero
* 7665751 AnDeSiTe6001 2026-10-26 22:14:33
|     test(cycle 2): modulo by zero raises ValueError (int and float zero)
* 409b1b3 AnDeSiTe6001 2026-10-26 22:11:55
|     feat(cycle 1): add modulo using Python's floored % operator
* b9cc7d1 AnDeSiTe6001 2026-10-26 22:11:42
|     test(cycle 1): modulo basic results and floored sign rule for negative operands
* 00bae58 AnDeSiTe6001 2026-10-26 21:58:01
      Baseline: Calc and tests from Question 1 (add/subtract/multiply/divide), written by hand without AI
```

每個 commit 修改的檔案（numstat：新增行數／刪除行數／檔案）：

```text
--- b9cc7d1 test(cycle 1): modulo basic results and floored sign rule for negative operands

10	0	CalcTest.py
--- 409b1b3 feat(cycle 1): add modulo using Python's floored % operator

4	1	Calc.py
--- 7665751 test(cycle 2): modulo by zero raises ValueError (int and float zero)

8	0	CalcTest.py
--- f2efb6e feat(cycle 2): modulo raises ValueError when the divisor is zero

3	0	Calc.py
--- 6b55792 test(cycle 3): modulo returns None for non-number input, checked before zero divisor

9	0	CalcTest.py
--- 2e3043c feat(cycle 3): modulo validates that both inputs are numbers

4	0	Calc.py
--- d8205d7 test(cycle 4): power basic results and power(0, 0) == 1

9	0	CalcTest.py
--- b831c69 feat(cycle 4): add power using Python's ** operator

3	0	Calc.py
--- 9bb80f2 test(cycle 5): negative exponent returns float; power(0, -1) raises ValueError

12	0	CalcTest.py
--- a404ff6 feat(cycle 5): power raises ValueError for zero to a negative power

3	0	Calc.py
--- e8ccfc1 test(cycle 6): power returns None for non-number input, checked before zero-base rule

9	0	CalcTest.py
--- e167a92 feat(cycle 6): power validates that both inputs are numbers

4	0	Calc.py
--- 43abd8a test(cycle 7): power returns None on int32 or float overflow

12	0	CalcTest.py
--- c20110a feat(cycle 7): power applies the int32/float overflow check used by the other operations

11	1	Calc.py
--- c77bf55 test(cycle 8): power raises ValueError when the result is not a real number

11	0	CalcTest.py
--- 9dfafdc feat(cycle 8): power raises ValueError instead of returning a complex number

2	0	Calc.py
--- dfc95c6 refactor: extract shared input validation and overflow check

29	61	Calc.py
```

### 6.7 全部測試通過

最終測試結果（12 個測試全過，完整輸出含 Calc 印出的訊息）：

```text
test_add (CalcTest.TestCalculator.test_add) ... ok
test_divide (CalcTest.TestCalculator.test_divide) ... ok
test_modulo (CalcTest.TestCalculator.test_modulo) ... ok
test_modulo_by_zero (CalcTest.TestCalculator.test_modulo_by_zero) ... ok
test_modulo_invalid_input (CalcTest.TestCalculator.test_modulo_invalid_input) ... ok
test_multiply (CalcTest.TestCalculator.test_multiply) ... ok
test_power (CalcTest.TestCalculator.test_power) ... ok
test_power_invalid_input (CalcTest.TestCalculator.test_power_invalid_input) ... ok
test_power_negative_exponent (CalcTest.TestCalculator.test_power_negative_exponent) ... ok
test_power_no_real_result (CalcTest.TestCalculator.test_power_no_real_result) ... ok
test_power_overflow (CalcTest.TestCalculator.test_power_overflow) ... ok
test_subtract (CalcTest.TestCalculator.test_subtract) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.001s

OK
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Overflow error: the result is too large.
Overflow error: the result is too large.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Overflow error: the result is too large.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Overflow error: the result is too large.
Overflow error: the result is too large.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
Overflow error: the result is too large.
Overflow error: the result is too large.
Overflow error: the result is too large.
Overflow error: the result is too large.
Invalid input: both arguments must be numbers.
Invalid input: both arguments must be numbers.
```

> **截圖**：請在 `HW2` 資料夾的終端機執行下列指令並截圖，貼在這裡：
> `.venv\Scripts\python.exe -m unittest -v CalcTest`

### 6.8 已知限制（未在本次 cycle 處理）

- **超大指數的效能**：`power` 會先算出完整的大整數，再檢查 int32 範圍。實測 `power(3, 10**7)` 要 1.67 秒才回傳 `None`，指數越大耗時越長，可能被拿來做阻斷服務（DoS）。如果要修，可以再開一個 cycle：先寫一個限時測試，再在計算前用 `b * log2(|a|)` 預估結果是否溢位。
- **`bool` 會被當成數字**：`add(True, 1) == 2`，這是第 1 題就有的行為，本題沒有更動。

---

## 第 7 題：只給測試，讓新 agent 寫 Calc

### 7.1 做法

- 把第 1 題的 `CalcTest.py`（4 個測試，與 baseline commit 相同）複製到一個**只有這個檔案**的隔離資料夾。
- 啟動一個**全新、沒有本對話任何脈絡**的 Claude Code 子代理（general-purpose，模型 Claude Opus 5.5）。提示中只說「這是測試，請寫出讓全部測試通過的實作」，並要求它只能使用該資料夾、不得修改測試。提示原文見 `Q7/agent_prompt.txt`。
- 子代理共用了 4 次工具，約 39 秒完成，4 個測試全過。完整回應原文見 `Q7/agent_response.md`，產出的程式在 `Q7/agent_calc/Calc.py`。

限制：子代理與我們在同一台電腦上執行，「只看該資料夾」是靠提示約束，不是沙箱強制。它只用了 4 次工具，從匯出的對話紀錄（附錄 G）可以查證它讀了哪些檔案。

### 7.2 它有沒有特判測試用的輸入？

**沒有。** 證據如下：

1. **程式碼檢查**：`Q7/agent_calc/Calc.py` 裡唯一的數值常數是 `INT_MIN = -(2**63)`、`INT_MAX = 2**63 - 1`，沒有 `if a == 2 and b == 3` 之類的分支。四個運算都透過同一個 `_compute(a, b, lambda ...)` 計算。
2. **用測試沒出現過的輸入探測**（`Q7/probe.py`）：`add(7,8)=15`、`subtract(-3,9)=-12`、`multiply(-3,7)=-21`、`divide(7,2)=3.5` 等都正確。
3. **Property-based 測試**：在 int32 範圍內，用 hypothesis 隨機產生的上千組輸入下，加減乘除的代數性質都成立（見 7.4）。

但它**自行發明了好幾條測試沒有要求的規則**。這比特判輸入更值得注意（見 7.5）。

### 7.3 新增的 property-based／metamorphic 測試

`Q7/test_properties.py` 的每個測試都**不寫死預期值**，只檢查多次呼叫之間應成立的關係。同一組測試同時跑在兩個實作上：`AgentCalc`（新 agent 寫的）與 `Q1Calc`（我第 1 題寫的）。每個測試由 hypothesis 產生 500 組輸入，並用 `derandomize=True` 讓結果可以重現。

| 測試 | 關係 | 輸入範圍 |
|---|---|---|
| `test_subtract_undoes_add` | `subtract(add(a,b), b) == a`（題目給的例子） | int32 整數，跳過溢位 |
| `test_divide_undoes_multiply` | `divide(multiply(a,b), b) == a` | 乘積不會溢位的整數，b ≠ 0 |
| `test_add_is_commutative` | `add(a,b) == add(b,a)` | ±2⁷⁰ 的整數 |
| `test_multiply_is_commutative` | `multiply(a,b) == multiply(b,a)` | ±2⁷⁰ 的整數 |
| `test_multiply_distributes_over_add` | `a·(b+c) == a·b + a·c` | 小整數 |
| `test_add_equals_subtract_negation` | `add(a,b) == subtract(a,-b)`（包括溢位時也要一致） | ±2⁷⁰ 的整數 |
| `test_number_minus_itself_is_zero` | `subtract(a,a) == 0` | ±2⁷⁰ 的整數 |
| `test_int_and_float_inputs_agree` | `add(a,b)` 與 `add(float(a), float(b))` 結果相同，或兩者都溢位 | ±2⁵²（int 轉 float 不失真的範圍） |
| `test_subtract_undoes_add_for_floats` | `subtract(add(a,b), b) ≈ a`（`math.isclose`，容差 1e-9） | 所有有限 float |

### 7.4 結果：有沒有暴露問題？

**有。** 18 個測試中 4 個失敗（完整輸出：`evidence/q7_properties_run.txt`）：

| 測試 | AgentCalc | Q1Calc（我的） | hypothesis 縮減後的反例 |
|---|---|---|---|
| `test_number_minus_itself_is_zero` | **FAIL** | pass | `subtract(2**63, 2**63)` → `None`（應為 0） |
| `test_int_and_float_inputs_agree` | pass\* | **FAIL** | `add(0, 2147483648)` → `None`，但 `add(0.0, 2147483648.0)` → `2147483648.0` |
| `test_subtract_undoes_add_for_floats` | **FAIL** | **FAIL** | `subtract(add(1.0, 2.0**53), 2.0**53)` → `0.0`（應約為 1.0） |
| 其餘 6 個性質 | pass | pass | — |

\* AgentCalc 在這個測試的輸入範圍（±2⁵²）內沒有失敗，但同樣的問題出現在 2⁶³：探測顯示 `add(2**62, 2**62)` → `None`，`add(2.0**62, 2.0**62)` → `9.22e18`。

解讀：

1. **AgentCalc 連輸入也套用範圍限制**：它把超過 int64 的**輸入**也當成無效，所以 `subtract(2**63, 2**63)` 結果明明是 0，卻回傳 `None`。第 1 題的測試只要求「結果太大」時回傳 `None`，沒有要求拒絕輸入。這條規則是 agent 自己加的。
2. **兩個實作的溢位規則都取決於型別、而不是數值**（metamorphic 關係「7 與 7.0 應給相同答案」被違反）：
   - 我的 Q1Calc 對 int 結果套用 int32 上限，對 float 則只檢查 `inf`。所以 `add(0, 2**31)` 溢位，`add(0.0, 2.0**31)` 卻不會。
   - AgentCalc 在 int64 邊界有同樣的問題。
   - 第 1 題的測試只用了 `10**100` 與 `1e308` 這種「兩種型別都一定溢位」的極端值，因此兩個實作都沒被抓到。
3. **浮點捨入誤差**：`1.0 + 2**53` 在 IEEE 754 double 下會被捨入回 `2**53`，再減掉就得到 0。這是 float 的固有限制，兩個實作都一樣。但它說明計算機在「不溢位」的情況下仍可能**安靜地回傳錯誤答案**，第 1 題的範例測試完全看不到這類問題。

### 7.5 新 agent 的實作與我的實作差在哪（差異測試）

`Q7/probe.py` 用同一組輸入跑兩個實作（完整輸出：`evidence/q7_probe.txt`）：

```text
call                                                  agent Calc                my Q1 Calc                
add(7, 8)                                             15                        15                        
add(-5, 5)                                            0                         0                         
subtract(100, 1)                                      99                        99                        
subtract(-3, 9)                                       -12                       -12                       
multiply(-3, 7)                                       -21                       -21                       
multiply(0, 12345)                                    0                         0                         
divide(7, 2)                                          3.5                       3.5                       
divide(-9, 3)                                         -3.0                      -3.0                      
add(0.1, 0.2)                                         0.30000000000000004       0.30000000000000004       
add(2147483647, 1)                                    2147483648                None                        <-- differ
add(4611686018427387904, 4611686018427387904)         None                      None                      
add(4.611686018427388e+18, 4.611686018427388e+18)     9.223372036854776e+18     9.223372036854776e+18     
subtract(9223372036854775808, 9223372036854775808)    None                      0                           <-- differ
add(100000000000000000000, -100000000000000000000)    None                      0                           <-- differ
divide(1, 0)                                          None                      raises ValueError           <-- differ
divide(0, 0)                                          None                      raises ValueError           <-- differ
add(True, 1)                                          None                      2                           <-- differ
add(nan, 1)                                           None                      nan                         <-- differ
add(inf, 1)                                           None                      None                      
```

第 1 題的測試沒有規範的地方，兩個 agent／人各自做了不同的選擇：

| 行為 | AgentCalc | 我的 Q1Calc |
|---|---|---|
| 整數上限 | int64（agent 自己挑的） | int32 |
| 輸入是否檢查範圍 | 是（超過 int64 的輸入回傳 `None`） | 否（只檢查結果） |
| `divide(x, 0)` | 回傳 `None` | raise `ValueError` |
| `bool` 輸入 | 拒絕，回傳 `None` | 當成整數，`add(True,1)==2` |
| `NaN` 輸入 | 回傳 `None` | 回傳 `nan` |

結論：新 agent **沒有作弊**，寫出的是通用、結構乾淨的實作，而且它在回應中主動說明「range 是我自己選的，測試只說需要上限、沒說是哪個」。不過它在測試沒有規範的地方做了五個自己的決定，其中「拒絕超出範圍的輸入」違反了 `a - a == 0` 這種基本代數性質。範例測試（example-based tests）只能固定少數點；property-based／metamorphic 測試不需要知道正確答案，就能抓出規格的漏洞與實作之間的不一致，也讓我發現自己第 1 題的 Calc 有「溢位規則取決於型別」的問題。

---

## 附錄 A：最終 `Calc.py`（第 6 題）

```python
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

        return a % b

    def power(self, a, b):
        if not self._valid_inputs(a, b):
            return None

        if a == 0 and b < 0:
            raise ValueError("Cannot raise zero to a negative power")

        c = self._calculate(operator.pow, a, b)
        if isinstance(c, complex):
            raise ValueError("The result is not a real number")

        return c
```

## 附錄 B：所有測試 `CalcTest.py`（第 1 題 + 第 6 題）

```python
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
```

## 附錄 C：第 6 題各 cycle 的紅燈輸出（實作前）

### Cycle 1
```text
test_modulo (CalcTest.TestCalculator.test_modulo) ... ERROR

======================================================================
ERROR: test_modulo (CalcTest.TestCalculator.test_modulo)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\CalcTest.py", line 69, in test_modulo
    self.assertEqual(calc.modulo(7, 3), 1)  # Expect 7 % 3 = 1
                     ^^^^^^^^^^^
AttributeError: 'Calculator' object has no attribute 'modulo'

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (errors=1)
```
### Cycle 2
```text
test_modulo_by_zero (CalcTest.TestCalculator.test_modulo_by_zero) ... ERROR

======================================================================
ERROR: test_modulo_by_zero (CalcTest.TestCalculator.test_modulo_by_zero)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\CalcTest.py", line 81, in test_modulo_by_zero
    calc.modulo(7, 0)
    ~~~~~~~~~~~^^^^^^
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\Calc.py", line 77, in modulo
    return a % b
           ~~^~~
ZeroDivisionError: integer modulo by zero

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
```
### Cycle 3
```text
test_modulo_invalid_input (CalcTest.TestCalculator.test_modulo_invalid_input) ... ERROR

======================================================================
ERROR: test_modulo_invalid_input (CalcTest.TestCalculator.test_modulo_invalid_input)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\CalcTest.py", line 88, in test_modulo_invalid_input
    self.assertEqual(calc.modulo('7', 3), None)
                     ~~~~~~~~~~~^^^^^^^^
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\Calc.py", line 80, in modulo
    return a % b
           ~~^~~
TypeError: not all arguments converted during string formatting

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
```
### Cycle 4
```text
test_power (CalcTest.TestCalculator.test_power) ... ERROR

======================================================================
ERROR: test_power (CalcTest.TestCalculator.test_power)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\CalcTest.py", line 96, in test_power
    self.assertEqual(calc.power(2, 3), 8)  # Expect 2 ** 3 = 8
                     ^^^^^^^^^^
AttributeError: 'Calculator' object has no attribute 'power'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```
### Cycle 5
```text
test_power_negative_exponent (CalcTest.TestCalculator.test_power_negative_exponent) ... ERROR

======================================================================
ERROR: test_power_negative_exponent (CalcTest.TestCalculator.test_power_negative_exponent)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\CalcTest.py", line 113, in test_power_negative_exponent
    calc.power(0, -1)
    ~~~~~~~~~~^^^^^^^
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\Calc.py", line 87, in power
    return a ** b
           ~~^^~~
ZeroDivisionError: 0.0 cannot be raised to a negative power

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
```
### Cycle 6
```text
test_power_invalid_input (CalcTest.TestCalculator.test_power_invalid_input) ... ERROR

======================================================================
ERROR: test_power_invalid_input (CalcTest.TestCalculator.test_power_invalid_input)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\CalcTest.py", line 118, in test_power_invalid_input
    self.assertEqual(calc.power('2', 3), None)
                     ~~~~~~~~~~^^^^^^^^
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\Calc.py", line 90, in power
    return a ** b
           ~~^^~~
TypeError: unsupported operand type(s) for ** or pow(): 'str' and 'int'

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (errors=1)
```
### Cycle 7
```text
test_power_overflow (CalcTest.TestCalculator.test_power_overflow) ... FAIL

======================================================================
FAIL: test_power_overflow (CalcTest.TestCalculator.test_power_overflow)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\CalcTest.py", line 129, in test_power_overflow
    self.assertEqual(calc.power(2, 31), None)          # INT32_MAX + 1
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 2147483648 != None

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)
```
### Cycle 8
```text
test_power_no_real_result (CalcTest.TestCalculator.test_power_no_real_result) ... FAIL

======================================================================
FAIL: test_power_no_real_result (CalcTest.TestCalculator.test_power_no_real_result)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\josep\Documents\Software_Testing_2026\HW2\CalcTest.py", line 140, in test_power_no_real_result
    with self.assertRaises(ValueError):
         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

## 附錄 D：第 7 題新 agent 寫的 `Calc.py`

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

## 附錄 E：第 7 題 property-based／metamorphic 測試

```python
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
```

## 附錄 F：第 7 題差異探測腳本

```python
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
```

## 附錄 G：AI 使用紀錄（AI usage log）

### G.1 工具資訊

| 題目 | 工具 | 模型 | 版本 |
|---|---|---|---|
| 第 6 題 | Claude Code（Claude 桌面應用程式 Code 分頁） | Claude Opus 5.5（`claude-opus-5-5`） | Claude Code 2.1.274 |
| 第 7 題（寫 Calc） | Claude Code 子代理（general-purpose，全新 context） | Claude Opus 5.5（`claude-opus-5-5`） | Claude Code 2.1.274 |
| 第 7 題（property 測試） | 同第 6 題的主 session | 同上 | 同上 |
| 第 1 題 | 未使用 AI | — | — |

### G.2 第 6、7 題主 session：我的 prompt（原文）

**Prompt 1**（附上 `CalcTDD (AI agent).pdf`）：

```
請先閱讀這篇pdf檔案 目前已經解決第一題 請先幫我解決 第6和7題並寫成報告 其他題先判定可行性後再討論
```

之後的互動都是透過 agent 提出的選擇題進行。下表依序列出問題原文與我的回答原文：

| # | Agent 的問題（原文） | 我的回答（原文） |
|---|---|---|
| 1 | Q6(c) 決策 1：modulo 遇到負數運算元時，結果該怎麼算？ | Floored（跟 Python 一樣）(Recommended) |
| 2 | Q6(c) 決策 2：modulo 除數為 0 時要怎麼處理？ | raise ValueError (Recommended) |
| 3 | Q6(c) 決策 3：power(0, 0) 的結果是什麼？ | 回傳 1 (Recommended) |
| 4 | Q6(c) 決策 4：power 遇到負指數時回傳什麼？ | 回傳 float (Recommended) |
| 5 | Cycle 1 審查：test_modulo 已寫好且已確認失敗（AttributeError: no attribute 'modulo'）。它編碼了基本餘數與你選的 floored 負數規則。核准後我會先 commit 測試，再寫實作。是否核准？ | 核准，照此 commit |
| 6 | Cycle 2 審查：test_modulo_by_zero 已確認失敗（目前丟出 ZeroDivisionError，而非你決定的 ValueError）。我額外加了除數為 0.0（float）的情況。是否核准？ | 核准，照此 commit |
| 7 | Cycle 3 審查：test_modulo_invalid_input 已確認失敗（'7' % 3 被 Python 當成字串格式化而丟 TypeError）。注意：最後一行是我自行加的決策——modulo('7', 0) 先檢查型別而回傳 None（與 divide 的檢查順序相同）。是否核准？ | 核准，照此 commit |
| 8 | Cycle 4 審查：test_power 已確認失敗（no attribute 'power'），編碼基本次方與你決定的 power(0, 0) == 1。是否核准？ | 核准，照此 commit |
| 9 | Cycle 5 審查：test_power_negative_exponent 已確認失敗。請注意：「負指數回傳 float」那幾行在 Cycle 4 的 a ** b 下其實已經會過，實際失敗的只有 power(0, -1)（目前丟 ZeroDivisionError，你先前選的是 ValueError）。是否核准？ | 核准，照此 commit |
| 10 | Cycle 6 審查：test_power_invalid_input 已確認失敗（'2' ** 3 丟 TypeError）。最後一行同樣是我自行加的順序決策：先檢查型別，再套用「0 的負次方」規則。是否核准？ | 核准，照此 commit |
| 11 | Cycle 7 審查：test_power_overflow 已確認失敗（power(2, 31) 回傳 2147483648，超過 int32）。我沿用 Q1 的 int32 範圍與「溢位回傳 None」規則，並測了邊界 INT32_MIN。是否核准？ | 核准，照此 commit |
| 12 | 負底數配上非整數指數（如 power(-8, 0.5)）在實數範圍無解，Python 會回傳 complex。Calc 該怎麼處理？ | raise ValueError (Recommended) |
| 13 | Cycle 8 審查：test_power_no_real_result 已確認失敗（目前回傳 complex、沒丟 ValueError）。我另加了一個對照案例：power(-2, 2.0) 指數雖是 float 但為整數值，仍應回傳 4.0。是否核准？ | 核准，照此 commit |

選項的完整說明與每次審查時附的測試預覽，都在匯出的對話紀錄中。

### G.3 Agent 的完整回應

主 session 的完整回應，包括每一次工具呼叫、終端機輸出與文字回覆，篇幅很長，所以用 Claude 桌面應用程式的 Export 功能匯出成檔案，作為本附錄的一部分一併繳交：

- 匯出檔：`C:\Users\josep\Downloads\session-export-1793024991462.zip`（含主 session 與第 7 題子代理的完整對話紀錄）
- 這份匯出是在報告組裝前產生的。之後產生報告、提交 git 的步驟，需要在對話結束後從 session 選單再 Export 一次才會包含進去。

### G.4 第 7 題新 agent session：prompt 與完整回應（原文）

**Prompt（原文）：**

```text
I have a Python unit test file for a calculator, but I don't have the implementation. Please write the implementation so that all tests pass.

Working folder (use ONLY this folder; do not read, search, or list any other files or directories on this machine):
C:/Users/josep/AppData/Local/Temp/claude/C--Users-josep-Documents-Software-Testing-2026-HW2/d27258f4-686c-4fcd-859c-756ca0e0bd54/scratchpad/q7_agent

The test file is CalcTest.py in that folder. It imports `from Calc import Calculator`, so create Calc.py in the same folder. Do not modify CalcTest.py.

Run the tests with this interpreter, from inside the working folder:
C:/Users/josep/Documents/Software_Testing_2026/HW2/.venv/Scripts/python.exe -m unittest -v CalcTest

When you are done, reply with: (1) the full final contents of Calc.py, (2) the full test output of your last run, and (3) a short explanation of the design decisions you made.
```

**完整回應（原文）：**

> All 4 tests pass. I created Calc.py and left CalcTest.py unchanged.
>
> File: C:/Users/josep/AppData/Local/Temp/claude/C--Users-josep-Documents-Software-Testing-2026-HW2/d27258f4-686c-4fcd-859c-756ca0e0bd54/scratchpad/q7_agent/Calc.py
>
> (1) Final contents of Calc.py
>
> ```python
> import math
>
> # Integer results must fit in a signed 64-bit integer; float results must be finite.
> INT_MIN = -(2 ** 63)
> INT_MAX = 2 ** 63 - 1
>
>
> class Calculator:
>     """A simple calculator that returns None for invalid input or out-of-range results."""
>
>     @staticmethod
>     def _is_valid_number(value):
>         # Accept only real ints and floats; bool is a subclass of int but is not a number here.
>         if isinstance(value, bool) or not isinstance(value, (int, float)):
>             return False
>         if isinstance(value, float):
>             return math.isfinite(value)
>         return INT_MIN <= value <= INT_MAX
>
>     @classmethod
>     def _check_result(cls, result):
>         return result if cls._is_valid_number(result) else None
>
>     def _compute(self, a, b, operation):
>         if not (self._is_valid_number(a) and self._is_valid_number(b)):
>             return None
>         try:
>             result = operation(a, b)
>         except (OverflowError, ZeroDivisionError):
>             return None
>         return self._check_result(result)
>
>     def add(self, a, b):
>         return self._compute(a, b, lambda x, y: x + y)
>
>     def subtract(self, a, b):
>         return self._compute(a, b, lambda x, y: x - y)
>
>     def multiply(self, a, b):
>         return self._compute(a, b, lambda x, y: x * y)
>
>     def divide(self, a, b):
>         return self._compute(a, b, lambda x, y: x / y)
> ```
>
> (2) Test output from the last run (`python.exe -m unittest -v CalcTest`, run inside the working folder)
>
> ```
> test_add (CalcTest.TestCalculator.test_add) ... ok
> test_divide (CalcTest.TestCalculator.test_divide) ... ok
> test_multiply (CalcTest.TestCalculator.test_multiply) ... ok
> test_subtract (CalcTest.TestCalculator.test_subtract) ... ok
>
> ----------------------------------------------------------------------
> Ran 4 tests in 0.000s
>
> OK
> ```
>
> (3) Design decisions
>
> - **None means error.** The tests expect `None` instead of an exception for bad input, so every invalid case returns `None`. That covers non-numbers, overflow, and division by zero.
> - **Type check.** Only `int` and `float` are accepted. Strings like `'2'` or `"documents"` give `None`. I also chose to reject `bool`, because Python treats `True`/`False` as ints, which isn't what a calculator user means.
> - **Range limits.** The tests need `10**100 + 10**100` and `10**100 * 10**100` to return `None`. Python ints never overflow by themselves, so the class has to set a limit. I picked the signed 64-bit integer range for both inputs and results. This is my own choice: the tests only say a limit is needed, not which one.
> - **Float limits.** Float inputs and results must be finite, so NaN and infinity give `None`. This handles `1e308 + 1e308`, `1e308 * 1e308` and `1e308 / 1e-308`, which all overflow to infinity. `OverflowError` is also caught in case Python raises it instead.
> - **Divide by zero.** It returns `None`, which is consistent with the rest. The tests don't check this case.
> - **Division result type.** `divide` uses true division, so `10 / 2` returns `5.0`. That passes `assertEqual(..., 5)`.
> - **Shared code.** All four operations go through one `_compute` helper, so the checks are written once and behave the same for each operation.
