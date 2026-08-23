# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class MixedImplOper(AsFigoLintRule):
    """
    **STYLE_NO_MIXED_IMPL_OPER** — Do not use ``|->`` and ``|=>`` in the same property.

    **Rationale**: Mixing overlapping (``|->``) and non-overlapping (``|=>``)
    implication operators in a single property creates ambiguous semantics and
    makes the intent harder to understand at a glance. Each property should use
    one consistent implication style.

    **Violation**::

        p_mixed: property (@(posedge clk) a |-> (b |=> c));

    **Correct usage**::

        p_olap:  property (@(posedge clk) a |-> ##1 b);
        p_nolap: property (@(posedge clk) a |=> ##1 b);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "STYLE_NO_MIXED_IMPL_OPER"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for propNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            lvNumOlap = len(list(propNode.iter_find_all({"tag": "|->"})))
            lvNumNolap = len(list(propNode.iter_find_all({"tag": "|=>"})))

            if lvNumOlap > 0 and lvNumNolap > 0:
                message = self.formatViolationMessage(
                    description=f"Property mixes '|->' ({lvNumOlap}) and '|=>' ({lvNumNolap}) operators — use one consistent implication style per property.",
                    code_snippet=propNode.text,
                    fix_suggestion="Split into separate properties, each using only '|->' or only '|=>'.",
                )
                self.linter.logViolation(self.ruleID, message)
