# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

import argparse
import os
import logging
import tomli
from af_lint_rule import AsFigoLintRule


class BaseLintLogger:
    """Base logging and configuration manager for the linting engine."""

    def __init__(self, prefix, configFile="config.toml", logLevel=logging.INFO, logFile="svalint_run.log"):
        self.prefix = prefix
        self.logger = logging.getLogger(f"{prefix}Logger")
        self.logger.setLevel(logLevel)

        formatter = logging.Formatter('%(message)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logLevel)
        stream_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(logFile, mode='a')
        file_handler.setLevel(logLevel)
        file_handler.setFormatter(formatter)

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

        self.rulesConfig = self.loadConfig(configFile)

        self.totalInfoCount = 0
        self.totalWarningCount = 0
        self.totalErrorCount = 0
        self.totalErrorList = []
        self.totalWarningList = []

        self.resetFileState("N/A")

    def loadConfig(self, configFile):
        """Loads rules configuration from TOML file."""
        try:
            with open(configFile, "rb") as file:
                config = tomli.load(file)
            return config.get("rules", {})
        except FileNotFoundError:
            self.logger.warning(f"{self.prefix}: Config file '{configFile}' not found. Using default settings.")
            return {}

    def ruleEnabled(self, ruleId):
        """Checks if a rule is enabled in config."""
        return self.rulesConfig.get(ruleId, True)

    def resetFileState(self, file_path):
        """Resets violation counters for a new target file."""
        self.currentFile = file_path
        self.infoCount = 0
        self.warningCount = 0
        self.errorCount = 0
        self.errorList = []
        self.warningList = []

    def resetGlobalState(self):
        """Resets global counters and rule execution metrics."""
        self.totalInfoCount = 0
        self.totalWarningCount = 0
        self.totalErrorCount = 0
        self.totalErrorList.clear()
        self.totalWarningList.clear()
        AsFigoLintRule.rule_count = 0

    def logInfo(self, ruleId, msg):
        """Logs informational messages."""
        self.infoCount += 1
        self.totalInfoCount += 1
        logMsg = f"{self.prefix}: [{self.currentFile}] INFO: {msg}"
        self.logger.info(logMsg)

    def logViolation(self, ruleId, msg, severity="ERROR"):
        """Logs a rule violation based on severity level."""
        if not self.ruleEnabled(ruleId):
            self.logger.debug(f"{self.prefix}: Rule [{ruleId}] is disabled and will not be logged.")
            return

        logMsg = f"{self.prefix}: [{self.currentFile}] Violation: [{ruleId}]:\n{msg}"

        if severity == "ERROR":
            self.errorCount += 1
            self.totalErrorCount += 1
            self.errorList.append(ruleId)
            self.totalErrorList.append(ruleId)
            self.logger.error(logMsg)
        elif severity == "WARNING":
            self.warningCount += 1
            self.totalWarningCount += 1
            self.warningList.append(ruleId)
            self.totalWarningList.append(ruleId)
            self.logger.warning(logMsg)
        else:
            raise ValueError(f"Unsupported severity level: {severity}")

    def logSummary(self):
        """Prints aggregated violation summary to stdout and log file."""
        self.logger.info("\n--------------------------------")
        self.logger.info("AsFigo SVALint Report Summary")
        self.logger.info(f"Total lint rules executed: {AsFigoLintRule.get_rule_count()}")
        self.logger.info("--------------------------------")

        self.logger.info("** Report counts by severity")
        self.logger.info(f"INFO    : {self.totalInfoCount}")
        self.logger.info(f"WARNING : {self.totalWarningCount}")
        self.logger.info(f"ERROR   : {self.totalErrorCount}")

        self.logger.info("\n** Report counts by ID")
        self._printRuleCounts(self.totalErrorList, "ERROR")
        self._printRuleCounts(self.totalWarningList, "WARNING")

        self.logger.info("--------------------------------\n")

    def _printRuleCounts(self, ruleList, severity):
        rule_dict = {}
        for rule_id in ruleList:
            rule_dict[rule_id] = rule_dict.get(rule_id, 0) + 1

        for rule_id, count in sorted(rule_dict.items(), key=lambda x: -x[1]):
            self.logger.info(f"[{rule_id}] {count}")


class AsFigoLinter(BaseLintLogger):
    """Core linter orchestration class."""

    def __init__(self, configFile="config.toml", logLevel=logging.INFO):
        super().__init__(prefix="AsFigo", configFile=configFile, logLevel=logLevel)

    def parseArguments(self):
        """Parses command-line arguments for single-file mode."""
        parser = argparse.ArgumentParser(description="AsFigoLinter Argument Parser")
        parser.add_argument("-t", "--test", required=True, help="Input test name (file path)")
        return parser.parse_args()

    def _parseFlist(self, flist_path):
        """Parses paths from a filelist file."""
        sv_files = []
        if not os.path.exists(flist_path):
            self.logger.error(f"Filelist '{flist_path}' not found.")
            return sv_files

        with open(flist_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('//') or line.startswith('#'):
                    continue
                line = os.path.expandvars(line)
                if line.startswith('+') or line.startswith('-'):
                    continue
                sv_files.append(line)

        return sv_files
