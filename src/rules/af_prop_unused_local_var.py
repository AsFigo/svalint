# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class PropUnusedLocalVar(AsFigoLintRule):
    """
    **PROP_UNUSED_LOCAL_VAR** — Local variable declared inside a property is never used.

    **Rationale**: An unused local variable in a property body is dead code — it
    consumes simulator resources on every evaluation thread without contributing
    to the check. It typically indicates an incomplete implementation or leftover
    from a refactor.

    **Violation**::

        property p_data_check;
            int unused_cnt;
            @(posedge clk) valid |-> data != 0;
        endproperty: p_data_check

    **Correct usage**::

        property p_data_check;
            @(posedge clk) valid |-> data != 0;
        endproperty: p_data_check

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PROP_UNUSED_LOCAL_VAR"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData
    ):
        # Find all property declarations
        for prop in data.tree.iter_find_all(
            {"tag": "kPropertyDeclaration"}
        ):

            # Find local/assertion variable declarations
            for decl in prop.iter_find_all(
                {"tag": "kAssertionVariableDeclaration"}
            ):

                varName = None

                # Get the declared variable name
                for idNode in decl.iter_find_all(
                    {"tag": "SymbolIdentifier"}
                ):
                    varName = idNode.text
                    break

                if varName is None:
                    continue

                # Count occurrences of the variable in the property.
                # One occurrence is the declaration itself.
                if prop.text.count(varName) == 1:

                    message = self.formatViolationMessage(
                        description=f"Local variable '{varName}' declared inside property is never used.",
                        code_snippet=prop.text,
                        fix_suggestion="Remove the unused local variable declaration.",
                    )
                    self.linter.logViolation(self.ruleID, message)
