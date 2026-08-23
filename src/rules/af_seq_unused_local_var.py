# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class SeqUnusedLocalVar(AsFigoLintRule):
    """
    **SEQ_UNUSED_LOCAL_VAR** — Local variable declared inside a sequence is never used.

    **Rationale**: An unused local variable in a sequence body is dead code — it
    consumes simulator resources on every evaluation thread without contributing
    to the check. It typically indicates an incomplete implementation or a
    leftover from a refactor.

    **Violation**::

        sequence seq_check;
            int unused_cnt;
            valid ##1 (data > 0);
        endsequence

    **Correct usage**::

        sequence seq_check;
            valid ##1 (data > 0);
        endsequence

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "SEQ_UNUSED_LOCAL_VAR"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for seqNode in data.tree.iter_find_all(
            {"tag": "kSequenceDeclaration"}
        ):
            for declNode in seqNode.iter_find_all(
                {"tag": "kAssertionVariableDeclaration"}
            ):
                varName = None
                for idNode in declNode.iter_find_all({"tag": "SymbolIdentifier"}):
                    varName = idNode.text
                    break

                if varName is None:
                    continue

                # Count all SymbolIdentifier leaves with this name in the sequence
                lvCount = sum(
                    1 for leaf in seqNode.iter_find_all({"tag": "SymbolIdentifier"})
                    if leaf.text == varName
                )

                # Exactly 1 occurrence means only the declaration — never used
                if lvCount == 1:
                    message = self.formatViolationMessage(
                        description=f"Local variable '{varName}' declared inside sequence is never used.",
                        code_snippet=seqNode.text,
                        fix_suggestion="Remove the unused local variable declaration.",
                    )
                    self.linter.logViolation(self.ruleID, message)
