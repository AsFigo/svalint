# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class MissingEndLblProp(AsFigoLintRule):
    """
    **DBG_MISS_END_LBL_PROP** — Property declaration must have an end-label.

    **Rationale**: End-labels (e.g., ``endproperty: p_my_prop``) create a visual
    bracket around the property body, making it easier to identify boundaries in
    large files and enabling consistent navigation in editors. They are especially
    valuable when properties span many lines.

    **Violation**::

        property p_req_ack;
            @(posedge clk) req |-> ##[1:3] ack;
        endproperty

    **Correct usage**::

        property p_req_ack;
            @(posedge clk) req |-> ##[1:3] ack;
        endproperty: p_req_ack

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        # Store the linter instance
        self.ruleID = "DBG_MISS_END_LBL_PROP"

    def apply(
        self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData
    ):
        for curNode in data.tree.iter_find_all(
            {"tag": "kPropertyDeclaration"}):
            lvSvaCode = curNode.text
            lvLastElem = curNode.descendants[-1]
            if (not lvLastElem.text):
                message = self.formatViolationMessage(
                    description="Property declaration is missing an end-label.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Add 'endproperty: <name>' to close the property declaration.",
                )
                self.linter.logViolation(self.ruleID, message)
