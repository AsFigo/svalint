# ----------------------------------------------------
# SPDX-FileCopyrightText: AsFigo Technologies, UK
# SPDX-FileCopyrightText: VerifWorks, India
# SPDX-License-Identifier: MIT
# ----------------------------------------------------

SVALINT := python3 ../bin/svalint.py

.PHONY: all clean

all:
	@echo "--- Running SVALint on fail example (expect violations) ---"
	$(SVALINT) -t sva_naming_f.sv || true
	@echo ""
	@echo "--- Running SVALint on pass example (expect 0 violations) ---"
	$(SVALINT) -t sva_naming_p.sv

clean:
	rm -rf tmp/ *.log
