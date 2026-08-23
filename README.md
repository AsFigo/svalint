# SVALint

Linter for SystemVerilog Assertions (SVA). Following the philosophy of BYOL — Build Your Own Linter, SVALint is an example of how users can roll out their own linters!

**SVALint** is an open-source **minimalist** linter tool designed to enforce style and correctness rules for SystemVerilog Assertion blocks. It provides a framework for **Build Your Own Linter** (**BYOL**), allowing users to create their own custom lint rules while benefiting from built-in checks such as naming conventions, assertion labels, operator usage, performance rules, and other SVA best practices.

## Table of Contents

1. [BYOL - Build Your Own Linter](#byol---build-your-own-linter)
2. [Open Source](#open-source)
3. [Documentation](#documentation)
4. [Directory Structure](#directory-structure)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Test Cases](#test-cases)
8. [Adding New Lint Rules](#adding-new-lint-rules)
9. [Dependencies](#dependencies)
10. [License](#license)
11. [Credits](#credits)

## BYOL - Build Your Own Linter

The core concept of **SVALint** is **BYOL** (Build Your Own Linter), a framework that lets you easily define custom linting rules tailored to your specific needs. **SVALint** is flexible and extensible.

## Open Source

This project is **open source** and licensed under the MIT License. Contributions are welcome, and you are free to fork, modify, and distribute it according to your needs.

## Documentation

Full rule reference — rationale, violation examples, correct usage, and severity — is available at:

- GitHub Pages: https://asfigo.github.io/svalint/
- Source: [`docs/source/rules.rst`](docs/source/rules.rst)

## Directory Structure

```
svalint/
├── bin/
│   ├── svalint.py               ← CLI entry point; imports all rule classes
│   └── verible_verilog_syntax.py
├── docs/
│   ├── requirements.txt
│   └── source/
│       ├── conf.py
│       ├── index.rst
│       └── rules.rst            ← hand-crafted rule reference (rationale, examples, severity)
├── examples/
│   ├── sva_naming_f.sv          ← fail case: property without p_ prefix
│   ├── sva_naming_p.sv          ← pass case: property with correct p_ prefix
│   └── Makefile                 ← runs SVALint on both example files
├── src/
│   ├── af_lint_rule.py          ← AsFigoLintRule abstract base class
│   ├── asfigo_linter.py         ← BaseLintLogger + AsFigoLinter orchestration
│   └── rules/
│       └── af_*.py              ← individual rule implementations
└── sva_tests/                   ← simulation test benches for SVA rule validation
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/AsFigo/svalint.git
cd svalint
```

2. Install Verible (SystemVerilog parser):

   See: https://github.com/chipsalliance/verible

3. Install Python dependencies:

```bash
pip install anytree tomli
```

## Usage

### Single file

```bash
python3 bin/svalint.py -t <path_to_file.sv>
```

### Filelist

```bash
python3 bin/svalint.py -f <filelist.txt>
```

### Custom config

```bash
python3 bin/svalint.py -t my_file.sv -c my_config.toml
```

Rule IDs can be selectively disabled in `config.toml`:

```toml
[rules]
ASSERT_NAMING = false
PERF_NO_LARGE_DELAY = false
```

If `config.toml` is absent, all rules are enabled by default.

### Quick example

```bash
cd examples && make all
```

## Test Cases

Test files in `examples/` follow the naming convention:

- `*_f.sv` — **fail** case: must produce **≥ 1 error**
- `*_p.sv` — **pass** case: must produce **0 errors**

## Adding New Lint Rules

1. Create a new Python file inside `src/rules/`. The class must inherit from `AsFigoLintRule`.
2. Set `self.ruleID` in `__init__`.
3. Implement `apply(self, filePath, data)` using CST traversal via Verible.
4. Import the new class in `bin/svalint.py`.
5. Document the new rule in `docs/source/rules.rst` following the existing format.

## Lint Rules

For the full rule reference — rationale, violation examples, correct usage, and severity — see:

- [`docs/source/rules.rst`](docs/source/rules.rst)

## Dependencies

- Python 3.x
- [Verible](https://github.com/chipsalliance/verible) — SystemVerilog parser from Google/ChipsAlliance
- `anytree`
- `tomli`

## License

This project is **open source** and licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This **SVALint** linter is part of the **BYOL** (Build Your Own Linter) framework from **AsFigo Technologies**.

## Credits

The rules and guidelines in **SVALint** are based on the following sources:

- **SystemVerilog Assertions Handbook** — Ben Cohen, Ajeetha Kumari Venkatesan, Lisa Piper, Srinivasan Venkataramanan: Many of the rules in this linter are inspired by the coding practices and design patterns outlined in this book, which provides a comprehensive approach to SystemVerilog Assertions, focusing on best practices for code quality and maintainability.
- **lowRISC Coding Guidelines**: This linter also draws upon the coding standards and guidelines from the lowRISC project. Their best practices for SystemVerilog coding have been a key resource for defining rules related to naming conventions, encapsulation, and other critical aspects of design quality.
- **Verible**: An open-source SystemVerilog parser from Google, available via ChipsAlliance.
