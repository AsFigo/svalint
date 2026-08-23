# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class UnusedSequence(AsFigoLintRule):
    """
    **SEQ_UNUSED_SEQUENCE** — Sequence declared but never referenced by any property or assertion.

    **Rationale**: A sequence that is declared but never used inside a property
    or assertion statement contributes no verification value. It is either dead
    code from a refactor or an incomplete implementation where the property
    binding was forgotten.

    **Violation**::

        sequence seq_req_gnt;
            req ##1 gnt;
        endsequence
        // No property or assertion referencing seq_req_gnt

    **Correct usage**::

        sequence seq_req_gnt;
            req ##1 gnt;
        endsequence
        property p_req_gnt;
            @(posedge clk) seq_req_gnt;
        endproperty

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "SEQ_UNUSED_SEQUENCE"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData,
    ):
        # Collect declared sequence names → {name: declaration_node}
        lvDeclaredSeqs = {}
        for seqNode in data.tree.iter_find_all({"tag": "kSequenceDeclaration"}):
            for child in getattr(seqNode, "children", []):
                if getattr(child, "tag", None) == "SymbolIdentifier":
                    lvDeclaredSeqs[child.text] = seqNode
                    break

        if not lvDeclaredSeqs:
            return

        # Collect all SymbolIdentifiers referenced in property declarations and assertion items
        lvReferencedNames = set()
        for propNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            for leaf in propNode.iter_find_all({"tag": "SymbolIdentifier"}):
                lvReferencedNames.add(leaf.text)
        for assertNode in data.tree.iter_find_all({"tag": "kAssertionItem"}):
            for leaf in assertNode.iter_find_all({"tag": "SymbolIdentifier"}):
                lvReferencedNames.add(leaf.text)
        for coverNode in data.tree.iter_find_all({"tag": "kCoverPropertyStatement"}):
            for leaf in coverNode.iter_find_all({"tag": "SymbolIdentifier"}):
                lvReferencedNames.add(leaf.text)

        for lvSeqName, lvSeqNode in lvDeclaredSeqs.items():
            if lvSeqName not in lvReferencedNames:
                message = self.formatViolationMessage(
                    description=f"Sequence '{lvSeqName}' is declared but never referenced in any property or assertion.",
                    code_snippet=lvSeqNode.text,
                    fix_suggestion="Reference the sequence in a property or assertion, or remove the unused sequence declaration.",
                )
                self.linter.logViolation(self.ruleID, message)
