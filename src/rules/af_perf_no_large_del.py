# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------
from af_lint_rule import AsFigoLintRule


class NoLargeDelayProp(AsFigoLintRule):
    """
    **PERF_NO_LARGE_DELAY** — Avoid large cycle delays (> 100 by default) in SVA properties.

    **Rationale**: Large delay values (e.g., ``##500``) force the simulator to
    maintain evaluation threads for hundreds of cycles, significantly increasing
    memory and runtime overhead. If a large delay is genuinely required, use a
    parameterized constant and document the justification. The threshold is
    configurable via ``cfgMaxDelay`` (default: 100).

    **Violation**::

        p_resp: property (@(posedge clk) req |-> ##500 ack);

    **Correct usage**::

        parameter MAX_RESP = 20;
        p_resp: property (@(posedge clk) req |-> ##[1:MAX_RESP] ack);

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PERF_NO_LARGE_DELAY"
        self.cfgMaxDelay = 100

    def apply(self, filePath: str, data: AsFigoLintRule.VeribleSyntax.SyntaxData):
        for curNode in data.tree.iter_find_all({"tag": "kPropertyDeclaration"}):
            lvSvaCode = curNode.text
            lvDelayG = curNode.iter_find_all({"tag": "kCycleDelayRange"})
            for curDelNode in lvDelayG:
                lvDelValG = curDelNode.iter_find_all({"tag": "TK_DecNumber"})
                for curDelValNode in lvDelValG:
                    if int(curDelValNode.text) > self.cfgMaxDelay:
                        message = self.formatViolationMessage(
                            description=f"Cycle delay '{curDelValNode.text}' exceeds the maximum allowed ({self.cfgMaxDelay}) — forces simulator to maintain threads for many cycles.",
                            code_snippet=lvSvaCode,
                            fix_suggestion=f"Use a bounded parameter (e.g., 'parameter MAX_RESP = {self.cfgMaxDelay}') and reference it in the delay.",
                        )
                        self.linter.logViolation(self.ruleID, message)
