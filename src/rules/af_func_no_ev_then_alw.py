# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule

# ==============================================================================
# MIXIN HELPER: Shared logic (NOT a lint rule, ignored by framework discovery)
# ==============================================================================
class _LivenessHelper:

    def checkPattern(self, data, eventuallyTokens, alwaysTokens):
        """
        Generic AST traversal logic to find nested prefix expressions matching
        specific 'eventually' -> 'always' sequences.
        """
        for prefixNode in data.tree.iter_find_all({"tag": "kPropertyPrefixExpression"}):
            outerLeaves = getattr(prefixNode, "leaves", [])
            if not outerLeaves:
                continue

            # Check if outer property matches our target 'eventually' tokens
            firstTok = outerLeaves[0].text.strip()
            if firstTok in eventuallyTokens:

                # Look for an inner prefix expression directly under this parent
                for innerPrefixNode in prefixNode.iter_find_all({"tag": "kPropertyPrefixExpression"}):
                    if innerPrefixNode == prefixNode:
                        continue

                    innerLeaves = getattr(innerPrefixNode, "leaves", [])
                    if innerLeaves:
                        innerTok = innerLeaves[0].text.strip()

                        # Check if inner property matches our target 'always' tokens
                        if innerTok in alwaysTokens:
                            lvSvaCode = prefixNode.text.strip()
                            message = self.formatViolationMessage(
                                description=self.lvDescription,
                                code_snippet=lvSvaCode,
                                fix_suggestion=self.lvFixSuggestion,
                            )
                            self.linter.logViolation(self.ruleID, message)
                            break


# ==============================================================================
# INDIVIDUAL RULES: Discovered and counted independently by the Linter
# ==============================================================================

class AvoidStrongEventuallyAlwaysRule(AsFigoLintRule, _LivenessHelper):
    """
    **FUNC_AVOID_S_EV_ALW** — Avoid ``s_eventually always`` (Unbounded Strong-Weak).

    **Rationale**: Asserting that a signal eventually becomes permanently true is
    fragile in dynamic simulation. Any subsequent reset, power-gating sequence,
    or testbench re-initialization will disturb the signal, producing persistent
    false assertion failures.

    **Violation**::

        a_stab: assert property (@(posedge clk) s_eventually always stable(data));

    **Correct usage**::

        a_stab: assert property (@(posedge clk) s_eventually [1:100] stable(data));

    **Severity**: ERROR
    """

    lvDescription = (
        "'s_eventually always' (unbounded strong-weak) detected — hardware states rarely hold forever; "
        "any reset or testbench re-initialization will cause persistent false assertion failures."
    )
    lvFixSuggestion = (
        "Use a bounded check (e.g., 's_eventually [1:N]') or add an explicit 'disable iff' condition."
    )

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_S_EV_ALW"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        self.checkPattern(data, ["s_eventually"], ["always"])


class AvoidStrongEventuallySAlwaysRule(AsFigoLintRule, _LivenessHelper):
    """
    **FUNC_AVOID_S_EV_S_ALW** — Avoid ``s_eventually s_always`` (Unbounded Strong-Strong).

    **Rationale**: Demanding that a signal stabilizes and holds permanently
    is unrealistic in simulation. Any subsequent reset or mode change will
    violate this expectation, causing persistent false failures.

    **Violation**::

        a_lock: assert property (@(posedge clk) s_eventually s_always locked);

    **Correct usage**::

        a_lock: assert property (@(posedge clk)
            s_eventually [1:50] s_always [0:10] locked);

    **Severity**: ERROR
    """

    lvDescription = (
        "'s_eventually s_always' (unbounded strong-strong) detected — demanding a signal holds permanently "
        "is unrealistic; any subsequent reset or mode change in the test will cause persistent failures."
    )
    lvFixSuggestion = (
        "Use a bounded check (e.g., 's_eventually [1:N] s_always [0:M]') or ensure this is strictly "
        "for a finite sequence."
    )

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_S_EV_S_ALW"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        self.checkPattern(data, ["s_eventually"], ["s_always"])


class AvoidEventuallyAlwaysRule(AsFigoLintRule, _LivenessHelper):
    """
    **FUNC_AVOID_EV_ALW** — Avoid ``eventually always`` (Bounded Weak-Weak).

    **Rationale**: Weak ``eventually`` allows the assertion to pass vacuously if
    the simulation ends before stabilization is observed. Additionally, expecting
    permanent stability in dynamic simulation leads to false failures when system
    state is later disturbed by resets or power sequences.

    **Violation**::

        a_stab: assert property (@(posedge clk) eventually always stable(data));

    **Correct usage**::

        a_stab: assert property (@(posedge clk) s_eventually [1:100] stable(data));

    **Severity**: ERROR
    """

    lvDescription = (
        "'eventually always' (weak-weak) detected — weak 'eventually' passes vacuously if simulation ends "
        "before stabilization is observed; permanent stability is also unrealistic in dynamic simulation."
    )
    lvFixSuggestion = (
        "Use 's_eventually [1:N]' (strong, bounded) or verify that permanent stability is truly intended "
        "and add 'disable iff' for reset/power-gating events."
    )

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_EV_ALW"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        self.checkPattern(data, ["eventually"], ["always"])


class AvoidEventuallySAlwaysRule(AsFigoLintRule, _LivenessHelper):
    """
    **FUNC_AVOID_EV_S_ALW** — Avoid ``eventually s_always`` (Bounded Weak-Strong).

    **Rationale**: This pattern asserts that a condition will eventually lock into
    a permanent strong state. In directed or constrained-random testbenches, this
    is highly susceptible to failures when test phases shift (e.g., low-power
    entry/exit). Add explicit disable conditions or bound the stability window.

    **Violation**::

        a_lock: assert property (@(posedge clk) eventually s_always locked);

    **Correct usage**::

        a_lock: assert property (@(posedge clk)
            s_eventually [1:50] locked disable iff (reset));

    **Severity**: ERROR
    """

    lvDescription = (
        "'eventually s_always' (weak-strong) detected — expecting a signal to lock into a permanent strong "
        "state is highly susceptible to failures when test phases shift (e.g., low-power entry/exit)."
    )
    lvFixSuggestion = (
        "Add explicit 'disable iff' conditions or bound the stability window "
        "(e.g., 's_eventually [1:N] locked disable iff (reset)')."
    )

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "FUNC_AVOID_EV_S_ALW"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        self.checkPattern(data, ["eventually"], ["s_always"])
