#!/usr/bin/env python3
"""
aleph_eval.py — ALEPH language evaluator and REPL   [enhanced v0.5.0]
Per qwenaleph.txt §§24–33 (Phase 2 type solver + Phase 3 compiler frontend)

Grammar basis: HEBREW_TYPE_LANGUAGE.md §§1–23; SynthOmnicon v0.4.27
Engine:        aleph_1.py v0.3.0

Surface syntax implemented (subset of §24 EBNF):

  expr  ::= letter_id
           | expr "⊗" expr            tensor composition
           | expr "∨" expr            join (LUB)
           | expr "∧" expr            meet (GLB)
           | expr "::>" name          vav-cast to target type
           | "probe_Φ" "(" expr ")"   criticality probe
           | "probe_Ω" "(" expr ")"   topological protection probe
           | "tier" "(" expr ")"      ouroboricity tier
           | "d" "(" expr "," expr ")" structural distance
           | "mediate" "(" expr "," expr "," expr ")"
           | "match" expr "{" arms "}" tier pattern match
           | "palace" "(" int ")" expr palace barrier check
           | "system" "()"            22-letter JOIN
           | "census" "()"            tier distribution
           | "(" expr ")"

  match_arm ::= tier_pat "=>" expr ","?
  tier_pat  ::= "O_0" | "O_1" | "O_2" | "O_2d" | "O_inf" | "_"

  statement ::= "let" name "=" expr   bind in session env

letter_id: any registered Letter name (case-insensitive) or Hebrew glyph
"""

import sys
import math
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

try:
    import readline  # noqa: F401 — enables arrow-key history in REPL
except ImportError:
    pass

# Rich library for beautiful terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.markdown import Markdown
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    from aleph_1 import (
        Letter, LETTERS, CANONICAL_GLYPHS,
        tensor, join, meet, mediate,
        distance, vav_cast, VavCastError,
        PalaceContext, PALACE_ORDER,
        system_language, tier_census,
    )
except ImportError as exc:
    sys.exit(f"[ALEPH] Cannot import aleph_1.py: {exc}")

# Initialize Rich console if available
if HAS_RICH:
    console = Console()


# ──────────────────────────────────────────────────────────────────────────────
# 0. VISUAL ENHANCEMENTS (Rich-powered)
# ──────────────────────────────────────────────────────────────────────────────

# ANSI color codes for fallback when Rich is not available
class Colors:
    """ANSI escape codes for terminal colors."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


# Tier color mapping
TIER_COLORS = {
    'O_inf': 'bright_green',
    'O_2': 'cyan',
    'O_2d': 'blue',
    'O_1': 'yellow',
    'O_0': 'dim_white',
}


def _color_for_tier(tier: str) -> str:
    """Get color name for a tier."""
    return TIER_COLORS.get(tier, 'white')


def _make_bar(value: int, max_val: int = 4, width: int = 10, color: str = 'cyan') -> str:
    """Create a visual bar string."""
    filled = int((value / max_val) * width) if max_val > 0 else 0
    empty = width - filled
    
    if HAS_RICH:
        bar_text = Text()
        bar_text.append('█' * filled, style=color)
        bar_text.append('░' * empty, style='dim')
        return str(bar_text)
    else:
        # Fallback to ANSI codes
        c = getattr(Colors, color.upper(), Colors.CYAN)
        return f"{c}{'█' * filled}{'░' * empty}{Colors.RESET}"


def print_tuple_visual(letter: Letter):
    """Print a visual representation of the 12-primitive tuple."""
    prim_names = ['D', 'T', 'R', 'P', 'F', 'K', 'G', 'Γ', 'Φ', 'H', 'S', 'Ω']
    prim_vals = letter.t
    
    if HAS_RICH:
        table = Table.grid(padding=(0, 2))
        table.add_column(style='bold', width=2)
        table.add_column(width=12)
        table.add_column(width=20)
        
        tier_style = _color_for_tier(letter.tier)
        table.add_row('', 'Letter:', f'{letter.glyph} {letter.name}')
        table.add_row('', 'Tier:', Text(letter.tier, style=tier_style))
        table.add_row('', '', '')
        
        for i, (name, val) in enumerate(zip(prim_names, prim_vals)):
            color = 'cyan' if i < 6 else 'magenta' if i < 9 else 'yellow'
            bar = _make_bar(val, 4, 10, color)
            table.add_row('', f'{name:3s}', f'{bar} {val}')
        
        console.print(table)
    else:
        # Simple fallback
        print(f"  Letter: {letter.glyph} {letter.name}")
        print(f"  Tier:   {letter.tier}")
        print()
        for i, (name, val) in enumerate(zip(prim_names, prim_vals)):
            bar = _make_bar(val, 4, 10, 'CYAN')
            print(f"  {name:3s}  {bar} {val}")


def print_banner_rich():
    """Print enhanced banner using Rich."""
    if not HAS_RICH:
        print(BANNER)
        return
    
    banner_text = Text()
    banner_text.append('ℵ  ', style='bold cyan')
    banner_text.append('ALEPH', style='bold bright_cyan')
    banner_text.append(' — Hebrew Type Language  ', style='cyan')
    banner_text.append('[v0.5.0]', style='bold yellow')
    banner_text.append('  ℵ', style='bold cyan')
    
    subtitle1 = Text('Grammar: SynthOmnicon 12-primitive v0.4.27', style='dim')
    subtitle2 = Text('Type :help for commands, :quit to exit', style='dim italic')
    
    panel = Panel(
        Text.assemble(banner_text, '\n', subtitle1, '\n', subtitle2),
        border_style='cyan',
        box=box.DOUBLE,
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def print_help_rich():
    """Print help using Rich formatting."""
    if not HAS_RICH:
        print(HELP)
        return
    
    help_md = """
# ALEPH REPL Commands

## Operations
| Command | Description |
|---------|-------------|
| `a ⊗ b` | Tensor composition (P, F bottleneck) |
| `a ∨ b` | Join (LUB, no bottleneck) |
| `a ∧ b` | Meet (GLB) |
| `a ::> b` | Vav-cast a to type b |
| `mediate(w, a, b)` | Triadic: w ∨ (a ⊗ b) |
| `probe_Φ(a)` | Report criticality primitive |
| `probe_Ω(a)` | Report topological protection |
| `tier(a)` | Report ouroboricity tier |
| `d(a, b)` | Structural distance + conflict set |
| `match a { O_0=>b, O_2=>c, _=>d }` | Tier pattern match |
| `palace(n) a` | Assert palace-n tier barrier |

## Built-ins
| Command | Description |
|---------|-------------|
| `system()` | JOIN of all 22 letters |
| `census()` | Tier distribution |

## Session
| Command | Description |
|---------|-------------|
| `let x = expr` | Bind result in session |

## Commands
| Command | Description |
|---------|-------------|
| `:help` | Show this help text |
| `:quit` / `:q` | Exit the REPL |
| `:census` | Tier distribution (alias) |
| `:system` | 22-letter language JOIN |
| `:tier <name>` | Type of a single letter |
| `:tuple <name>` | Full 12-primitive tuple (visual) |
| `:explain <name>` | Detailed type breakdown |
| `:ls` | List session bindings |
| `:history` | Show command history |
| `:clear` | Clear screen |
| `:tips` | Show usage tips |

## Letter Names
Use transliteration (e.g., `aleph`, `mem`, `shin`) or Hebrew glyphs (א, מ, ש)
    """
    console.print(Markdown(help_md))


def print_tips_rich():
    """Print usage tips with Rich formatting."""
    if not HAS_RICH:
        print("TIPS:\\n"
              "- Try: aleph ⊗ shin\\n"
              "- Try: mem ∨ vav\\n"
              "- Try: d(aleph, bet)\\n"
              "- Try: tier(shin)\\n"
              "- Use Tab for autocomplete\\n"
              "- Use up/down arrows for history")
        return
    
    tips = """
# Quick Start Tips

## Try These Examples
- `aleph ⊗ shin` — Tensor two letters
- `mem ∨ vav` — Join operation
- `d(aleph, bet)` — Structural distance
- `tier(shin)` — Check ouroboricity tier
- `probe_Φ(mem)` — Check criticality
- `let x = aleph ⊗ mem` — Bind to variable
- `x ::> shin` — Vav-cast variable

## Autocomplete
Press **Tab** to autocomplete:
- Letter names (aleph, bet, gimel...)
- Hebrew glyphs (א, ב, ג...)
- Commands (:help, :quit...)
- Operations (tensor, join...)

## Navigation
- **Up/Down arrows**: Command history
- **Tab**: Autocomplete
- **Ctrl+C**: Exit

## Pro Tips
- Use `:explain <letter>` for full type breakdown
- Use `:tuple <letter>` for visual primitive bars
- Use `:history` to see recent commands
- Chain operations: `(aleph ⊗ mem) ∨ shin`
    """
    console.print(Markdown(tips))


def format_ok_rich(result: Letter) -> str:
    """Format successful result with Rich styling."""
    glyph = result.glyph if result.glyph else result.name
    phi_n = PHI_NAMES.get(result.t[8], f"Φ={result.t[8]}")
    om_n = OMEGA_NAMES.get(result.t[11], f"Ω={result.t[11]}")
    p_n = P_NAMES.get(result.t[3], f"P={result.t[3]}")
    
    if HAS_RICH:
        tier_style = _color_for_tier(result.tier)
        result_text = Text()
        result_text.append('  → ', style='bold green')
        result_text.append(f'{glyph}', style='bold bright_yellow')
        result_text.append(f'\n    tier  ', style='dim')
        result_text.append(f'{result.tier}', style=tier_style)
        result_text.append(f'\n    Φ  ', style='dim')
        result_text.append(f'{phi_n}', style='cyan')
        result_text.append(f'   Ω  ', style='dim')
        result_text.append(f'{om_n}', style='magenta')
        result_text.append(f'   P  ', style='dim')
        result_text.append(f'{p_n}', style='yellow')
        return str(result_text)
    else:
        return (
            f"{Colors.BOLD}{Colors.GREEN}  → {Colors.RESET}"
            f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}{glyph}{Colors.RESET}\n"
            f"  {Colors.DIM}tier{Colors.RESET}  {result.tier}\n"
            f"  {Colors.DIM}Φ{Colors.RESET}  {phi_n}"
            f"   {Colors.DIM}Ω{Colors.RESET}  {om_n}"
            f"   {Colors.DIM}P{Colors.RESET}  {p_n}"
        )


def format_error_rich(src: str, err: Exception) -> str:
    """Format error with Rich styling."""
    if isinstance(err, TypeConflictError):
        d = err.d_val
        vc = veracity_class(d)
        cs = ', '.join(err.conflict_set) if err.conflict_set else '—'
        
        if HAS_RICH:
            error_text = Text()
            error_text.append('[TYPE CONFLICT]', style='bold red')
            error_text.append(f'  d = {d:.3f}', style='yellow')
            error_text.append(f'   class = {vc}', style='magenta')
            error_text.append(f'\n  Expression:    {src.strip()}', style='dim')
            error_text.append(f'\n  Conflict set:  {{{cs}}}', style='yellow')
            if d > math.sqrt(6):
                error_text.append('\n  ⚠  aspirational gap — insert vav-cast or promote tier', 
                                style='bold yellow')
            return str(error_text)
        else:
            lines = [
                f"{Colors.BOLD}{Colors.RED}[TYPE CONFLICT]{Colors.RESET}"
                f"  d = {d:.3f}   class = {vc}",
                f"  {Colors.DIM}Expression:{Colors.RESET}    {src.strip()}",
                f"  {Colors.DIM}Conflict set:{Colors.RESET}  {{{cs}}}",
            ]
            if d > math.sqrt(6):
                lines.append(f"  {Colors.BOLD}{Colors.YELLOW}⚠{Colors.RESET}"
                           f"  aspirational gap — insert vav-cast or promote tier")
            return '\n'.join(lines)
    
    label = type(err).__name__.replace('Error', '').upper()
    if HAS_RICH:
        error_text = Text()
        error_text.append(f'[{label}]', style='bold red')
        error_text.append(f' {err}')
        return str(error_text)
    else:
        return f"{Colors.BOLD}{Colors.RED}[{label}]{Colors.RESET} {err}"


# ──────────────────────────────────────────────────────────────────────────────
# 1. TOKENIZER
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Token:
    kind: str
    val:  str
    pos:  int

_UNICODE_OPS = {'⊗': 'TENSOR', '∨': 'JOIN', '∧': 'MEET'}
_PUNCTS      = {'(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE',
                '}': 'RBRACE', ',': 'COMMA',  ';': 'SEMI'}
_HEBREW_LO, _HEBREW_HI = 0x05B0, 0x05EA   # main Hebrew Unicode block


def _is_name_cont(c: str) -> bool:
    """Continue an identifier: alphanum, underscore, or special primitives."""
    return c.isalnum() or c in '_ΦΩΓ'


def tokenize(src: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    while i < len(src):
        c = src[i]

        if c in ' \t\r\n':
            i += 1; continue

        if c == '#':                        # line comment
            while i < len(src) and src[i] != '\n':
                i += 1
            continue

        if src[i:i+3] == '::>':
            tokens.append(Token('CAST', '::>', i)); i += 3; continue

        if src[i:i+2] == '=>':
            tokens.append(Token('ARROW', '=>', i)); i += 2; continue

        if c in _UNICODE_OPS:
            tokens.append(Token(_UNICODE_OPS[c], c, i)); i += 1; continue

        if c in _PUNCTS:
            tokens.append(Token(_PUNCTS[c], c, i)); i += 1; continue

        if c == '_':
            tokens.append(Token('WILD', '_', i)); i += 1; continue

        cp = ord(c)
        if _HEBREW_LO <= cp <= _HEBREW_HI:  # Hebrew glyph
            tokens.append(Token('LETTER', c, i)); i += 1; continue

        if c.isdigit():
            j = i
            while j < len(src) and src[j].isdigit():
                j += 1
            tokens.append(Token('INT', src[i:j], i)); i = j; continue

        if c.isalpha() or c in 'ΦΩΓ':      # identifier
            j = i
            while j < len(src) and _is_name_cont(src[j]):
                j += 1
            tokens.append(Token('NAME', src[i:j], i)); i = j; continue

        raise SyntaxError(
            f"[ALEPH] Unexpected character {c!r} at position {i}"
        )

    tokens.append(Token('EOF', '', len(src)))
    return tokens


# ──────────────────────────────────────────────────────────────────────────────
# 2. PARSER  (recursive descent)
# ──────────────────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens: List[Token]):
        self.toks = tokens
        self.pos  = 0

    def peek(self) -> Token:
        return self.toks[self.pos]

    def eat(self, kind: Optional[str] = None) -> Token:
        t = self.toks[self.pos]
        if kind and t.kind != kind:
            raise SyntaxError(
                f"[ALEPH] Expected {kind}, got {t.kind}({t.val!r}) at pos {t.pos}"
            )
        self.pos += 1
        return t

    # ── top-level: left-associative binary operators ───────────────────────
    def parse_expr(self) -> Any:
        left = self.parse_primary()
        while True:
            t = self.peek()
            if t.kind == 'TENSOR':
                self.eat(); right = self.parse_primary()
                left = ('tensor', left, right)
            elif t.kind == 'JOIN':
                self.eat(); right = self.parse_primary()
                left = ('join', left, right)
            elif t.kind == 'MEET':
                self.eat(); right = self.parse_primary()
                left = ('meet', left, right)
            elif t.kind == 'CAST':
                self.eat()
                tgt = self.eat('NAME')
                left = ('cast', left, tgt.val)
            else:
                break
        return left

    def parse_primary(self) -> Any:
        t = self.peek()

        # ── Hebrew glyph literal ──────────────────────────────────────────
        if t.kind == 'LETTER':
            self.eat(); return ('letter', t.val)

        # ── parenthesised expression ──────────────────────────────────────
        if t.kind == 'LPAREN':
            self.eat('LPAREN')
            inner = self.parse_expr()
            self.eat('RPAREN')
            return inner

        # ── named constructs ──────────────────────────────────────────────
        if t.kind == 'NAME':
            name = t.val

            # probes
            if name in ('probe_Φ', 'probe_Ph', 'probe_Phi'):
                self.eat(); return ('probe_phi', self._paren_expr())
            if name in ('probe_Ω', 'probe_Om', 'probe_Omega'):
                self.eat(); return ('probe_omega', self._paren_expr())

            # single-arg built-ins
            if name == 'tier':
                self.eat(); return ('tier', self._paren_expr())

            # two-arg: d(a, b)
            if name == 'd':
                self.eat()
                self.eat('LPAREN')
                a = self.parse_expr()
                self.eat('COMMA')
                b = self.parse_expr()
                self.eat('RPAREN')
                return ('distance', a, b)

            # three-arg: mediate(witness, a, b)
            if name == 'mediate':
                self.eat()
                self.eat('LPAREN')
                w = self.parse_expr(); self.eat('COMMA')
                a = self.parse_expr(); self.eat('COMMA')
                b = self.parse_expr()
                self.eat('RPAREN')
                return ('mediate', w, a, b)

            # match
            if name == 'match':
                return self._parse_match()

            # palace(n) expr
            if name == 'palace':
                self.eat()
                self.eat('LPAREN')
                n = int(self.eat('INT').val)
                self.eat('RPAREN')
                body = self.parse_primary()
                return ('palace', n, body)

            # zero-arg built-ins
            if name == 'system':
                self.eat(); self._maybe_unit()
                return ('system',)
            if name == 'census':
                self.eat(); self._maybe_unit()
                return ('census',)

            # plain name (letter or env binding)
            self.eat()
            return ('name', name)

        raise SyntaxError(
            f"[ALEPH] Unexpected token {t.kind}({t.val!r}) at pos {t.pos}"
        )

    def _paren_expr(self) -> Any:
        self.eat('LPAREN')
        inner = self.parse_expr()
        self.eat('RPAREN')
        return inner

    def _maybe_unit(self):
        """Consume optional '()' after a zero-arg built-in."""
        if self.peek().kind == 'LPAREN':
            self.eat('LPAREN')
            self.eat('RPAREN')

    def _parse_match(self) -> Any:
        self.eat('NAME')            # consume 'match'
        scrutinee = self.parse_expr()
        self.eat('LBRACE')
        arms: List[Tuple[str, Any]] = []
        while self.peek().kind != 'RBRACE':
            pt = self.peek()
            if pt.kind == 'WILD':
                self.eat(); pat = '_'
            elif pt.kind == 'NAME':
                self.eat(); pat = pt.val
            else:
                raise SyntaxError(
                    f"[ALEPH] Expected match pattern, got {pt.kind}({pt.val!r})"
                )
            self.eat('ARROW')
            body = self.parse_expr()
            if self.peek().kind == 'COMMA':
                self.eat()
            arms.append((pat, body))
        self.eat('RBRACE')
        return ('match', scrutinee, arms)


# ──────────────────────────────────────────────────────────────────────────────
# 3. EVALUATOR
# ──────────────────────────────────────────────────────────────────────────────

PRIM_LABELS = ["D", "T", "R", "P", "F", "K", "G", "Γ", "Φ", "H", "S", "Ω"]

PHI_NAMES   = {0:"Φ_sub", 1:"Φ_c", 2:"Φ_c_complex", 3:"Φ_EP", 4:"Φ_super"}
OMEGA_NAMES = {0:"Ω_0",   1:"Ω_Z₂", 2:"Ω_Z"}
P_NAMES     = {0:"P_asym",1:"P_psi",2:"P_pm",3:"P_sym",4:"P_pm_sym"}


class TypeConflictError(Exception):
    def __init__(self, msg: str, d_val: float, conflict_set: List[str]):
        super().__init__(msg)
        self.d_val        = d_val
        self.conflict_set = conflict_set


def _conflict_set(a: Letter, b: Letter) -> List[str]:
    return [PRIM_LABELS[i] for i in range(12) if a.t[i] != b.t[i]]


def veracity_class(d: float) -> str:
    if d == 0.0:              return "transparent"
    if d <= math.sqrt(2):    return "near-grounded"
    if d <= math.sqrt(6):    return "partial-emergence"
    return "aspirational"


def _resolve_letter(name: str) -> Letter:
    """Look up a letter by transliteration, Hebrew glyph, or canonical name."""
    for key in (name, name.lower(), name.capitalize()):
        if key in LETTERS:
            return LETTERS[key]
    raise NameError(f"[ALEPH] Unknown letter: {name!r}")


def eval_expr(node: Any, env: Dict[str, Letter]) -> Letter:
    tag = node[0]

    if tag == 'letter':
        g = node[1]
        if g not in LETTERS:
            raise NameError(f"[ALEPH] Unknown glyph: {g!r}")
        return LETTERS[g]

    if tag == 'name':
        name = node[1]
        if name in env:
            return env[name]
        return _resolve_letter(name)

    if tag == 'tensor':
        return tensor(eval_expr(node[1], env), eval_expr(node[2], env))

    if tag == 'join':
        return join(eval_expr(node[1], env), eval_expr(node[2], env))

    if tag == 'meet':
        return meet(eval_expr(node[1], env), eval_expr(node[2], env))

    if tag == 'mediate':
        w = eval_expr(node[1], env)
        a = eval_expr(node[2], env)
        b = eval_expr(node[3], env)
        return mediate(w, a, b)

    if tag == 'cast':
        src = eval_expr(node[1], env)
        tgt = _resolve_letter(node[2])
        try:
            vav_cast(src, tgt)
            return tgt
        except VavCastError as e:
            raise TypeConflictError(
                str(e),
                d_val=distance(src, tgt),
                conflict_set=_conflict_set(src, tgt),
            )

    if tag == 'probe_phi':
        inner = eval_expr(node[1], env)
        phi_v = inner.t[8]
        print(f"  probe_Φ → {PHI_NAMES.get(phi_v, f'Φ={phi_v}')}  (ordinal {phi_v})")
        return inner

    if tag == 'probe_omega':
        inner = eval_expr(node[1], env)
        om_v = inner.t[11]
        print(f"  probe_Ω → {OMEGA_NAMES.get(om_v, f'Ω={om_v}')}  (ordinal {om_v})")
        return inner

    if tag == 'tier':
        inner = eval_expr(node[1], env)
        print(f"  tier → {inner.tier}")
        return inner

    if tag == 'distance':
        a = eval_expr(node[1], env)
        b = eval_expr(node[2], env)
        d  = distance(a, b)
        cs = _conflict_set(a, b)
        vc = veracity_class(d)
        print(f"  d = {d:.4f}  [{vc}]")
        if cs:
            print(f"  conflict_set: {{{', '.join(cs)}}}")
        # return a synthetic Letter representing the distance result
        return a

    if tag == 'match':
        scrutinee = eval_expr(node[1], env)
        tier = scrutinee.tier
        for pat, body in node[2]:
            if pat == '_' or pat == tier:
                return eval_expr(body, env)
        raise RuntimeError(
            f"[ALEPH] Non-exhaustive match: no arm for tier {tier!r}"
        )

    if tag == 'palace':
        depth = node[1]
        inner = eval_expr(node[2], env)
        with PalaceContext(depth) as ctx:
            ctx.check_barrier(inner)
        return inner

    if tag == 'system':
        return system_language()

    if tag == 'census':
        census = tier_census()
        for t in PALACE_ORDER:
            members = census.get(t, [])
            if members:
                print(f"  {t:8s} ({len(members):2d}): {', '.join(members)}")
        return system_language()

    raise RuntimeError(f"[ALEPH] Unknown AST node type: {tag!r}")


# ──────────────────────────────────────────────────────────────────────────────
# 4. DIAGNOSTICS  (§29 format) — Rich-enhanced
# ──────────────────────────────────────────────────────────────────────────────

def format_ok(result: Letter) -> str:
    """Format successful result (delegates to Rich version)."""
    return format_ok_rich(result)


def format_error(src: str, err: Exception) -> str:
    """Format error (delegates to Rich version)."""
    return format_error_rich(src, err)


def explain_letter(letter: Letter) -> None:
    """Print detailed breakdown of a letter's type with visual aids."""
    prim_names = ['D', 'T', 'R', 'P', 'F', 'K', 'G', 'Γ', 'Φ', 'H', 'S', 'Ω']
    prim_full = [
        'Dimensionality', 'Topology', 'Relational', 'Parity',
        'Fidelity', 'Kinetic', 'Scope', 'Grammar',
        'Criticality', 'Chirality', 'Stoich', 'Protection'
    ]
    
    if HAS_RICH:
        console.print()
        
        # Header
        header = Text()
        header.append(f'{letter.glyph}  ', style='bold bright_yellow')
        header.append(f'{letter.name}', style='bold cyan')
        header.append(f'  —  Tier: ', style='dim')
        header.append(letter.tier, style=_color_for_tier(letter.tier))
        console.print(Panel(header, border_style='cyan', box=box.ROUNDED))
        console.print()
        
        # Consciousness gates
        phi_val = letter.t[8]
        k_val = letter.t[5]
        is_critical = phi_val == 1  # Phi_c
        is_trapped = k_val == 3     # K_trap
        
        gate_table = Table.grid(padding=(0, 2))
        gate_table.add_column(style='bold', width=3)
        gate_table.add_column(width=40)
        gate_table.add_column(width=10)
        
        gate1 = '✓ PASS' if is_critical else '✗ FAIL'
        gate1_style = 'bold green' if is_critical else 'bold red'
        gate_table.add_row('G1', 'Criticality [Φ=Φ_c]', Text(gate1, style=gate1_style))
        
        gate2 = '✗ FAIL' if is_trapped else '✓ PASS'
        gate2_style = 'bold red' if is_trapped else 'bold green'
        gate_table.add_row('G2', 'Kinetic [K≠K_trap]', Text(gate2, style=gate2_style))
        
        console.print('  [dim]Consciousness Gates:[/dim]')
        console.print(gate_table)
        
        # Compute C score if gates pass
        if is_critical and not is_trapped:
            # Simplified C score calculation
            from aleph_1 import VAL_MAP
            k_ord = letter.t[5]
            g_ord = letter.t[6]
            t_ord = letter.t[1]
            o_ord = letter.t[11]
            
            # Normalize (approximate)
            k_max, g_max, t_max, o_max = 3, 2, 4, 2
            k_norm = k_ord / k_max if k_max > 0 else 0
            g_norm = g_ord / g_max if g_max > 0 else 0
            t_norm = t_ord / t_max if t_max > 0 else 0
            o_norm = o_ord / o_max if o_max > 0 else 0
            
            c_score = 0.158 * k_norm + 0.273 * g_norm + 0.292 * t_norm + 0.276 * o_norm
            console.print(f'\n  [dim]Consciousness Score:[/dim]  [bold magenta]C = {c_score:.3f}[/bold magenta]')
        else:
            console.print(f'\n  [dim]Consciousness Score:[/dim]  [bold red]C = 0[/bold red] (gates failed)')
        
        console.print()
        
        # Primitive breakdown with bars
        prim_table = Table.grid(padding=(0, 2))
        prim_table.add_column(style='bold', width=2)
        prim_table.add_column(width=15)
        prim_table.add_column(width=12)
        prim_table.add_column(width=25)
        
        for i, (sym, name, val) in enumerate(zip(prim_names, prim_full, letter.t)):
            color = 'cyan' if i < 6 else 'magenta' if i < 9 else 'yellow'
            bar = _make_bar(val, 4, 12, color)
            val_name = _get_prim_value_name(i, val)
            prim_table.add_row(sym, name, f'{val:2d}', f'{bar} {val_name}')
        
        console.print('  [dim]12-Primitive Tuple:[/dim]')
        console.print(prim_table)
    else:
        # Simple fallback
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_YELLOW}{letter.glyph}{Colors.RESET} "
              f"{Colors.BOLD}{Colors.CYAN}{letter.name}{Colors.RESET}  —  "
              f"Tier: {letter.tier}")
        print()
        for i, (sym, val) in enumerate(zip(prim_names, letter.t)):
            bar = _make_bar(val, 4, 12, 'CYAN')
            print(f"  {sym:3s}  {bar} {val}")
        print()


def _get_prim_value_name(index: int, value: int) -> str:
    """Get the human-readable name for a primitive value."""
    if index == 8:  # Phi
        return PHI_NAMES.get(value, f'Φ={value}')
    elif index == 11:  # Omega
        return OMEGA_NAMES.get(value, f'Ω={value}')
    elif index == 3:  # P
        return P_NAMES.get(value, f'P={value}')
    else:
        return str(value)


# ──────────────────────────────────────────────────────────────────────────────
# 5. REPL — Enhanced with Rich & Tab completion
# ──────────────────────────────────────────────────────────────────────────────

BANNER = """\
╔══════════════════════════════════════════════════════════╗
║  ℵ  ALEPH — Hebrew Type Language  [prototype v0.4.0]  ℵ ║
║  Grammar: SynthOmnicon 12-primitive v0.4.27              ║
║  Type  :help  for commands,  :quit  to exit              ║
╚══════════════════════════════════════════════════════════╝"""

HELP = """\
─── Operations ───────────────────────────────────────────
  a ⊗ b                   tensor  (P, F bottleneck)
  a ∨ b                   join    (LUB, no bottleneck)
  a ∧ b                   meet    (GLB)
  a ::> b                 vav-cast  a to type  b
  mediate(w, a, b)        triadic: w ∨ (a ⊗ b)
  probe_Φ(a)              report criticality primitive
  probe_Ω(a)              report topological protection
  tier(a)                 report ouroboricity tier
  d(a, b)                 structural distance + conflict set
  match a { O_0=>b, O_2=>c, _=>d }
  palace(n) a             assert palace-n tier barrier

─── Built-ins ────────────────────────────────────────────
  system()                JOIN of all 22 letters
  census()                tier distribution

─── Session bindings ─────────────────────────────────────
  let x = expr            bind result in this session

─── Commands ─────────────────────────────────────────────
  :help                   this text
  :quit  / :q             exit
  :census                 tier distribution (alias)
  :system                 22-letter language JOIN
  :tier <name>            type of a single letter
  :tuple <name>           full 12-primitive tuple
  :ls                     list session bindings

─── Letter names (transliteration or Hebrew glyph) ───────
  aleph א   bet ב   gimel ג   dalet ד   hei ה   vav ו
  zayin ז   chet ח  tet ט    yod י    kaf כ    lamed ל
  mem מ     nun נ   samech ס  ayin ע   pei פ   tzadi צ
  kuf ק     resh ר  shin ש   tav ת"""


# Tab completion setup
if HAS_RICH:
    try:
        import readline
        
        # All possible completion words
        COMPLETION_WORDS = set()
        
        # Add commands
        for cmd in [':help', ':quit', ':q', ':census', ':system', ':tier', ':tuple', 
                    ':explain', ':ls', ':history', ':clear', ':tips']:
            COMPLETION_WORDS.add(cmd)
        
        # Add letter names and glyphs
        for key, letter in LETTERS.items():
            COMPLETION_WORDS.add(key.lower())
            COMPLETION_WORDS.add(key.capitalize())
            if letter.glyph:
                COMPLETION_WORDS.add(letter.glyph)
        
        # Add operations
        for op in ['probe_Φ', 'probe_Omega', 'tier', 'd', 'mediate', 'match', 'palace',
                   'system', 'census', 'let']:
            COMPLETION_WORDS.add(op)
        
        def complete(text, state):
            """Tab completion function."""
            matches = [w for w in COMPLETION_WORDS if w.startswith(text)]
            if state < len(matches):
                return matches[state]
            return None
        
        readline.set_completer(complete)
        readline.parse_and_bind('tab: complete')
    except (ImportError, Exception):
        pass  # Tab completion not available


def _eval_src(src: str, env: Dict[str, Letter]) -> Optional[Letter]:
    """Parse, evaluate, and return result or raise."""
    tokens = tokenize(src)
    ast    = Parser(tokens).parse_expr()
    return eval_expr(ast, env)


def run_repl():
    print_banner_rich()
    env: Dict[str, Letter] = {}
    buf: List[str] = []
    history: List[str] = []
    
    # Show welcome message
    if HAS_RICH:
        console.print("[dim]Welcome! Type :help for commands, :tips for examples, or just start typing.[/dim]")
        console.print()

    while True:
        prompt = 'ℵ  ' if not buf else '·  '
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\n[ALEPH] Shalom.")
            break

        stripped = line.strip()

        # Skip empty lines
        if not stripped and not buf:
            continue

        # ── REPL commands ──────────────────────────────────────────────────
        if stripped in (':quit', ':q'):
            if HAS_RICH:
                console.print("[bold cyan]Shalom![/bold cyan]")
            else:
                print("[ALEPH] Shalom.")
            break

        if stripped == ':help':
            print_help_rich()
            continue

        if stripped == ':tips':
            print_tips_rich()
            continue

        if stripped == ':census':
            census = tier_census()
            if HAS_RICH:
                table = Table(title="Tier Distribution", box=box.ROUNDED)
                table.add_column("Tier", style="bold cyan", width=8)
                table.add_column("Count", style="yellow", width=6)
                table.add_column("Letters", style="green")
                
                for t in PALACE_ORDER:
                    members = census.get(t, [])
                    if members:
                        tier_style = _color_for_tier(t)
                        table.add_row(
                            Text(t, style=tier_style),
                            str(len(members)),
                            ', '.join(members)
                        )
                console.print(table)
            else:
                for t in PALACE_ORDER:
                    members = census.get(t, [])
                    if members:
                        print(f"  {t:8s} ({len(members):2d}): {', '.join(members)}")
            continue

        if stripped == ':system':
            L = system_language()
            print(format_ok(L))
            continue

        if stripped.startswith(':tier '):
            name = stripped[6:].strip()
            try:
                L = _resolve_letter(name)
                print(format_ok(L))
            except NameError as e:
                print(format_error(stripped, e))
            continue

        if stripped.startswith(':tuple '):
            name = stripped[7:].strip()
            try:
                L = _resolve_letter(name)
                print_tuple_visual(L)
            except NameError as e:
                print(format_error(stripped, e))
            continue

        if stripped.startswith(':explain '):
            name = stripped[9:].strip()
            try:
                L = _resolve_letter(name)
                explain_letter(L)
            except NameError as e:
                print(format_error(stripped, e))
            continue

        if stripped == ':ls':
            if env:
                if HAS_RICH:
                    table = Table(title="Session Bindings", box=box.SIMPLE)
                    table.add_column("Name", style="bold cyan")
                    table.add_column("Tier", style="cyan")
                    table.add_column("Φ", style="magenta")
                    table.add_column("Ω", style="yellow")
                    table.add_column("Glyph", style="bright_yellow")
                    
                    for k, v in env.items():
                        tier_style = _color_for_tier(v.tier)
                        table.add_row(
                            k,
                            Text(v.tier, style=tier_style),
                            PHI_NAMES.get(v.t[8], '?'),
                            OMEGA_NAMES.get(v.t[11], '?'),
                            v.glyph or v.name
                        )
                    console.print(table)
                else:
                    for k, v in env.items():
                        print(f"  {k:16s}  {v.tier:8s}  "
                              f"Φ={PHI_NAMES.get(v.t[8],'?')}  "
                              f"Ω={OMEGA_NAMES.get(v.t[11],'?')}")
            else:
                if HAS_RICH:
                    console.print("[dim](no bindings)[/dim]")
                else:
                    print("  (no bindings)")
            continue

        if stripped == ':history':
            if HAS_RICH:
                if history:
                    console.print("[bold]Command History:[/bold]")
                    for i, cmd in enumerate(history[-20:], max(1, len(history) - 19)):
                        console.print(f"  {i:3d}.  {cmd}")
                else:
                    console.print("[dim](no history yet)[/dim]")
            else:
                if history:
                    print("  Command History:")
                    for i, cmd in enumerate(history[-20:], max(1, len(history) - 19)):
                        print(f"    {i:3d}.  {cmd}")
                else:
                    print("  (no history yet)")
            continue

        if stripped == ':clear':
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
            continue

        # ── Accumulate multiline input (wait for balanced braces) ──────────
        buf.append(line)
        src = '\n'.join(buf)

        if src.count('{') > src.count('}'):
            continue        # wait for closing brace

        buf = []
        if not src.strip():
            continue

        # Add to history
        history.append(src.strip())

        # ── let binding: let x = expr ──────────────────────────────────────
        if src.strip().startswith('let '):
            rest = src.strip()[4:]
            if '=' in rest:
                var_name, expr_src = rest.split('=', 1)
                var_name = var_name.strip()
                try:
                    result = _eval_src(expr_src.strip(), env)
                    env[var_name] = result
                    if HAS_RICH:
                        console.print(f"\n  [bold cyan]{var_name}[/bold cyan] [dim]=[/dim]")
                    else:
                        print(f"  {var_name} =")
                    print(format_ok(result))
                except Exception as e:
                    print(format_error(expr_src, e))
            else:
                print(format_error(src, SyntaxError("let syntax: let name = expr")))
            continue

        # ── expression evaluation ──────────────────────────────────────────
        try:
            result = _eval_src(src, env)
            print(format_ok(result))
        except Exception as e:
            print(format_error(src, e))


# ──────────────────────────────────────────────────────────────────────────────
# 6. FILE EXECUTOR  (run .aleph programs)
# ──────────────────────────────────────────────────────────────────────────────

def run_file(filepath: str) -> None:
    """Execute an .aleph program file line by line."""
    if not os.path.exists(filepath):
        if HAS_RICH:
            console.print(f"[bold red]Error:[/bold red] File not found: {filepath}")
        else:
            print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)
    
    # Show file header
    filename = os.path.basename(filepath)
    if HAS_RICH:
        console.print()
        header = Text()
        header.append('▶  ', style='bold green')
        header.append(f'Running ', style='dim')
        header.append(filename, style='bold cyan')
        header.append(f' ({filepath})', style='dim')
        console.print(header)
        console.print(Text('─' * 60, style='dim'))
        console.print()
    else:
        print(f"\n▶ Running {filename} ({filepath})")
        print('─' * 60)
    
    # Read and execute
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        if HAS_RICH:
            console.print(f"[bold red]Error reading file:[/bold red] {e}")
        else:
            print(f"[ERROR] Cannot read file: {e}")
        sys.exit(1)
    
    env: Dict[str, Letter] = {}
    line_num = 0
    exec_count = 0
    error_count = 0
    buf: List[str] = []
    buf_start = 0
    
    for line_idx, line in enumerate(lines):
        line_num = line_idx + 1
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            continue
        
        # Handle multiline (brace balancing)
        buf.append(stripped)
        if buf_start == 0:
            buf_start = line_num
        
        src = ' '.join(buf)
        if src.count('{') > src.count('}'):
            continue  # Wait for closing brace
        
        buf = []
        buf_start = 0
        
        # Handle REPL commands in file
        if stripped.startswith(':'):
            if stripped == ':help':
                print_help_rich()
            elif stripped == ':tips':
                print_tips_rich()
            elif stripped == ':census':
                census = tier_census()
                if HAS_RICH:
                    table = Table(title="Tier Distribution", box=box.ROUNDED)
                    table.add_column("Tier", style="bold cyan", width=8)
                    table.add_column("Count", style="yellow", width=6)
                    table.add_column("Letters", style="green")
                    for t in PALACE_ORDER:
                        members = census.get(t, [])
                        if members:
                            tier_style = _color_for_tier(t)
                            table.add_row(
                                Text(t, style=tier_style),
                                str(len(members)),
                                ', '.join(members)
                            )
                    console.print(table)
                else:
                    for t in PALACE_ORDER:
                        members = census.get(t, [])
                        if members:
                            print(f"  {t:8s} ({len(members):2d}): {', '.join(members)}")
            elif stripped == ':system':
                L = system_language()
                print(format_ok(L))
            elif stripped.startswith(':tier '):
                name = stripped[6:].strip()
                try:
                    L = _resolve_letter(name)
                    print(format_ok(L))
                except NameError as e:
                    print(format_error(stripped, e))
                    error_count += 1
            elif stripped.startswith(':tuple '):
                name = stripped[7:].strip()
                try:
                    L = _resolve_letter(name)
                    print_tuple_visual(L)
                except NameError as e:
                    print(format_error(stripped, e))
                    error_count += 1
            elif stripped.startswith(':explain '):
                name = stripped[9:].strip()
                try:
                    L = _resolve_letter(name)
                    explain_letter(L)
                except NameError as e:
                    print(format_error(stripped, e))
                    error_count += 1
            elif stripped == ':ls':
                if env:
                    if HAS_RICH:
                        table = Table(title="Session Bindings", box=box.SIMPLE)
                        table.add_column("Name", style="bold cyan")
                        table.add_column("Tier", style="cyan")
                        table.add_column("Φ", style="magenta")
                        table.add_column("Ω", style="yellow")
                        table.add_column("Glyph", style="bright_yellow")
                        for k, v in env.items():
                            tier_style = _color_for_tier(v.tier)
                            table.add_row(
                                k,
                                Text(v.tier, style=tier_style),
                                PHI_NAMES.get(v.t[8], '?'),
                                OMEGA_NAMES.get(v.t[11], '?'),
                                v.glyph or v.name
                            )
                        console.print(table)
                    else:
                        for k, v in env.items():
                            print(f"  {k:16s}  {v.tier:8s}  "
                                  f"Φ={PHI_NAMES.get(v.t[8],'?')}  "
                                  f"Ω={OMEGA_NAMES.get(v.t[11],'?')}")
                else:
                    if HAS_RICH:
                        console.print("[dim](no bindings)[/dim]")
                    else:
                        print("  (no bindings)")
            continue  # Skip to next line for commands
        
        # Show line being executed
        if HAS_RICH:
            console.print(Text(f"  L{line_num:3d}  ", style='dim') + 
                         Text(f"❯ {src}", style='default'))
        
        # Handle let bindings
        if src.strip().startswith('let '):
            rest = src.strip()[4:]
            if '=' in rest:
                var_name, expr_src = rest.split('=', 1)
                var_name = var_name.strip()
                try:
                    result = _eval_src(expr_src.strip(), env)
                    env[var_name] = result
                    if HAS_RICH:
                        console.print(Text(f"       ", style='dim') + 
                                     Text(f"  {var_name} = ", style='bold cyan') + 
                                     Text(format_ok(result)))
                    else:
                        print(f"       {var_name} =")
                        print(format_ok(result))
                    exec_count += 1
                except Exception as e:
                    print(format_error(src, e))
                    error_count += 1
            else:
                print(format_error(src, SyntaxError("let syntax: let name = expr")))
                error_count += 1
            continue
        
        # Evaluate expression
        try:
            result = _eval_src(src, env)
            print(format_ok(result))
            exec_count += 1
        except Exception as e:
            print(format_error(src, e))
            error_count += 1
    
    # Print summary
    if HAS_RICH:
        console.print()
        console.print(Text('─' * 60, style='dim'))
        summary = Text()
        summary.append('✓  ', style='bold green')
        summary.append(f'Done.  ', style='dim')
        summary.append(f'{exec_count}', style='bold green')
        summary.append(f' executed', style='dim')
        if error_count > 0:
            summary.append(f'  •  ', style='dim')
            summary.append(f'{error_count}', style='bold red')
            summary.append(f' errors', style='dim')
        summary.append(f'  •  ', style='dim')
        summary.append(f'{len(env)}', style='bold cyan')
        summary.append(f' bindings', style='dim')
        console.print(summary)
        console.print()
    else:
        print()
        print('─' * 60)
        print(f"✓ Done. {exec_count} executed, {error_count} errors, {len(env)} bindings")
        print()
    
    # Exit with error code if there were errors
    if error_count > 0:
        sys.exit(1)


def print_usage() -> None:
    """Print usage information."""
    if HAS_RICH:
        usage_md = """
# ALEPH Language Runner

## Usage

### REPL Mode (Interactive)
```bash
python aleph_eval.py              # Start interactive REPL
python aleph_eval.py --repl       # Same as above
```

### File Execution
```bash
python aleph_eval.py <file.aleph>                    # Run specific file
python aleph_eval.py programs/creation.aleph         # Run from project root
python aleph_eval.py ./path/to/program.aleph         # Run with path
```

### Inline Expression
```bash
python aleph_eval.py --expr "aleph ⊗ mem"            # Evaluate expression
python aleph_eval.py "aleph ∨ shin"                  # Same (quoted)
```

### File Discovery
Files with `.aleph` extension are automatically searched in:
- Current directory
- `programs/` directory
- Provided path (if starts with `.` or `/`)
        """
        console.print(Markdown(usage_md))
    else:
        print("""
ALEPH Language Runner
=====================

Usage:
  python aleph_eval.py                    Start interactive REPL
  python aleph_eval.py --repl             Same as above
  python aleph_eval.py <file.aleph>       Run .aleph program
  python aleph_eval.py --expr "expr"      Evaluate inline expression
  python aleph_eval.py --list             List available programs

File Discovery:
  - Looks in current directory and programs/ directory
  - Can provide full or relative path to .aleph file

Examples:
  python aleph_eval.py programs/creation.aleph
  python aleph_eval.py --expr "aleph ⊗ mem"
  python aleph_eval.py --list
        """)


def list_programs() -> None:
    """List available .aleph programs."""
    programs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'programs')
    
    if not os.path.exists(programs_dir):
        if HAS_RICH:
            console.print("[yellow]No programs/ directory found[/yellow]")
        else:
            print("No programs/ directory found")
        return
    
    programs = [f for f in os.listdir(programs_dir) if f.endswith('.aleph')]
    programs.sort()
    
    if HAS_RICH:
        if not programs:
            console.print("[dim](no .aleph files found)[/dim]")
            return
        
        table = Table(title="Available ALEPH Programs", box=box.ROUNDED)
        table.add_column("#", style="dim", width=4)
        table.add_column("File", style="bold cyan")
        table.add_column("Path", style="green")
        
        for i, prog in enumerate(programs, 1):
            table.add_row(
                str(i),
                prog,
                os.path.join('programs', prog)
            )
        console.print(table)
        console.print(f"\n[dim]Run: python aleph_eval.py programs/<filename>[/dim]")
    else:
        print("Available ALEPH Programs:")
        print('─' * 40)
        for i, prog in enumerate(programs, 1):
            print(f"  {i:2d}. {prog}")
        print()
        print("Run: python aleph_eval.py programs/<filename>")


def resolve_aleph_file(name: str) -> Optional[str]:
    """Resolve an .aleph file name, searching common locations."""
    # If it's an explicit path
    if os.path.isfile(name):
        return name
    
    # Add .aleph extension if missing
    if not name.endswith('.aleph'):
        name_with_ext = name + '.aleph'
    else:
        name_with_ext = name
    
    # Search in current directory
    if os.path.isfile(name_with_ext):
        return os.path.abspath(name_with_ext)
    
    # Search in programs/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    programs_path = os.path.join(script_dir, 'programs', name_with_ext)
    if os.path.isfile(programs_path):
        return programs_path
    
    return None


# ──────────────────────────────────────────────────────────────────────────────
# 7. MAIN ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    
    # No args → REPL
    if not args:
        run_repl()
        return
    
    # --repl flag → REPL
    if args == ['--repl']:
        run_repl()
        return
    
    # --help or -h → Usage
    if args in (['--help'], ['-h']):
        print_usage()
        return
    
    # --list → List available programs
    if args == ['--list']:
        list_programs()
        return
    
    # --expr "..." → Evaluate inline expression
    if args[0] == '--expr':
        if len(args) < 2:
            if HAS_RICH:
                console.print("[bold red]Error:[/bold red] --expr requires an expression")
            else:
                print("[ERROR] --expr requires an expression")
            sys.exit(1)
        src = ' '.join(args[1:])
        try:
            result = _eval_src(src, {})
            print(format_ok(result))
        except Exception as e:
            print(format_error(src, e))
            sys.exit(1)
        return
    
    # Try to interpret as file or expression
    # First argument
    first_arg = args[0]
    
    # Check if it's a file
    if first_arg.endswith('.aleph') or os.path.isfile(first_arg):
        filepath = resolve_aleph_file(first_arg)
        if filepath:
            run_file(filepath)
            return
        else:
            if HAS_RICH:
                console.print(f"[bold red]Error:[/bold red] File not found: {first_arg}")
                console.print(f"\n[dim]Searched:[/dim]")
                console.print(f"  • {first_arg}")
                if not first_arg.startswith('/'):
                    console.print(f"  • programs/{first_arg}")
                console.print(f"\n[dim]Hint: Use --list to see available programs[/dim]")
            else:
                print(f"[ERROR] File not found: {first_arg}")
                print(f"\nSearched:")
                print(f"  • {first_arg}")
                if not first_arg.startswith('/'):
                    print(f"  • programs/{first_arg}")
                print(f"\nHint: Use --list to see available programs")
            sys.exit(1)
    
    # Treat remaining args as inline expression
    src = ' '.join(args)
    try:
        result = _eval_src(src, {})
        print(format_ok(result))
    except Exception as e:
        print(format_error(src, e))
        sys.exit(1)


if __name__ == '__main__':
    main()
