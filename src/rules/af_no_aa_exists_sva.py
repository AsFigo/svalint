# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# Author: Himank Gangwal, Sep 02, 2025
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

class AvoidAAExistsSVA(AsFigoLintRule):
    """
    **NO_AA_EXISTS_SVA** — Avoid associative array ``exists()`` method inside SVA.

    **Rationale**: IEEE LRM 1800 §16.6 requires sampled associative array elements
    to persist until assertion evaluation completes, but many EDA tools have not
    fully adopted this requirement and impose restrictions or prohibit it entirely.
    Avoid ``exists()`` inside SVA to maintain broad tool compatibility.

    **Violation**::

        a_mem: assert property (@(posedge clk)
            (valid, v=mem.exists(addr)) |-> v);

    **Correct usage**: Sample the ``exists()`` result into a logic signal in an
    always block and reference that signal in SVA.

    **Severity**: ERROR

    **References**: IEEE 1800 LRM §16.6. Rule suggested by Ben Cohen.
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "NO_AA_EXISTS_SVA"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": ["kPropertyDeclaration"]}):
            for hierNode in curNode.iter_find_all({"tag": ["kHierarchyExtension"]}):
                if self._containsExists(hierNode):
                    message = self.formatViolationMessage(
                        description="Associative array '.exists()' used inside SVA — many EDA tools restrict or prohibit this (IEEE 1800 §16.6).",
                        code_snippet=curNode.text,
                        fix_suggestion="Sample the exists() result into a logic signal in an always block and reference that signal in SVA.",
                    )
                    self.linter.logViolation(self.ruleID, message)

    def _containsExists(self, node):
        """Checks if a node or its children contain 'exists' usage."""
        if hasattr(node, 'text') and 'exists' in node.text:
            return True
        for identifier in node.iter_find_all({"tag": "SymbolIdentifier"}):
            if identifier.text == "exists":
                return True
        return False
