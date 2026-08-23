# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class UnusedProperty(AsFigoLintRule):
    """
    **PROP_UNUSED_PROPERTY** — Property declared but never referenced by any assertion, assumption, or cover.

    **Rationale**: A property that is declared but never bound to an
    ``assert property``, ``assume property``, or ``cover property`` statement
    contributes no verification value. It is either dead code from a refactor or
    an incomplete implementation where the binding was forgotten.

    **Violation**::

        property p_req_gnt;
            @(posedge clk) req |-> ##1 gnt;
        endproperty
        // No assert/assume/cover referencing p_req_gnt

    **Correct usage**::

        property p_req_gnt;
            @(posedge clk) req |-> ##1 gnt;
        endproperty
        assert property (p_req_gnt);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PROP_UNUSED_PROPERTY"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        # Collect declared property names → {name: declaration_node}
        lvDeclaredProps = {}
        for propNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            for child in getattr(propNode, "children", []):
                if getattr(child, "tag", None) == "SymbolIdentifier":
                    lvDeclaredProps[child.text] = propNode
                    break

        if not lvDeclaredProps:
            return

        # Collect all SymbolIdentifiers referenced inside assertion/assume/cover items
        lvReferencedNames = set()
        for assertNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            for leaf in assertNode.iter_find_all({"tag": "SymbolIdentifier"}):
                lvReferencedNames.add(leaf.text)
        for coverNode in data.tree.iter_find_all({"tag": "kCoverPropertyStatement"}):
            for leaf in coverNode.iter_find_all({"tag": "SymbolIdentifier"}):
                lvReferencedNames.add(leaf.text)
        for assumeNode in data.tree.iter_find_all({"tag": "kAssumePropertyStatement"}):
            for leaf in assumeNode.iter_find_all({"tag": "SymbolIdentifier"}):
                lvReferencedNames.add(leaf.text)

        for lvPropName, lvPropNode in lvDeclaredProps.items():
            if lvPropName not in lvReferencedNames:
                message = self.formatViolationMessage(
                    description=f"Property '{lvPropName}' is declared but never referenced in any 'assert property', 'assume property', or 'cover property' statement.",
                    code_snippet=lvPropNode.text,
                    fix_suggestion="Add a corresponding assertion or remove the unused property declaration.",
                )
                self.linter.logViolation(self.ruleID, message)
