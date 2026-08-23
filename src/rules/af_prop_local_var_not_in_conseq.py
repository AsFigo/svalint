# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class PropLocalVarNotInConseq(AsFigoLintRule):
    """
    **PROP_LOCAL_VAR_NOT_USED_IN_CONSEQ** — Local variable captured in antecedent but never referenced in consequent.

    **Rationale**: A local variable assigned in the antecedent (e.g.,
    ``(valid, captured = data)``) is typically intended to be compared in the
    consequent (e.g., ``captured > 0``). If the consequent never references the
    variable the capture is pointless and the check is likely incomplete.

    **Violation**::

        property p_data_check;
            int captured;
            @(posedge clk)
                (valid, captured = data) |-> (data > 0);
        endproperty

    **Correct usage**::

        property p_data_check;
            int captured;
            @(posedge clk)
                (valid, captured = data) |-> (captured > 0);
        endproperty

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PROP_LOCAL_VAR_NOT_USED_IN_CONSEQ"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        for propNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            for declNode in propNode.iter_find_all(
                {"tag": "kAssertionVariableDeclaration"}
            ):
                varName = None
                for idNode in declNode.iter_find_all({"tag": "SymbolIdentifier"}):
                    varName = idNode.text
                    break

                if varName is None:
                    continue

                # For each implication operator, get the consequent and check for varName
                for implLeaf in (
                    list(propNode.iter_find_all({"tag": "|->"}))
                    + list(propNode.iter_find_all({"tag": "|=>"}))
                ):
                    lvSiblings = getattr(implLeaf, "siblings", [])
                    if len(lvSiblings) < 2:
                        continue

                    # siblings[1] is the consequent (siblings excludes self)
                    lvConseqNode = lvSiblings[1]

                    # CST-based check: search for SymbolIdentifier leaves in consequent
                    lvConseqSymbols = {
                        leaf.text
                        for leaf in lvConseqNode.iter_find_all(
                            {"tag": "SymbolIdentifier"}
                        )
                    }

                    if varName not in lvConseqSymbols:
                        message = self.formatViolationMessage(
                            description=f"Local variable '{varName}' is captured in the antecedent but never referenced in the consequent — the captured value is not verified.",
                            code_snippet=propNode.text,
                            fix_suggestion=f"Reference '{varName}' in the consequent expression, or remove the capture if it is not needed.",
                        )
                        self.linter.logViolation(self.ruleID, message)
                        break  # One violation per property per variable
