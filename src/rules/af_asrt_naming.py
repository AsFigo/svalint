# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# Author: Himank Gangwal, Sep 02, 2025
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

class AssertNaming(AsFigoLintRule):
    """
    **ASSERT_NAMING** — Assert label must start with ``a_``.

    **Rationale**: A consistent ``a_`` prefix on assertion labels allows engineers
    to instantly distinguish assertions from assumptions (``m_``) and cover
    directives (``c_``) in log files, waveforms, and formal reports without
    reading the full directive syntax.

    **Violation**::

        req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack);

    **Correct usage**::

        a_req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack);

    **Severity**: WARNING
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "ASSERT_NAMING"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvLabel = curNode.children[0].text
            lvVerifDirType = curNode.children[1]
            if (not 'kAssertPropertyStatement' in lvVerifDirType.tag):
                continue

            if not lvLabel:
                continue

            if not lvLabel.startswith("a_"):
                message = self.formatViolationMessage(
                    description=f"Assert label '{lvLabel}' must start with 'a_' prefix.",
                    code_snippet=curNode.text,
                    fix_suggestion="Rename label to 'a_<name>' (e.g., 'a_req_ack').",
                )
                self.linter.logViolation(self.ruleID, message, "WARNING")
        
    def _getAssertPropertyName(self, assert_node):
        """Extracts the assert property name from an assert property statement."""
        # Look for SymbolIdentifier nodes that represent the assert property name
        for identifier in assert_node.iter_find_all({"tag": "SymbolIdentifier"}):
            # The first SymbolIdentifier in an assert property is usually the name
            return identifier.text
        return "Unknown"
