# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoFirstMatchOperInAsrt(AsFigoLintRule):
    """
    **STYLE_AVOID_FIRST_MATCH_A** — Avoid ``first_match()`` in SVA for formal verification.

    **Rationale**: ``first_match()`` creates multiple concurrent threads that
    formal tools must evaluate simultaneously, potentially causing state-space
    explosion and degraded performance. It also adds complexity that makes
    failures harder to debug. While acceptable in simulation, it is generally
    discouraged for formal analysis.

    **Violation**::

        a_req: assert property (@(posedge clk)
            first_match(req ##[1:5] ack) |-> done);

    **Correct usage**: Restructure using deterministic timing or goto repetition
    to eliminate the need for ``first_match``.

    **Severity**: ERROR

    **References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "STYLE_AVOID_FIRST_MATCH_A"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text
            lvFirstMatchList = list(curNode.iter_find_all({"tag": "first_match"}))
            if len(lvFirstMatchList) > 0:
                message = self.formatViolationMessage(
                    description="'first_match()' found in SVA — creates multiple concurrent threads, causing state-space explosion in formal tools.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Restructure using deterministic timing or goto repetition '[->1]' to eliminate 'first_match'.",
                )
                self.linter.logViolation(self.ruleID, message)
