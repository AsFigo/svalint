# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class AvoidWeakUntilWithRule(AsFigoLintRule):
    """
    **FUNC_AVOID_WEAK_UNTIL_WITH** — Avoid weak ``until_with``; use ``s_until_with``.

    **Rationale**: Like ``until``, the weak ``until_with`` operator passes vacuously
    at simulation end if the termination condition is never reached. Use
    ``s_until_with`` (strong until_with) to enforce that the endpoint condition
    is strictly observed within the simulation run.

    **Violation**::

        a_hold: assert property (@(posedge clk) busy until_with ready);

    **Correct usage**::

        a_hold: assert property (@(posedge clk) busy s_until_with ready);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_WEAK_UNTIL_WITH"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text

            for curUntilNode in curNode.iter_find_all({"tag": "until_with"}):
                if curUntilNode.text.strip() == "until_with":
                    message = self.formatViolationMessage(
                        description="Weak 'until_with' operator found — assertion passes vacuously if simulation ends before termination condition is met.",
                        code_snippet=lvSvaCode,
                        fix_suggestion="Replace 'until_with' with 's_until_with' to enforce liveness.",
                    )
                    self.linter.logViolation(self.ruleID, message)
