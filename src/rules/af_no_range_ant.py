# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoRangeInAntAsrt(AsFigoLintRule):
    """
    **STYLE_AVOID_RANGE_IN_ANT_A** — Avoid cycle ranges in assertion antecedent.

    **Rationale**: Range repetition in an antecedent (e.g., ``##[1:10]``) creates
    multiple concurrent threads, one per possible delay value. Only one thread
    can be non-vacuous while others generate spurious vacuous passes. Use goto
    repetition (``[->1]``) to ensure exactly one match thread.

    **Violation**::

        a_rdy: assert property (@(posedge clk)
            $rose(req) ##[1:10] rdy |-> ##[1:2] ack);

    **Correct usage**::

        a_rdy: assert property (@(posedge clk)
            $rose(req) ##1 rdy[->1] |-> ##[1:2] ack);

    **Severity**: ERROR

    **References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk §2.2.2.2
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "STYLE_AVOID_RANGE_IN_ANT_A"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text
            for curImplNode in curNode.iter_find_all({"tag": "kPropertyImplicationList"}):
                lvImplAntNode = curImplNode.children[0]
                lvAntRangeList = list(lvImplAntNode.iter_find_all({"tag": "kCycleRange"}))
                if len(lvAntRangeList) > 0:
                    message = self.formatViolationMessage(
                        description="Cycle range '##[lo:hi]' in assertion antecedent creates multiple concurrent threads — only one can be non-vacuous.",
                        code_snippet=lvSvaCode,
                        fix_suggestion="Replace '##[1:N] sig' with '##1 sig[->1]' to ensure exactly one match thread.",
                    )
                    self.linter.logViolation(self.ruleID, message)
