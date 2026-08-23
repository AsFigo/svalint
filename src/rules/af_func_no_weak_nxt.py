# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

# ==============================================================================
# MIXIN HELPER: Shared logic (NOT a lint rule, ignored by framework discovery)
# ==============================================================================
class _NexttimeHelper:

    def checkNexttimePattern(self, data, expectBounded: bool):
        """
        Traverses the AST to find weak 'nexttime' property expressions.
        expectBounded = False -> detects unbounded nexttime (e.g., nexttime a)
        expectBounded = True  -> detects bounded nexttime   (e.g., nexttime [2] a)
        """
        for prefixNode in data.tree.iter_find_all({"tag": "kPropertyPrefixExpression"}):
            leaves = getattr(prefixNode, "leaves", [])
            if not leaves:
                continue

            # Match the weak 'nexttime' keyword (explicitly avoiding 's_nexttime')
            firstTok = leaves[0].text.strip()
            if firstTok == "nexttime":
                # Check whether a kPropertyExpressionIndex node exists for bounded ranges
                hasIndex = len(list(prefixNode.iter_find_all({"tag": "kPropertyExpressionIndex"}))) > 0

                if expectBounded and hasIndex:
                    svaCode = prefixNode.text.strip()
                    message = self.formatViolationMessage(
                        description=self.lvDescription,
                        code_snippet=svaCode,
                        fix_suggestion=self.lvFixSuggestion,
                    )
                    self.linter.logViolation(self.ruleID, message)
                elif not expectBounded and not hasIndex:
                    svaCode = prefixNode.text.strip()
                    message = self.formatViolationMessage(
                        description=self.lvDescription,
                        code_snippet=svaCode,
                        fix_suggestion=self.lvFixSuggestion,
                    )
                    self.linter.logViolation(self.ruleID, message)


# ==============================================================================
# INDIVIDUAL RULES: Discovered and counted independently by the Linter
# ==============================================================================

class AvoidUnboundedNexttimeRule(AsFigoLintRule, _NexttimeHelper):
    """
    **FUNC_AVOID_NEXTTIME** — Avoid unbounded weak ``nexttime``; use ``s_nexttime``.

    **Rationale**: Weak ``nexttime`` evaluates to true vacuously if the simulation
    ends or clock ticks terminate before the next cycle is observed, making the
    assertion ineffective. Use ``s_nexttime`` (strong nexttime) to enforce that
    the next-cycle condition is strictly observed.

    **Violation**::

        a_nxt: assert property (@(posedge clk) req |-> nexttime ack);

    **Correct usage**::

        a_nxt: assert property (@(posedge clk) req |-> s_nexttime ack);

    **Severity**: ERROR
    """

    lvDescription = (
        "Unbounded weak 'nexttime' detected — evaluates vacuously true if the simulation ends before "
        "the next cycle is observed, making the assertion ineffective."
    )
    lvFixSuggestion = "Replace 'nexttime' with the strong variant 's_nexttime'."

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_NEXTTIME"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        self.checkNexttimePattern(data, expectBounded=False)


class AvoidBoundedNexttimeRule(AsFigoLintRule, _NexttimeHelper):
    """
    **FUNC_AVOID_BOUNDED_NEXTTIME** — Avoid bounded weak ``nexttime [k]``; use ``s_nexttime [k]``.

    **Rationale**: Bounded weak ``nexttime [k]`` allows vacuously true passes at
    simulation limits when insufficient clock cycles remain, potentially masking
    functional verification blind spots. Use ``s_nexttime [k]`` to prevent such
    vacuous passes.

    **Violation**::

        a_nxt: assert property (@(posedge clk) req |-> nexttime [2] ack);

    **Correct usage**::

        a_nxt: assert property (@(posedge clk) req |-> s_nexttime [2] ack);

    **Severity**: ERROR
    """

    lvDescription = (
        "Bounded weak 'nexttime [k]' detected — allows vacuously true passes at simulation limits "
        "when insufficient clock cycles remain, potentially masking verification blind spots."
    )
    lvFixSuggestion = "Replace bounded weak 'nexttime [k]' with the strong variant 's_nexttime [k]'."

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_BOUNDED_NEXTTIME"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        self.checkNexttimePattern(data, expectBounded=True)
