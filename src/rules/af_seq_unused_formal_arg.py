# ----------------------------------------------------
#
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
#
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class SeqUnusedFormalArg(AsFigoLintRule):
    """
    **SEQ_UNUSED_FORMAL_ARG** — Sequence has a formal argument that is never used in its body.

    **Rationale**: Unused formal arguments in a sequence definition indicate dead
    parameters. Callers must still pass values for them, creating misleading
    signatures and dead code. Remove unused arguments to keep interfaces clean
    and intent clear.

    **Violation**::

        sequence s_req(logic clk, logic unused);
            @(posedge clk) ##1 $rose(req);
        endsequence: s_req

    **Correct usage**::

        sequence s_req(logic clk);
            @(posedge clk) ##1 $rose(req);
        endsequence: s_req

    **Severity**: WARNING
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "SEQ_UNUSED_FORMAL_ARG"

    def apply(
        self,
        filePath: str,
        data: AsFigoLintRule.VeribleSyntax.SyntaxData
    ):
        for seqNode in data.tree.iter_find_all(
            {"tag": "kSequenceDeclaration"}
        ):

            sequence_name = None
            formal_args = []

            # Get sequence name
            for node in seqNode.children:
                if node.tag == "SymbolIdentifier":
                    sequence_name = node.text
                    break

            # Find formal argument list
            for node in seqNode.iter_find_all(
                {"tag": "SymbolIdentifier"}
            ):
                if node.text != sequence_name:
                    formal_args.append(node.text)

            # Remove duplicate identifiers
            formal_args = list(dict.fromkeys(formal_args))

            if not formal_args:
                continue

            # Find sequence body
            body_nodes = seqNode.iter_find_all(
                {"tag": "kSequenceDeclarationFinalExpr"}
            )

            body_text = ""

            for bodyNode in body_nodes:
                body_text += bodyNode.text

            unused_args = []

            for arg in formal_args:
                if arg not in body_text:
                    unused_args.append(arg)

            if unused_args:
                message = self.formatViolationMessage(
                    description=f"Sequence '{sequence_name}' has unused formal argument(s): {', '.join(unused_args)}.",
                    code_snippet=seqNode.text,
                    fix_suggestion="Remove unused argument(s) from the sequence signature.",
                )
                self.linter.logViolation(self.ruleID, message, "WARNING")
