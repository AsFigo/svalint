# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule


class UseSimpleExprConseq(AsFigoLintRule):
    """
    **DBG_USE_SIMPLE_EXPR_IN_CONSEQ** — Avoid complex consequent expressions; prefer multiple simple properties.

    **Rationale**: A property with multiple implication operators or a consequent
    containing more than two ``&&`` expressions is difficult to debug when it
    fails — the failing sub-expression is not immediately obvious from the error
    report. Splitting into smaller properties lets the tool pinpoint exactly which
    condition failed.

    **Violation**::

        p_complex: property (@(posedge clk)
            req |-> ack && data_valid && !err && count > 0);

    **Correct usage**::

        p_ack:   assert property (@(posedge clk) req |-> ack);
        p_valid: assert property (@(posedge clk) req |-> data_valid);
        p_noerr: assert property (@(posedge clk) req |-> !err);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "DBG_USE_SIMPLE_EXPR_IN_CONSEQ"

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):

        for curNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            lvSvaCode = curNode.text
            lvNumOlapOper = len(list(curNode.iter_find_all({"tag": "|->"})))
            lvNumNonOlapOper = len(list(curNode.iter_find_all({"tag": "|=>"})))

            if (lvNumOlapOper + lvNumNonOlapOper > 1):
                message = self.formatViolationMessage(
                    description="Property has multiple implication operators — complex consequent makes failure diagnosis difficult.",
                    code_snippet=lvSvaCode,
                    fix_suggestion="Split into multiple simple properties, one condition per property.",
                )
                self.linter.logViolation(self.ruleID, message)
                continue

            for lvOlapImplNode in curNode.iter_find_all({"tag": "|->"}):
                lvConseqNode = lvOlapImplNode.siblings[1]
                lvNumANDinConseq = len(list(lvConseqNode.iter_find_all({"tag": "&&"})))
                if (lvNumANDinConseq > 2):
                    message = self.formatViolationMessage(
                        description=f"Consequent has {lvNumANDinConseq} '&&' conditions — too complex to pinpoint the failing sub-expression.",
                        code_snippet=lvSvaCode,
                        fix_suggestion="Split into multiple simple properties, one condition per property.",
                    )
                    self.linter.logViolation(self.ruleID, message)
