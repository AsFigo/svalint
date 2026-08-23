# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class ImmediateSvaAlwaysComb(AsFigoLintRule):
    """
    **STYLE_NO_IMM_SVA_IN_ALWAYS_COMB** — Avoid plain immediate assertions inside ``always_comb``; use ``assert final``.

    **Rationale**: An immediate assertion (``assert (expr)``) placed inside an
    ``always_comb`` block fires combinatorially on every delta cycle, not just
    at the end of the time step. This can trigger spurious failures during
    intermediate signal glitches. The deferred form ``assert final`` evaluates
    only after all combinatorial settling, giving the correct result.

    **Violation**::

        always_comb begin
            assert (a == b) else $error("fail");
        end

    **Correct usage**::

        always_comb begin
            assert final (a == b) else $error("fail");
        end

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "STYLE_NO_IMM_SVA_IN_ALWAYS_COMB"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for alwaysNode in data.tree.iter_find_all({"tag": "kAlwaysStatement"}):
            lvChildren = getattr(alwaysNode, "children", [])
            if not lvChildren:
                continue

            lvFirstText = getattr(lvChildren[0], "text", "").strip()
            if lvFirstText != "always_comb":
                continue

            for assertStmtNode in alwaysNode.iter_find_all(
                {"tag": "kAssertionStatement"}
            ):
                for assertHeaderNode in assertStmtNode.iter_find_all(
                    {"tag": "kAssertionHeader"}
                ):
                    lvHasFinal = any(
                        getattr(child, "text", "").strip() == "final"
                        for child in getattr(assertHeaderNode, "children", [])
                    )
                    if not lvHasFinal:
                        message = self.formatViolationMessage(
                            description="Plain immediate 'assert' inside 'always_comb' — fires on every delta cycle and may produce spurious failures during combinatorial glitches.",
                            code_snippet=assertHeaderNode.text,
                            fix_suggestion="Replace 'assert (expr)' with 'assert final (expr)' to evaluate only after combinatorial settling.",
                        )
                        self.linter.logViolation(self.ruleID, message)
