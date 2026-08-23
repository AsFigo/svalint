# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# Author: Himank Gangwal, Sep 02, 2025
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

class AvoidPopBkSVA(AsFigoLintRule):
    """
    **COMPAT_NO_POP_BACK_SVA** — Avoid queue method ``pop_back()`` inside SVA.

    **Rationale**: IEEE LRM 1800 §16.6 requires sampled queue elements to persist
    until assertion evaluation completes, but many EDA tools restrict or prohibit
    queue method calls inside SVA expressions for performance reasons. Avoid
    ``pop_back()`` in SVA to ensure broad simulator and formal tool compatibility.

    **Violation**::

        a_data: assert property (@(posedge clk)
            $rose(valid) |-> (q.pop_back() == 8'hA5));

    **Correct usage**: Sample the queue element into a logic variable in an
    always block and reference that variable in SVA.

    **Severity**: ERROR

    **References**: IEEE 1800 LRM §16.6. Rule suggested by Ben Cohen.
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "COMPAT_NO_POP_BACK_SVA"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": ["kPropertyDeclaration"]}):
            for hierNode in curNode.iter_find_all({"tag": ["kHierarchyExtension"]}):
                if self._containsPopBack(hierNode):
                    message = self.formatViolationMessage(
                        description="Queue method '.pop_back()' used inside SVA — many EDA tools restrict or prohibit this (IEEE 1800 §16.6).",
                        code_snippet=curNode.text,
                        fix_suggestion="Sample the queue element in an always block and reference a logic variable in SVA.",
                    )
                    self.linter.logViolation(self.ruleID, message)

    def _containsPopBack(self, node):
        """Checks if a node or its children contain 'pop_back' usage."""
        if hasattr(node, 'text') and 'pop_back' in node.text:
            return True
        for identifier in node.iter_find_all({"tag": "SymbolIdentifier"}):
            if identifier.text == "pop_back":
                return True
        return False
