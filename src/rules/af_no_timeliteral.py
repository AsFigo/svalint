# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoExplTimeLiterals(AsFigoLintRule):
    """
    **REUSE_NO_TIMELITERAL** — Avoid explicit time literals in SVA property declarations.

    **Rationale**: Hard-coded time values (e.g., ``10ns``, ``100ps``) in SVA make
    properties non-reusable across designs with different clock frequencies or
    timing budgets. Use parameters or `` `define`` macros so timing can be
    adjusted without modifying the assertion source.

    **Violation**::

        p_timeout: property (@(posedge clk)
            start |-> done within 100ns);

    **Correct usage**::

        parameter TIMEOUT_CYCLES = 20;
        p_timeout: property (@(posedge clk)
            start |-> ##[1:TIMEOUT_CYCLES] done);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        # Store the linter instance
        self.ruleID = "REUSE_NO_TIMELITERAL"

    def apply(
        self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData
    ):
        for curNode in data.tree.iter_find_all(
            {"tag": "kPropertyDeclaration"}
        ):
            lvSvaCode = curNode.text
            lvTimeLiteralG = curNode.iter_find_all({"tag": "TK_TimeLiteral"})
            lvTimeLiteralList = list(lvTimeLiteralG)
            if len(lvTimeLiteralList) > 0:
                message = self.formatViolationMessage(
                    description="Explicit time literal (e.g., '100ns') found in property — prevents reuse across designs with different timing budgets.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Replace the literal with a parameter or '`define' macro.",
                )
                self.linter.logViolation(self.ruleID, message)
