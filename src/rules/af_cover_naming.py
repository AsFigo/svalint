# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# Author: Himank Gangwal, Sep 02, 2025
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

class CoverNaming(AsFigoLintRule):
    """
    **COVER_NAMING** — Cover label must start with ``c_``.

    **Rationale**: A consistent ``c_`` prefix on cover directives distinguishes
    coverage intent from assertions (``a_``) and assumptions (``m_``) when
    reviewing formal reachability reports and simulation coverage logs.

    **Violation**::

        req_seen: cover property (@(posedge clk) req);

    **Correct usage**::

        c_req_seen: cover property (@(posedge clk) req);

    **Severity**: WARNING
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "COVER_NAMING"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvLabel = curNode.children[0].text
            lvVerifDirType = curNode.children[1]

            if (not 'kCoverPropertyStatement' in lvVerifDirType.tag):
                continue

            if not lvLabel:
                continue

            if not lvLabel.startswith("c_"):
                message = self.formatViolationMessage(
                    description=f"Cover label '{lvLabel}' must start with 'c_' prefix.",
                    code_snippet=curNode.text,
                    fix_suggestion="Rename label to 'c_<name>' (e.g., 'c_req_seen').",
                )
                self.linter.logViolation(self.ruleID, message, "WARNING")
        
