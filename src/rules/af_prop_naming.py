# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# Author: Himank Gangwal, June 07, 2025
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

class PropNaming(AsFigoLintRule):
    """
    **PROP_NAMING** — Property declaration must start with ``p_``.

    **Rationale**: A consistent ``p_`` prefix on property names allows engineers
    to instantly identify and filter property declarations in log files, waveforms,
    and code search. It also visually separates properties from sequences
    (typically ``s_`` prefixed) and module-level signals.

    **Violation**::

        property req_ack;
            @(posedge clk) req |-> ##[1:3] ack;
        endproperty: req_ack

    **Correct usage**::

        property p_req_ack;
            @(posedge clk) req |-> ##[1:3] ack;
        endproperty: p_req_ack

    **Severity**: WARNING
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PROP_NAMING"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            lvSvaCode = self._getHeaderName(curNode)
            if (not lvSvaCode.startswith("p_")):
                message = self.formatViolationMessage(
                    description=f"Property '{lvSvaCode}' must start with 'p_' prefix.",
                    code_snippet=curNode.text,
                    fix_suggestion="Rename to 'p_<name>' (e.g., 'p_req_ack').",
                )
                self.linter.logViolation(self.ruleID, message, "WARNING")
                
    def _getHeaderName(self, header):
        """Extracts the property or sequence name from its declaration header."""
        for identifier in header.iter_find_all({"tag": "SymbolIdentifier"}):
            return identifier.text
        return "Unknown"
