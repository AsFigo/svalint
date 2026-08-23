# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class DelayBeforeFell(AsFigoLintRule):
    """
    **DELAY_BEFORE_FELL** — A ``##1`` delay is required immediately before ``$fell``.

    **Rationale**: ``$fell(sig)`` samples the signal on two consecutive clocks.
    Without a preceding ``##1``, the assertion may fire on the very first active
    clock before ``sig`` has a defined previous value, causing spurious failures
    at time zero or after resets when signal history is undefined.

    **Violation**::

        p_fell_bad: property (@(posedge clk) req |-> $fell(gnt));

    **Correct usage**::

        p_fell_ok: property (@(posedge clk) req |-> ##1 $fell(gnt));

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "DELAY_BEFORE_FELL"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for prop in data.tree.iter_find_all(
            {"tag": "kPropertyDeclaration"}
        ):
            # Collect all $fell calls in this property
            lvAllFell = [
                node for node in prop.iter_find_all({"tag": "kSystemTFCall"})
                if getattr(node.children[0], "text", "") == "$fell"
            ]
            if not lvAllFell:
                continue

            # Collect $fell calls that are properly inside a kSequenceDelayRange
            lvFellWithDelayIds = set()
            for delayNode in prop.iter_find_all({"tag": "kSequenceDelayRange"}):
                for tfNode in delayNode.iter_find_all({"tag": "kSystemTFCall"}):
                    if getattr(tfNode.children[0], "text", "") == "$fell":
                        lvFellWithDelayIds.add(id(tfNode))

            # Flag any $fell not inside a kSequenceDelayRange
            for tfNode in lvAllFell:
                if id(tfNode) not in lvFellWithDelayIds:
                    message = self.formatViolationMessage(
                        description="'$fell' used without a preceding '##1' delay — may fire spuriously at time zero or after reset.",
                        code_snippet=prop.text,
                        fix_suggestion="Add '##1' immediately before '$fell': '##1 $fell(sig)'.",
                    )
                    self.linter.logViolation(self.ruleID, message)
                    break
