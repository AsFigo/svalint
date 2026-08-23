# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class MissingEndLblSEQ(AsFigoLintRule):
    """
    **DBG_MISS_END_LBL_SEQ** — Sequence declaration must have an end-label.

    **Rationale**: End-labels (e.g., ``endsequence: s_my_seq``) visually bracket
    the sequence body and improve navigability in large files. They are especially
    valuable in deeply nested or multi-line sequence definitions.

    **Violation**::

        sequence s_req_rise;
            @(posedge clk) ##1 $rose(req);
        endsequence

    **Correct usage**::

        sequence s_req_rise;
            @(posedge clk) ##1 $rose(req);
        endsequence: s_req_rise

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        # Store the linter instance
        self.ruleID = "DBG_MISS_END_LBL_SEQ"

    def apply(
        self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData
    ):
        for curNode in data.tree.iter_find_all(
            {"tag": "kSequenceDeclaration"}):
            lvSvaCode = curNode.text
            lvLastElem = curNode.descendants[-1]
            if (not lvLastElem.text):
                message = self.formatViolationMessage(
                    description="Sequence declaration is missing an end-label.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Add 'endsequence: <name>' to close the sequence declaration.",
                )
                self.linter.logViolation(self.ruleID, message)
