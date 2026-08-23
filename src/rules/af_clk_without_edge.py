# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class ClkWithoutEdge(AsFigoLintRule):
    """
    **STYLE_NO_CLK_WITHOUT_EDGE** — Avoid ``@(clk)`` as a clocking event; use ``posedge`` or ``negedge``.

    **Rationale**: A clocking event ``@(clk)`` without an edge qualifier samples
    both the rising and falling edges of the clock. This is almost never the
    intended behaviour in SVA and leads to the assertion firing twice per cycle,
    producing confusing and often spurious results.

    **Violation**::

        p_req_gnt: property (@(clk) req |-> ##1 gnt);

    **Correct usage**::

        p_req_gnt: property (@(posedge clk) req |-> ##1 gnt);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "STYLE_NO_CLK_WITHOUT_EDGE"

    def _checkEventExpressions(self, topNode, lvSvaCode):
        for evtExprNode in topNode.iter_find_all({"tag": "kEventExpression"}):
            lvChildren = getattr(evtExprNode, "children", [])
            if not lvChildren:
                continue
            lvFirstText = getattr(lvChildren[0], "text", "").strip()
            if lvFirstText not in ("posedge", "negedge"):
                message = self.formatViolationMessage(
                    description="Clocking event '@(clk)' used without 'posedge' or 'negedge' — samples both edges, firing twice per clock cycle.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Replace '@(clk)' with '@(posedge clk)' or '@(negedge clk)'.",
                )
                self.linter.logViolation(self.ruleID, message)
                return  # One violation per top-level node

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for propNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            self._checkEventExpressions(propNode, propNode.text)

        for assertNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            self._checkEventExpressions(assertNode, assertNode.text)
