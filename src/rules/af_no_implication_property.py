# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoImplicationProperty(AsFigoLintRule):
    """
    **NO_IMPLICATION_PROPERTY** — Avoid logical implication ``->`` in property; use ``|->`` or ``|=>``.

    **Rationale**: The ``->`` operator is a combinational logical implication, not
    a temporal one. Inside a property it evaluates statically in a single clock
    step and does not express sequential behavior. SVA temporal implication
    operators ``|->`` (overlapping) and ``|=>`` (non-overlapping) should be used
    to express sequential intent correctly.

    **Violation**::

        p_bad: property (@(posedge clk) (req -> ack));

    **Correct usage**::

        p_ok: property (@(posedge clk) req |-> ack);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "NO_IMPLICATION_PROPERTY"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        # Find all property declarations
        for prop in data.tree.iter_find_all(
            {"tag": "kPropertyDeclaration"}
        ):

            # Find binary expression nodes inside the property
            for binary in prop.iter_find_all(
                {"tag": "kBinaryExpression"}
            ):

                expression = binary.text.strip()

                # Detect only non-overlapped implication "->".
                # Do not flag "|->" or "|=>".
                if (
                    "->" in expression
                    and "|->" not in expression
                    and "|=>" not in expression
                ):
                    message = self.formatViolationMessage(
                        description="Logical implication '->' found inside property — this is combinational, not temporal.",
                        code_snippet=expression,
                        fix_suggestion="Replace '->' with temporal '|->' (overlapping) or '|=>' (non-overlapping).",
                    )
                    self.linter.logViolation(self.ruleID, message)
