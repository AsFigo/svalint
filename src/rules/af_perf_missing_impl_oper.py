# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------
from af_lint_rule import AsFigoLintRule


class MissingImplicationOper(AsFigoLintRule):
    """
    **PERF_MISSING_IMPLICATION_OPER** — SVA property without an implication operator hurts simulation performance.

    **Rationale**: A property without ``|->`` or ``|=>`` evaluates its consequent
    on every active clock edge, creating a continuous evaluation thread with no
    gating condition. This significantly degrades simulation performance on large
    designs. Add an antecedent with an implication operator to gate evaluation
    on meaningful trigger conditions. Exception: the ``forbid`` property style.

    **Violation**::

        p_no_x: property (@(posedge clk) !$isunknown(data));

    **Correct usage**::

        p_no_x: property (@(posedge clk) valid |-> !$isunknown(data));

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PERF_MISSING_IMPLICATION_OPER"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            lvSvaCode = curNode.text
            lvOlapImplG = curNode.iter_find_all({"tag": "|->"})
            lvNonOlapImplG = curNode.iter_find_all({"tag": "|=>"})
            lvNumImplOper = len(list(lvOlapImplG)) + len(list(lvNonOlapImplG))
            if lvNumImplOper == 0:
                message = self.formatViolationMessage(
                    description="SVA property has no implication operator ('|->' or '|=>') — consequent evaluates on every active clock edge.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Add an antecedent with '|->' or '|=>' to gate evaluation on a meaningful trigger condition.",
                )
                self.linter.logViolation(self.ruleID, message)
