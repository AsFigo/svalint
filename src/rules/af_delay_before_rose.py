# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class DelayBeforeRose(AsFigoLintRule):
    """
    **DELAY_BEFORE_ROSE** — A ``##1`` delay is required immediately before ``$rose``.

    **Rationale**: ``$rose(sig)`` samples the signal on two consecutive clocks.
    Without a preceding ``##1``, the assertion may fire on the very first active
    clock before ``sig`` has a defined previous value, causing spurious failures
    at time zero or after resets when signal history is undefined.

    **Violation**::

        p_rose_bad: property (@(posedge clk) $rose(req) |-> ack);

    **Correct usage**::

        p_rose_ok: property (@(posedge clk) ##1 $rose(req) |-> ack);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "DELAY_BEFORE_ROSE"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for prop in data.tree.iter_find_all(
            {"tag": "kPropertyDeclaration"}
        ):
            prop_text = prop.text

            if "$rose" not in prop_text:
                continue

            if "##1 $rose" in prop_text or "##1$rose" in prop_text:
                continue

            message = self.formatViolationMessage(
                description="'$rose' used without a preceding '##1' delay — may fire spuriously at time zero or after reset.",
                code_snippet=prop_text,
                fix_suggestion="Add '##1' immediately before '$rose': '##1 $rose(sig)'.",
            )
            self.linter.logViolation(self.ruleID, message)
