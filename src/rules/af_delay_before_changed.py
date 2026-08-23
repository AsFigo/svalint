# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class DelayBeforeChanged(AsFigoLintRule):
    """
    **DELAY_BEFORE_CHANGED** — A ``##1`` delay is required immediately before ``$changed``.

    **Rationale**: ``$changed(sig)`` samples the signal on two consecutive clocks.
    Without a preceding ``##1``, the assertion may fire on the very first active
    clock before ``sig`` has a defined previous value, causing spurious failures
    at time zero or after resets when signal history is undefined.

    **Violation**::

        p_changed_bad: property (@(posedge clk) req |-> $changed(gnt));

    **Correct usage**::

        p_changed_ok: property (@(posedge clk) req |-> ##1 $changed(gnt));

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "DELAY_BEFORE_CHANGED"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for prop in data.tree.iter_find_all(
            {"tag": "kPropertyDeclaration"}
        ):
            # Collect all $changed calls in this property
            lvAllChanged = [
                node for node in prop.iter_find_all({"tag": "kSystemTFCall"})
                if getattr(node.children[0], "text", "") == "$changed"
            ]
            if not lvAllChanged:
                continue

            # Collect $changed calls that are properly inside a kSequenceDelayRange
            lvChangedWithDelayIds = set()
            for delayNode in prop.iter_find_all({"tag": "kSequenceDelayRange"}):
                for tfNode in delayNode.iter_find_all({"tag": "kSystemTFCall"}):
                    if getattr(tfNode.children[0], "text", "") == "$changed":
                        lvChangedWithDelayIds.add(id(tfNode))

            # Flag any $changed not inside a kSequenceDelayRange
            for tfNode in lvAllChanged:
                if id(tfNode) not in lvChangedWithDelayIds:
                    message = self.formatViolationMessage(
                        description="'$changed' used without a preceding '##1' delay — may fire spuriously at time zero or after reset.",
                        code_snippet=prop.text,
                        fix_suggestion="Add '##1' immediately before '$changed': '##1 $changed(sig)'.",
                    )
                    self.linter.logViolation(self.ruleID, message)
                    break
