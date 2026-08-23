# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class ThroughoutRhsBool(AsFigoLintRule):
    """
    **STYLE_THROUGHOUT_RHS_BOOL** — RHS of ``throughout`` is a plain boolean expression, not a sequence.

    **Rationale**: The ``throughout`` operator has the form
    ``boolean_expr throughout sequence_expr``. The right-hand side must be a
    meaningful multi-cycle sequence expression containing cycle delays (``##``)
    or repetition operators. Using a plain boolean signal as the RHS produces
    a degenerate single-cycle check, which is rarely the intent and makes the
    purpose of ``throughout`` misleading.

    **Violation**::

        p_valid_throughout: property (@(posedge clk)
            valid throughout ack);

    **Correct usage**::

        p_valid_throughout: property (@(posedge clk)
            valid throughout (req ##[1:5] ack));

    **Severity**: ERROR
    """

    # CST node tags that indicate a proper multi-cycle sequence in the RHS
    _SEQUENCE_TAGS = frozenset({
        "kSequenceDelayRepetition",
        "kSequenceDelayRange",
        "kConsecutiveRepetition",
        "kSequenceRepetitionExpression",
        "kCycleDelayRange",
    })

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "STYLE_THROUGHOUT_RHS_BOOL"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for propNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            for binExprNode in propNode.iter_find_all({"tag": "kBinaryExpression"}):
                lvChildren = getattr(binExprNode, "children", [])
                if len(lvChildren) < 3:
                    continue

                lvOperatorText = getattr(lvChildren[1], "text", "").strip()
                if lvOperatorText != "throughout":
                    continue

                # RHS is children[2]
                lvRhsNode = lvChildren[2]

                # Check for any sequence-indicator node in the RHS
                lvHasSeqNode = any(
                    len(list(lvRhsNode.iter_find_all({"tag": tag}))) > 0
                    for tag in self._SEQUENCE_TAGS
                )

                if not lvHasSeqNode:
                    message = self.formatViolationMessage(
                        description="RHS of 'throughout' is a plain boolean expression, not a multi-cycle sequence — the 'throughout' check degenerates to a single cycle.",
                        code_snippet=propNode.text,
                        fix_suggestion="Replace the boolean RHS with a proper sequence expression, e.g., '(req ##[1:5] ack)'.",
                    )
                    self.linter.logViolation(self.ruleID, message)
                    break  # One violation per property
