# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------
from af_lint_rule import AsFigoLintRule

class ReuseNoOneLinerFABLK(AsFigoLintRule):
    """
    **REUSE_NO_ONE_LINER_FAIL_ABLK** — Fail action block must use ``begin/end``, not a one-liner.

    **Rationale**: A one-liner fail action block cannot be extended without
    structural refactoring. Using ``begin/end`` from the start allows additional
    debug statements, coverage increments, or task calls to be added later
    without changing the block structure, improving long-term reusability.

    **Violation**::

        a_req_ack: assert property (@(posedge clk) req |-> ack)
            else $error("FAIL");

    **Correct usage**::

        a_req_ack: assert property (@(posedge clk) req |-> ack)
            else begin
                $error("FAIL: req=%0b ack=%0b", req, ack);
            end

    **Severity**: ERROR
    """
  
    def __init__(self, linter):
        self.linter = linter  # Store the linter instance
        self.ruleID = "REUSE_NO_ONE_LINER_FAIL_ABLK"

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
                continue
            lvFablkType = lvAsrtFailAblkNodeNxt.descendants[2]
            lvFablkTypeName = str(lvFablkType)
            if ('[kSeqBlock]' not in lvFablkTypeName):
                message = self.formatViolationMessage(
                    description="Fail action block is a one-liner — cannot be extended without structural refactoring.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Wrap the fail action in 'begin/end': 'else begin $error(...); end'",
                )
                self.linter.logViolation(self.ruleID, message)

