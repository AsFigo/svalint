# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoUBRangeInAntAsrt(AsFigoLintRule):
    """
    **PERF_AVOID_$_RANGE_IN_ANT_A** — Avoid unbounded ``##[1:$]`` range in assertion antecedent.

    **Rationale**: An unbounded range in the antecedent forces the tool to spawn
    and maintain an unbounded number of concurrent threads, one per possible cycle
    count. This causes state-space explosion in formal tools and significant
    slowdown in simulation. Use a finite bound based on expected design behavior.

    **Violation**::

        a_ack: assert property (@(posedge clk)
            req ##[1:$] rdy |-> ack);

    **Correct usage**::

        a_ack: assert property (@(posedge clk)
            req ##[1:10] rdy |-> ack);

    **Severity**: ERROR

    **References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PERF_AVOID_$_RANGE_IN_ANT_A"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text
            for curImplNode in curNode.iter_find_all({"tag": "kPropertyImplicationList"}):
                lvImplAntNode = curImplNode.children[0]
                lvAntRangeG = lvImplAntNode.iter_find_all({"tag": "kCycleDelayRange"})
                for curDelRangeNode in lvAntRangeG:
                    lvAntUBRangeList = list(curDelRangeNode.iter_find_all({"tag": "$"}))
                    if len(lvAntUBRangeList) > 0:
                        message = self.formatViolationMessage(
                            description="Unbounded '##[1:$]' range in assertion antecedent — spawns unbounded concurrent threads causing state-space explosion.",
                            code_snippet=lvSvaCode,
                            fix_suggestion="Replace '##[1:$]' with a finite bound, e.g., '##[1:10]'.",
                        )
                        self.linter.logViolation(self.ruleID, message)
