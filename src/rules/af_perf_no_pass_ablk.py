# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------
from af_lint_rule import AsFigoLintRule

class PerfNoPABlk(AsFigoLintRule):
    """
    **PERF_PASS_ACT_BLK** — Assert statement must not have a pass action block.

    **Rationale**: A pass action block executes on every successful assertion
    evaluation, which can occur millions of times per simulation run. This
    severely degrades simulation performance. Pass action blocks are almost
    never needed; remove them or use coverage-based approaches instead.

    **Violation**::

        a_req_ack: assert property (@(posedge clk) req |-> ack)
            $info("pass");

    **Correct usage**::

        a_req_ack: assert property (@(posedge clk) req |-> ack)
            else $error("FAIL: req=%0b ack=%0b", req, ack);

    **Severity**: ERROR
    """
  
    def __init__(self, linter):
        self.linter = linter  # Store the linter instance
        self.ruleID = "PERF_PASS_ACT_BLK"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = curNode.text

            lvAsrtPassAblkNode = curNode.iter_find_all({"tag": "kAssertPropertyBody"})
            lvAsrtPassAblkNodeNxt = next(lvAsrtPassAblkNode, None)
            if lvAsrtPassAblkNodeNxt is None:
                continue  
            lvNullNode = lvAsrtPassAblkNodeNxt.iter_find_all({"tag": "kNullStatement"})
            lvNullNodeList = list(lvNullNode)


            if (len(lvAsrtPassAblkNodeNxt.text) > 1):
                message = self.formatViolationMessage(
                    description="Pass action block found in assert statement — executes on every successful evaluation, severely degrading simulation performance.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Remove the pass action block. Use coverage directives instead if observability is needed.",
                )
                self.linter.logViolation(self.ruleID, message)

