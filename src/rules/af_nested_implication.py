# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NestedImplication(AsFigoLintRule):
    """
    **STYLE_NO_NESTED_IMPL** — Avoid nested implication operators inside a property consequent.

    **Rationale**: Nesting an implication (``|->`` or ``|=>``) inside the
    consequent of another implication creates compound semantics that are hard
    to reason about. When such a property fails, it is unclear which implication
    violated the intent. Split into multiple simple properties instead.

    **Violation**::

        p_nested: property (@(posedge clk) a |-> (b |-> c));

    **Correct usage**::

        p_ab: property (@(posedge clk) a |-> b);
        p_bc: property (@(posedge clk) b |-> c);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "STYLE_NO_NESTED_IMPL"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for propNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            lvViolated = False

            for implLeaf in (
                list(propNode.iter_find_all({"tag": "|->"}))
                + list(propNode.iter_find_all({"tag": "|=>"}))
            ):
                lvSiblings = getattr(implLeaf, "siblings", [])
                if len(lvSiblings) < 2:
                    continue

                # siblings[1] is the consequent expression (siblings excludes self)
                lvConseqNode = lvSiblings[1]
                lvNestedOlap = list(lvConseqNode.iter_find_all({"tag": "|->"}))
                lvNestedNolap = list(lvConseqNode.iter_find_all({"tag": "|=>"}))

                if lvNestedOlap or lvNestedNolap:
                    lvViolated = True
                    break

            if lvViolated:
                message = self.formatViolationMessage(
                    description="Implication operator nested inside the consequent of another implication — creates ambiguous semantics and difficult-to-diagnose failures.",
                    code_snippet=propNode.text,
                    fix_suggestion="Split into multiple simple properties, one implication per property.",
                )
                self.linter.logViolation(self.ruleID, message)
