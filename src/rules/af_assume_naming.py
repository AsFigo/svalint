# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# Author: Himank Gangwal, Sep 02, 2025
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

class AssumeNaming(AsFigoLintRule):
    """
    **ASSUME_NAMING** — Assume label must start with ``m_``.

    **Rationale**: The ``m_`` prefix (model/assume) distinguishes constraint
    assumptions from assertions (``a_``) and coverage (``c_``) in formal tool
    reports and log files, making intent immediately clear during review.

    **Violation**::

        req_stable: assume property (@(posedge clk) $stable(req));

    **Correct usage**::

        m_req_stable: assume property (@(posedge clk) $stable(req));

    **Severity**: WARNING
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "ASSUME_NAMING"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvLabel = curNode.children[0].text
            lvVerifDirType = curNode.children[1]

            if (not 'kAssumePropertyStatement' in lvVerifDirType.tag):
                continue

            if not lvLabel:
                continue

            if not lvLabel.startswith("m_"):
                message = self.formatViolationMessage(
                    description=f"Assume label '{lvLabel}' must start with 'm_' prefix.",
                    code_snippet=curNode.text,
                    fix_suggestion="Rename label to 'm_<name>' (e.g., 'm_req_stable').",
                )
                self.linter.logViolation(self.ruleID, message, "WARNING")
        
