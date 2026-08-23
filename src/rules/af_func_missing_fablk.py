# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------
from af_lint_rule import AsFigoLintRule

class FuncMissingFABLK(AsFigoLintRule):
    """
    **FUNC_MISSING_FAIL_ABLK** — Assert statement must have a fail action block.

    **Rationale**: Without an ``else`` fail action block, a failing assertion
    produces only a generic simulator error with no design-context information.
    A fail action block with ``$error`` or ``$fatal`` lets you print signal
    values, timestamps, and custom messages, drastically reducing debug time.

    **Violation**::

        a_req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack);

    **Correct usage**::

        a_req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack)
            else $error("req=%0b ack=%0b", req, ack);

    **Severity**: ERROR
    """
  
    def __init__(self, linter):
        self.linter = linter  # Store the linter instance
        self.ruleID = "FUNC_MISSING_FAIL_ABLK"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text

            lvAsrtIter = curNode.iter_find_all({"tag": "kAssertPropertyStatement"})
            lvAsrtProp = next(lvAsrtIter, None)
            if lvAsrtProp is None:
                continue

            lvAsrtFailAblkNode = curNode.iter_find_all({"tag": "kElseClause"})
            lvAsrtFailAblkNodeNxt = next(lvAsrtFailAblkNode, None)
            if lvAsrtFailAblkNodeNxt is None:
                message = self.formatViolationMessage(
                    description="Assert statement is missing a fail action block — errors will produce only a generic simulator message.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Add 'else $error(\"...\")' after the assert property to log signal values on failure.",
                )
                self.linter.logViolation(self.ruleID, message)

