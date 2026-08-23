# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class UseRealTimeVsTime(AsFigoLintRule):
    """
    **FUNC_AVOID_DOLLAR_TIME** — Use ``$realtime`` instead of ``$time`` in SVA.

    **Rationale**: ``$time`` returns an integer truncated to simulation time
    precision, losing sub-precision timing information. ``$realtime`` returns
    a real-valued time that accurately reflects actual simulation time, which
    is essential for timing assertions where sub-precision differences matter.

    **Violation**::

        a_timeout: assert property (@(posedge clk)
            start |-> ($time - t0 < TIMEOUT));

    **Correct usage**::

        a_timeout: assert property (@(posedge clk)
            start |-> ($realtime - t0 < TIMEOUT));

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        # Store the linter instance
        self.ruleID = "FUNC_AVOID_DOLLAR_TIME"

    def apply(
        self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData
    ):
        for curNode in data.tree.iter_find_all(
            {"tag": "kPropertyDeclaration"}
        ):
            lvSvaCode = curNode.text
            lvSysTFCall = curNode.iter_find_all({"tag": "kSystemTFCall"})
            for curSysTFName in lvSysTFCall:
                lvSysTFNameIter = curSysTFName.iter_find_all({"tag": "SystemTFIdentifier"})
                lvCurSysTFName = next(lvSysTFNameIter)
                if ('$time' in lvCurSysTFName.text):
                    message = self.formatViolationMessage(
                        description="'$time' used inside SVA property — returns a truncated integer that loses sub-precision timing information.",
                        code_snippet=lvSvaCode,
                        fix_suggestion="Replace '$time' with '$realtime' for accurate real-valued simulation time.",
                    )
                    self.linter.logViolation(self.ruleID, message)
