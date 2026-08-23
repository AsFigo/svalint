# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

import sys
import os
# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import argparse
import logging
import verible_verilog_syntax
from af_lint_rule import AsFigoLintRule
from asfigo_linter import AsFigoLinter
from rules.af_asrt_no_label import MissingLabelChk
from rules.af_perf_no_pass_ablk import PerfNoPABlk
from rules.af_no_timeliteral import NoExplTimeLiterals
from rules.af_no_within_oper import NoWithinOperInAsrt
from rules.af_no_fmatch_oper import NoFirstMatchOperInAsrt
from rules.af_no_range_ant import NoRangeInAntAsrt
from rules.af_perf_no_ub_range_ant import NoUBRangeInAntAsrt
from rules.af_func_missing_fablk import FuncMissingFABLK
from rules.af_missing_elbl_prop import MissingEndLblProp
from rules.af_missing_elbl_seq import MissingEndLblSEQ
from rules.af_prop_naming import PropNaming
from rules.af_perf_missing_impl_oper import MissingImplicationOper
from rules.af_perf_no_large_del import NoLargeDelayProp
from rules.af_use_simple_cnseq import UseSimpleExprConseq
from rules.af_no_dollar_time import UseRealTimeVsTime
from rules.af_func_cov_nolap import FuncNOLAPInCoverProp
from rules.af_func_cov_olap import FuncOLAPInCoverProp
from rules.af_reuse_fa_one_liner import ReuseNoOneLinerFABLK
from rules.af_func_no_ub_in_cnseq import NoUBRangeInConseqAsrt
from rules.af_asrt_naming import AssertNaming
from rules.af_no_aa_exists_sva import AvoidAAExistsSVA
from rules.af_no_pop_back_sva import AvoidPopBkSVA
from rules.af_no_pop_front_sva import AvoidPopFrSVA
from rules.af_assume_naming import AssumeNaming
from rules.af_cover_naming import CoverNaming
from rules.af_func_no_weak_until import AvoidWeakUntilRule
from rules.af_func_no_weak_until_w import AvoidWeakUntilWithRule
from rules.af_func_no_weak_ev import AvoidWeakEventuallyRule
from rules.af_prop_unused_formal_arg import PropUnusedFormalArg
from rules.af_seq_unused_formal_arg import SeqUnusedFormalArg
from rules.af_prop_unused_local_var import PropUnusedLocalVar
from rules.af_no_cover_seq import NoCoverSeq
from rules.af_no_implication_property import NoImplicationProperty
from rules.af_delay_before_rose import DelayBeforeRose
from rules.af_delay_before_fell import DelayBeforeFell
from rules.af_delay_before_changed import DelayBeforeChanged
from rules.af_clk_without_edge import ClkWithoutEdge
from rules.af_mixed_impl_oper import MixedImplOper
from rules.af_nested_implication import NestedImplication
from rules.af_no_ub_repeat_ant import NoUbRepeatInAnt
from rules.af_immediate_sva_always_comb import ImmediateSvaAlwaysComb
from rules.af_seq_unused_local_var import SeqUnusedLocalVar
from rules.af_prop_local_var_not_in_conseq import PropLocalVarNotInConseq
from rules.af_unused_property import UnusedProperty
from rules.af_unused_sequence import UnusedSequence
from rules.af_throughout_rhs_bool import ThroughoutRhsBool

from rules.af_func_no_ev_then_alw import (
    AvoidStrongEventuallyAlwaysRule,
    AvoidStrongEventuallySAlwaysRule,
    AvoidEventuallyAlwaysRule,
    AvoidEventuallySAlwaysRule
)
from rules.af_func_no_weak_nxt import (
    AvoidUnboundedNexttimeRule,
    AvoidBoundedNexttimeRule
)

class SVALinter(AsFigoLinter):
    """Linter that applies multiple rules on SVA code."""

    def __init__(self, configFile, logLevel=logging.INFO):
        super().__init__(configFile=configFile, logLevel=logLevel)
        # Automatically discover and register all subclasses of AsFigoLintRule
        self.rules = [rule_cls(self) for rule_cls in AsFigoLintRule.__subclasses__()]

    def loadSyntaxTree(self, file_path):
        """Loads Verilog syntax tree using VeribleVerilogSyntax."""
        parser = verible_verilog_syntax.VeribleVerilogSyntax()
        return parser.parse_files([file_path], options={"gen_tree": True})

    def runOnSingleFile(self, filePath):
        """Runs all lint rules on a single file. Used by regression runner."""
        self.resetFileState(filePath)

        if not os.path.exists(filePath):
            self.logger.error(f"File not found: {filePath}")
            return

        treeData = self.loadSyntaxTree(filePath)
        for fp, fileData in treeData.items():
            self.logInfo("SVALint", f"Loaded test file: {filePath}")
            for rule in self.rules:
                rule.run(fp, fileData)

    def runOnFlist(self, flist_path):
        """Runs lint rules on all files listed in a filelist."""
        files = self._parseFlist(flist_path)
        for file_path in files:
            self.runOnSingleFile(file_path)

    def runCli(self):
        """Parses command-line arguments and triggers linter execution."""
        parser = argparse.ArgumentParser(description="AsFigo SVALint Engine")
        parser.add_argument("-t", "--test", help="Path to single SystemVerilog target file")
        parser.add_argument("-f", "--filelist", help="Path to filelist containing SystemVerilog target files")
        parser.add_argument("-c", "--config", default="config.toml", help="Path to rules configuration file")

        args = parser.parse_args()

        if args.config != "config.toml":
            self.rulesConfig = self.loadConfig(args.config)

        if args.test:
            self.runOnSingleFile(args.test)
        elif args.filelist:
            self.runOnFlist(args.filelist)
        else:
            parser.print_help()
            return 1

        self.logSummary()
        return 1 if self.totalErrorCount > 0 else 0


if __name__ == "__main__":
    linter = SVALinter(configFile="config.toml", logLevel=logging.INFO)
    sys.exit(linter.runCli())
