# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------
from af_lint_rule import AsFigoLintRule

class FuncOLAPInCoverProp(AsFigoLintRule):
    """
    **FUNC_NO_OLAP_COVER** — Avoid overlapping implication (``|->``) in cover property.

    **Rationale**: Using ``|->`` with a ``cover property`` directive can collect
    vacuous coverage when the antecedent does not hold, giving a false sense of
    coverage completeness. Use ``##0`` for same-cycle coverage or restructure
    without implication.

    **Violation**::

        c_req_ack: cover property (@(posedge clk) req |-> ack);

    **Correct usage**::

        c_req_ack: cover property (@(posedge clk) req ##0 ack);

    **Severity**: ERROR
    """
  
    def __init__(self, linter):
        self.linter = linter  # Store the linter instance
        self.ruleID = "FUNC_NO_OLAP_COVER"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kCoverPropertyStatement"}):
            lvSvaCode = curNode.text
            lvNonOlapImplG = curNode.iter_find_all({"tag": "|->"})
            if (len(list(lvNonOlapImplG)) > 0):
                message = self.formatViolationMessage(
                    description="Overlapping implication '|->' used inside 'cover property' — collects vacuous coverage when antecedent does not hold.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Replace '|->' with '##0' for direct same-cycle coverage.",
                )
                self.linter.logViolation(self.ruleID, message)

