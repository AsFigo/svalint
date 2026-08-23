# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoUBRangeInConseqAsrt(AsFigoLintRule):
    """
    **FUNC_AVOID_$_RANGE_IN_CONSEQ_A** — Avoid unbounded ``##[0:$]`` range in assertion consequent.

    **Rationale**: An assertion with an infinite range (``$``) in its consequent
    can never FAIL — it will always find a future cycle where the condition holds,
    or wait indefinitely. This makes the assertion useless for verification. Use
    a deterministic bounded delay instead.

    **Violation**::

        a_ack: assert property (@(posedge clk) $rose(req) |-> ##[0:$] ack);

    **Correct usage**::

        a_ack: assert property (@(posedge clk) $rose(req) |-> ##[1:8] ack);

    **Severity**: ERROR

    **References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_$_RANGE_IN_CONSEQ_A"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text
            for curImplNode in curNode.iter_find_all({"tag": "|->"}):
                lvImplCnseqNode = curImplNode.siblings[1]
                lvRangeG = lvImplCnseqNode.iter_find_all({"tag": "kCycleDelayRange"})
                for curDelRangeNode in lvRangeG:
                    lvCnseqUBRangeG = curDelRangeNode.iter_find_all({"tag": "$"})
                    lvCnseqUBRangeList = list(lvCnseqUBRangeG)
                    if len(lvCnseqUBRangeList) > 0:
                        message = self.formatViolationMessage(
                            description="Unbounded '##[0:$]' range in assertion consequent — assertion can never fail.",
                            code_snippet=lvSvaCode,
                            fix_suggestion="Replace '##[0:$]' with a bounded range, e.g., '##[1:8]'.",
                        )
                        self.linter.logViolation(self.ruleID, message)
