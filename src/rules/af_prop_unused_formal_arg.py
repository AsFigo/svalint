# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

from af_lint_rule import AsFigoLintRule
import re


class PropUnusedFormalArg(AsFigoLintRule):
    """
    **PROP_UNUSED_FORMAL_ARG** — Property has a formal argument that is never used in its body.

    **Rationale**: Unused formal arguments indicate dead parameters — either a
    check was planned but never implemented, or a refactor left the signature
    inconsistent with the body. Callers must still pass values for them, creating
    misleading interfaces and dead code.

    **Violation**::

        property p_req_ack(input logic clk, input logic unused_sig);
            @(posedge clk) req |-> ack;
        endproperty: p_req_ack

    **Correct usage**::

        property p_req_ack(input logic clk);
            @(posedge clk) req |-> ack;
        endproperty: p_req_ack

    **Severity**: ERROR
    """

    def __init__(self, linter):
        self.linter = linter
        self.ruleID = "PROP_UNUSED_FORMAL_ARG"

    def apply(self, filePath, data):

        with open(filePath, "r") as f:
            text = f.read()

        # Remove comments
        text = re.sub(r'//.*', '', text)

        properties = re.finditer(
            r'property\s+(\w+)\s*\((.*?)\)\s*;(.*?)endproperty',
            text,
            re.DOTALL
        )

        for prop in properties:

            prop_name = prop.group(1)
            formal_args = prop.group(2)
            body = prop.group(3)

            # Extract only argument names
            args = []

            for arg in formal_args.split(","):

                arg = arg.strip()

                m = re.search(
                    r'(?:input|output|inout)\s+'
                    r'(?:logic|bit|reg|wire|int)?\s*'
                    r'([A-Za-z_][A-Za-z0-9_]*)$',
                    arg
                )

                if m:
                    args.append(m.group(1))

            unused = []

            for arg in args:

                if not re.search(r'\b' + re.escape(arg) + r'\b', body):
                    unused.append(arg)

            if unused:
                message = self.formatViolationMessage(
                    description=f"Property '{prop_name}' has unused formal argument(s): {', '.join(unused)}.",
                    fix_suggestion="Remove unused argument(s) from the property signature.",
                )
                self.linter.logViolation(self.ruleID, message)
