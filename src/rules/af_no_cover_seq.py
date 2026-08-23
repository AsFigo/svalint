# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoCoverSeq(AsFigoLintRule):
    """
    **NO_COVER_SEQ** — Avoid ``cover sequence``; use ``cover property`` instead.

    **Rationale**: ``cover sequence`` is deprecated in practice and has limited
    support across EDA tools. ``cover property`` is the standard, universally
    supported form for temporal coverage collection and should always be preferred.

    **Violation**::

        c_req: cover sequence (@(posedge clk) req ##1 ack);

    **Correct usage**::

        c_req: cover property (@(posedge clk) req ##1 ack);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "NO_COVER_SEQ"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for curNode in data.tree.iter_find_all(
            {"tag": "kCoverSequenceStatement"}
        ):
            lvSvaCode = curNode.text.strip()

            message = self.formatViolationMessage(
                description="'cover sequence' is deprecated and has limited EDA tool support.",
                code_snippet=lvSvaCode,
                fix_suggestion="Replace 'cover sequence' with 'cover property'.",
            )
            self.linter.logViolation(self.ruleID, message)
