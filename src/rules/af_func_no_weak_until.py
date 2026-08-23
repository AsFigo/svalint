# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class AvoidWeakUntilRule(AsFigoLintRule):
    """
    **FUNC_AVOID_WEAK_UNTIL** — Avoid weak ``until``; use ``s_until``.

    **Rationale**: The weak ``until`` operator allows non-terminating evaluation —
    if the simulation ends before the termination condition is met, the assertion
    passes vacuously. Use ``s_until`` (strong until) to guarantee the termination
    condition is actually observed within the simulation run.

    **Violation**::

        a_hold: assert property (@(posedge clk) busy until ready);

    **Correct usage**::

        a_hold: assert property (@(posedge clk) busy s_until ready);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_WEAK_UNTIL"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text

            for curUntilNode in curNode.iter_find_all({"tag": "until"}):
                if curUntilNode.text.strip() == "until":
                    message = self.formatViolationMessage(
                        description="Weak 'until' operator found — assertion passes vacuously if simulation ends before termination condition is met.",
                        code_snippet=lvSvaCode,
                        fix_suggestion="Replace 'until' with 's_until' to enforce liveness.",
                    )
                    self.linter.logViolation(self.ruleID, message)
