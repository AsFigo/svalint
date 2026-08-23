# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class NoUbRepeatInAnt(AsFigoLintRule):
    """
    **PERF_NO_UB_REPEAT_IN_ANT** — Avoid unbounded consecutive repetition ``[*]`` or ``[+]`` in assertion antecedent.

    **Rationale**: ``sig[*]`` (zero or more) and ``sig[+]`` (one or more) are
    unbounded consecutive repetitions. When placed in an antecedent they force
    the tool to maintain an unlimited number of concurrent match threads — one
    per possible cycle count — causing state-space explosion in formal tools
    and significant simulation slowdown.

    **Violation**::

        a_req_gnt: assert property (@(posedge clk) req[*] |-> gnt);

    **Correct usage**::

        a_req_gnt: assert property (@(posedge clk) req[*1:5] |-> gnt);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PERF_NO_UB_REPEAT_IN_ANT"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for assertNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            lvSvaCode = assertNode.text

            for implListNode in assertNode.iter_find_all(
                {"tag": "kPropertyImplicationList"}
            ):
                # Antecedent is children[0] of kPropertyImplicationList
                lvChildren = getattr(implListNode, "children", [])
                if not lvChildren:
                    continue
                lvAntNode = lvChildren[0]

                for repNode in lvAntNode.iter_find_all(
                    {"tag": "kConsecutiveRepetition"}
                ):
                    lvRepChildren = getattr(repNode, "children", [])
                    if not lvRepChildren:
                        continue
                    lvRepText = getattr(lvRepChildren[0], "text", "").strip()

                    # [*] = zero-or-more, [+] = one-or-more — both unbounded
                    if lvRepText in ("[*]", "[+]"):
                        message = self.formatViolationMessage(
                            description=f"Unbounded consecutive repetition '{lvRepText}' in assertion antecedent — spawns unlimited match threads causing performance issues.",
                            code_snippet=lvSvaCode,
                            fix_suggestion="Replace unbounded repetition with a finite bound, e.g., '[*1:N]'.",
                        )
                        self.linter.logViolation(self.ruleID, message)
                        break
