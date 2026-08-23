# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

class MissingLabelChk(AsFigoLintRule):
    """
    **ASSERT_MISSING_LABEL** — Assert statements must have a label.

    **Rationale**: Labels on assertions enable targeted waveform search, log
    filtering, and coverage reporting. Without a label, tracing a failing
    assertion back to its source in a large design is time-consuming. Most
    formal and simulation tools can filter and report assertions by label.

    **Violation**::

        assert property (@(posedge clk) req |-> ##[1:3] ack);

    **Correct usage**::

        a_req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack);

    **Severity**: ERROR
    """
  
    def __init__(self, linter):
        self.linter = linter  # Store the linter instance
        self.ruleID = "ASSERT_MISSING_LABEL"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
          lvSvaCode = curNode.text
          lvAsrtLabel =  curNode.children[0]
          if (( ":" not in lvAsrtLabel.text)):
                message = self.formatViolationMessage(
                    description="Assert statement is missing a label.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Add an 'a_' prefixed label: 'a_<name>: assert property ...'",
                )
                self.linter.logViolation(self.ruleID, message)


