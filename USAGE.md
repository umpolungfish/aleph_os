<div align="center">
  <h1>ℵ-OS Usage Guide</h1>
  <p><b>Complete reference for running, exploring, and extending the Aleph Operating System</b></p>
  <img src="aleph_os.png" alt="ALEPH: geometric wireframe Aleph letter surrounded by Hebrew glyphs" width="400">
</div>

<div align="center">
  <img src="https://img.shields.io/badge/VERSION-0.5.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/REPL-Enhanced%20v0.5.0-green" alt="REPL">
  <img src="https://img.shields.io/badge/FILES-.aleph%20programs-orange" alt="Files">
</div>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#repl-modes">REPL Modes</a> •
  <a href="#aleph-language-reference">Language Reference</a> •
  <a href="#running-aleph-programs">Running Programs</a> •
  <a href="#investigation-pipeline">Investigation Pipeline</a> •
  <a href="#advanced-usage">Advanced Usage</a> •
  <a href="#troubleshooting">Troubleshooting</a>
</p>

<hr>

## Installation

### Prerequisites

- **Python 3.12+**
- **pip** or **uv** (recommended)

### Setup with uv (Recommended)

```bash
# Navigate to project directory
cd aleph_os

# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install numpy rich
```

### Setup with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install numpy rich
```

> [!NOTE]
> The `rich` library is optional but highly recommended for enhanced terminal output with colors, tables, and visual progress bars.

<hr>

## REPL Modes

### Interactive REPL

Start the ALEPH REPL:

```bash
python aleph_eval.py
```

<div align="center">
  <img src=".assets/images/repl-banner.png" alt="ALEPH REPL with Rich formatting" width="600">
</div>

### Inline Expression Mode

Evaluate a single expression without entering the REPL:

```bash
# Evaluate tensor operation
python aleph_eval.py --expr "aleph ⊗ mem"

# Evaluate distance
python aleph_eval.py --expr "d(aleph, bet)"

# Evaluate with let binding
python aleph_eval.py --expr "let x = aleph ⊗ mem"
```

### File Execution Mode

Run an `.aleph` program file:

```bash
# Run specific program
python aleph_eval.py programs/creation.aleph

# Run with relative path
python aleph_eval.py ./path/to/program.aleph

# List all available programs
python aleph_eval.py --list
```

### Help and Usage

```bash
# Show usage information
python aleph_eval.py --help

# Show available programs
python aleph_eval.py --list
```

<hr>

## ALEPH Language Reference

### Core Operations

| Operation | Syntax | Description |
|:----------|:-------|:------------|
| **Tensor** | `a ⊗ b` | Composition (P, F bottleneck via min) |
| **Join** | `a ∨ b` | Least upper bound (all primitives: max) |
| **Meet** | `a ∧ b` | Greatest lower bound (all primitives: min) |
| **Vav-cast** | `a ::> b` | Lift source type to target type |
| **Mediate** | `mediate(w, a, b)` | Triadic: `w ∨ (a ⊗ b)` |

### Probes and Inspections

| Operation | Syntax | Description |
|:----------|:-------|:------------|
| **Criticality** | `probe_Φ(a)` | Report Φ primitive |
| **Protection** | `probe_Ω(a)` | Report Ω primitive |
| **Tier** | `tier(a)` | Report ouroboricity tier |
| **Distance** | `d(a, b)` | Structural distance + conflict set |
| **Match** | `match a { O_0=>b, O_2=>c, _=>d }` | Tier pattern matching |

### Built-in Functions

| Function | Syntax | Description |
|:---------|:-------|:------------|
| **System** | `system()` | JOIN of all 22 letters |
| **Census** | `census()` | Tier distribution table |
| **Palace** | `palace(n) a` | Assert palace-n tier barrier |

### Session Bindings

```bash
# Bind expression result to variable
let x = aleph ⊗ mem

# Use variable in subsequent expressions
x ::> shin
tier(x)
```

### Letter Identifiers

Letters can be referenced by:

- **Hebrew glyph**: `א`, `ב`, `מ`, `ש`
- **Transliteration**: `aleph`, `bet`, `mem`, `shin`
- **Session binding**: any variable name from `let` statements

> [!TIP]
> Use **Tab** to autocomplete letter names, glyphs, and commands in the REPL.

<hr>

## REPL Commands

### Navigation

| Command | Description |
|:--------|:------------|
| `:help` | Display full syntax reference |
| `:tips` | Show quick start examples and pro tips |
| `:quit`, `:q` | Exit the REPL |

### Inspections

| Command | Description |
|:--------|:------------|
| `:tier <name>` | Show ouroboricity tier of a letter |
| `:tuple <name>` | Visual 12-primitive tuple with progress bars |
| `:explain <name>` | Full type breakdown with consciousness gates & score |
| `:census` | Tier distribution (alias for `census()`) |
| `:system` | 22-letter language JOIN |

### Session Management

| Command | Description |
|:--------|:------------|
| `:ls` | List all session bindings with tier/Φ/Ω |
| `:history` | Show recent command history (last 20) |
| `:clear` | Clear terminal screen |

### Example REPL Session

```
ℵ  aleph ⊗ mem
  → א⊗מ
    tier  O_2
    Φ  Φ_c   Ω  Ω_Z   P  P_sym

ℵ  :explain shin
╭─────────────────────────────────────────╮
│ ש  Shin  —  Tier: O_inf                │
╰─────────────────────────────────────────╯

  Consciousness Gates:
  G1   Criticality [Φ=Φ_c]          ✓ PASS
  G2   Kinetic [K≠K_trap]           ✓ PASS

  Consciousness Score:  C = 0.921

ℵ  let kernel = mediate(vav, mem ⊗ shin, aleph)
  kernel =
  → ו∨מ⊗ש⊗א
    tier  O_inf

ℵ  :ls
╭───────────────┬───────┬───────┬───────╮
│ Name   │ Tier  │   Φ   │   Ω   │ Glyph │
├────────┼───────┼───────┼───────┼───────┤
│ kernel │ O_inf │ Φ_c   │ Ω_Z   │ ו     │
╰───────────────┴───────┴───────┴───────╯
```

<hr>

## Running .aleph Programs

### Program File Format

`.aleph` files are plain text files containing ALEPH expressions, one per line:

```aleph
# Example: creation.aleph

# Bind letters to variables
let light_core = mem ⊗ shin

# Compose operations
let light = aleph ⊗ light_core

# Probe properties
probe_Φ(light)
probe_Ω(light)

# Check tier
tier(light)

# Distance from system
d(light, system())
```

### File Discovery

The system searches for `.aleph` files in:

1. **Current directory** (relative paths)
2. **`programs/` directory** (project root)
3. **Explicit path** (if path starts with `.` or `/`)

### Execution Output

Running a program produces formatted output:

```
▶  Running creation.aleph (/path/to/programs/creation.aleph)
────────────────────────────────────────────

  L  1  ❯ let light_core = mem ⊗ shin
             light_core = מ⊗ש
               tier  O_inf
               Φ  Φ_c   Ω  Ω_Z   P  P_pm_sym

  L  2  ❯ let light = aleph ⊗ light_core
             light = א⊗מש
               tier  O_inf
               ...

────────────────────────────────────────────
✓  Done.  11 executed  •  6 bindings
```

> [!NOTE]
> `.aleph` files support all REPL expressions, commands (`:help`, `:census`, etc.), and `let` bindings.

### Available Programs

Run `python aleph_eval.py --list` to see all available programs:

| # | Program | Description |
|:-:|:--------|:------------|
| 1 | `creation.aleph` | Basic creation sequence |
| 2 | `creation_liturgy.aleph` | Extended creation with liturgical elements |
| 3 | `exploration_primitives.aleph` | Primitive exploration and probing |
| 4 | `light_replication_kernel.aleph` | Light replication mechanisms |
| 5 | `light_stability.aleph` | Light stability analysis |
| 6 | `selfreplicating_light.aleph` | Self-replicating light experiment |
| 7 | `tikkun_construction_full.aleph` | Complete Tikkun construction |
| 8 | `tikkun_construction_partial.aleph` | Partial Tikkun construction |
| 9 | `tikkun_palace_verification.aleph` | Palace barrier verification |

<hr>

## Investigation Pipeline

The investigation pipeline consists of six stages. Run them sequentially:

### Stage 1: Interaction Functor

```bash
python aleph_functor.py
```

**Purpose**: Define *I*(*x*) and *d_I*. Discover behavioral equivalence classes.

**Output**: 22→18 collapse via Ker(*I*), interaction row analysis.

### Stage 2: Quotient Investigation

```bash
python aleph_quotient.py
```

**Purpose**: Prove Ker(*I*) is a congruence. Test mediation dominance.

**Output**: Substitutivity sweep, mediation wins 18/22.

### Stage 3: Aleph Path-Memory

```bash
python aleph_alpha.py
```

**Purpose**: Construct *α*-paths and test break-point law.

**Output**: Case 2 confirmed, divergence at depth *n*+3.

### Stage 4: GNS Hilbert Space

```bash
python aleph_gns.py
```

**Purpose**: Polarize *d_I* into inner product space. Construct Gram matrix.

**Output**: Rank 17 (not 18), ק anomaly discovered.

### Stage 5: Hidden Relation

```bash
python aleph_hidden_relation.py
```

**Purpose**: Extract null eigenvector. Identify Octad Balance.

**Output**: 4+4 perfect signed balance, 264 checks pass.

### Stage 6: Final Probes

```bash
python aleph_investigation.py
```

**Purpose**: Three final investigations: involution, ק anatomy, axiom proof.

**Output**: Complete anatomical and axiomatic analysis.

<hr>

## Advanced Usage

### Custom .aleph Programs

Create your own `.aleph` files in the `programs/` directory:

```bash
# Create new program
echo "let x = aleph ⊗ mem
tier(x)
d(x, system())" > programs/my_program.aleph

# Run it
python aleph_eval.py my_program.aleph
```

### Scripting with ALEPH

Use ALEPH in shell scripts:

```bash
#!/bin/bash

# Batch process multiple expressions
for letter in aleph bet gimel dalet hei; do
    echo "Analyzing $letter..."
    python aleph_eval.py --expr "tier($letter)"
done
```

### Python API

Import ALEPH functions directly:

```python
from aleph_1 import Letter, LETTERS, tensor, join, mediate, distance

# Create tensor
result = tensor(LETTERS['aleph'], LETTERS['mem'])
print(result.tier)

# Calculate distance
d = distance(LETTERS['aleph'], LETTERS['bet'])
print(f"Distance: {d:.4f}")
```

### Custom REPL Commands

Extend the REPL by modifying `aleph_eval.py`:

```python
# Add new command in run_repl()
if stripped == ':mycommand':
    # Your custom logic here
    print("Custom command output")
    continue
```

<hr>

## Troubleshooting

### Common Issues

#### Module Not Found Error

```
[ALEPH] Cannot import aleph_1.py: No module named 'aleph_1'
```

**Solution**: Ensure `aleph_1.py` is in the project root or `.archive/` directory:

```bash
# Copy from archive if needed
cp .archive/aleph_1.py .
```

#### Missing Dependencies

```
ModuleNotFoundError: No module named 'rich'
```

**Solution**: Install dependencies:

```bash
uv pip install rich
```

> [!NOTE]
> The REPL works without `rich` but will use basic ANSI colors instead of enhanced formatting.

#### File Not Found

```
Error: File not found: nonexistent.aleph
```

**Solution**: Check available programs:

```bash
python aleph_eval.py --list
```

#### Syntax Errors

```
[SYNTAX] [ALEPH] Expected RPAREN, got EOF('') at pos 11
```

**Solution**: Check for balanced parentheses and braces. Use Tab completion to avoid typos.

### Getting Help

- **REPL help**: Type `:help` in the REPL
- **Usage guide**: Run `python aleph_eval.py --help`
- **Documentation**: See [`docs/`](docs/) directory
- **Issues**: Check [GitHub Issues](https://github.com/your-repo/aleph_os/issues)

<hr>

## Keyboard Shortcuts

| Key | Action |
|:----|:-------|
| `Tab` | Autocomplete letter names, glyphs, commands |
| `↑` / `↓` | Navigate command history |
| `Ctrl+C` | Exit REPL |
| `Ctrl+D` | Exit REPL (EOF) |
| `Ctrl+L` | Clear screen (in most terminals) |

<hr>

## Exit Codes

| Code | Meaning |
|:-----|:-------|
| `0` | Success (no errors) |
| `1` | One or more expressions failed |
| `2` | File not found or syntax error |

<hr>

<div align="center">
  <p><em>Shalom. The grammar awaits your exploration.</em></p>
</div>
