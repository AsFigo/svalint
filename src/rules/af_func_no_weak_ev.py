# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class AvoidWeakEventuallyRule(AsFigoLintRule):
    """
    **FUNC_AVOID_WEAK_EVENTUALLY** — Avoid weak ``eventually``; use ``s_eventually``.

    **Rationale**: The weak ``eventually`` operator passes vacuously if the
    simulation ends before the condition becomes true, making liveness assertions
    meaningless — they can never fail. Use ``s_eventually`` (strong eventually)
    to enforce that the condition must be observed within the simulation run.

    **Violation**::

        a_done: assert property (@(posedge clk) start |-> eventually done);

    **Correct usage**::

        a_done: assert property (@(posedge clk) start |-> s_eventually done);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_WEAK_EVENTUALLY"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text

            for curEventuallyNode in curNode.iter_find_all({"tag": "eventually"}):
                if curEventuallyNode.text.strip() == "eventually":
                    message = self.formatViolationMessage(
                        description="Weak 'eventually' operator found — assertion passes vacuously if simulation ends before condition becomes true.",
                        code_snippet=lvSvaCode,
                        fix_suggestion="Replace 'eventually' with 's_eventually' to enforce liveness.",
                    )
                    self.linter.logViolation(self.ruleID, message)
