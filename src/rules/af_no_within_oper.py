# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoWithinOperInAsrt(AsFigoLintRule):
    """
    **STYLE_AVOID_WITHIN_A** — Avoid the ``within`` sequence operator in SVA.

    **Rationale**: The ``within`` operator, while part of the LRM, has misleading
    semantics that frequently cause incorrect assertion intent. Its interaction
    with threading and overlap semantics is non-intuitive, leading to assertions
    that appear correct but check something different from what was intended.
    Explicit sequence composition using ``##`` and repetition operators is clearer
    and more portable.

    **Violation**::

        a_ack: assert property (@(posedge clk)
            (req ##1 ack) within (start ##[1:10] stop));

    **Correct usage**: Express the temporal relationship explicitly using ``##``
    delays and repetition without relying on ``within``.

    **Severity**: ERROR

    **References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "STYLE_AVOID_WITHIN_A"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text
            lvWithinList = list(curNode.iter_find_all({"tag": "within"}))
            if len(lvWithinList) > 0:
                message = self.formatViolationMessage(
                    description="'within' sequence operator found in SVA — semantics are non-intuitive and frequently cause incorrect assertion intent.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Express the temporal relationship explicitly using '##' delays and repetition operators.",
                )
                self.linter.logViolation(self.ruleID, message)
