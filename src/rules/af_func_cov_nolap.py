# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------
from af_lint_rule import AsFigoLintRule

class FuncNOLAPInCoverProp(AsFigoLintRule):
    """
    **FUNC_NO_NON_OLAP_COVER** — Avoid non-overlapping implication (``|=>``) in cover property.

    **Rationale**: Using ``|=>`` with a ``cover property`` directive causes coverage
    to be reported one cycle after the trigger, collecting vacuous or false-positive
    hits. The cover directive should express direct observability; use ``##1``
    or restructure the property to avoid ``|=>``.

    **Violation**::

        c_req_ack: cover property (@(posedge clk) req |=> ack);

    **Correct usage**::

        c_req_ack: cover property (@(posedge clk) req ##1 ack);

    **Severity**: ERROR
    """
  
    def __init__(self, linter):
        self.linter = linter  # Store the linter instance
        self.ruleID = "FUNC_NO_NON_OLAP_COVER"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kCoverPropertyStatement"}):
            lvSvaCode = curNode.text
            lvNonOlapImplG = curNode.iter_find_all({"tag": "|=>"})
            if (len(list(lvNonOlapImplG)) > 0):
                message = self.formatViolationMessage(
                    description="Non-overlapping implication '|=>' used inside 'cover property' — reports coverage one cycle after the trigger, collecting false-positive hits.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Replace '|=>' with '##1' or restructure the property without an implication operator.",
                )
                self.linter.logViolation(self.ruleID, message)

