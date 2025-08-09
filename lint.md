Got it — you want a linter for your (custom) language, with just-enough parsing to support rules. Here’s a compact blueprint plus runnable snippets using Lark so you don’t spend weeks on a full parser.

Plan
	1.	Define a tolerant grammar (parse just enough to locate constructs you’ll lint).
	2.	Build a CST/AST with positions (line/column) for good diagnostics.
	3.	Write rules as visitors that walk the tree and emit findings.
	4.	Add config + ignores (severity, per‑rule enable/disable, // lint-disable).
	5.	Drive with tests (golden tests + unit tests per rule).

⸻

1) Minimal grammar (Lark)

Example for a tiny lang with let statements and expressions (+ - * /, parens). Adjust to your language.

# grammar.lark
?start: stmt*
stmt: "let" NAME "=" expr ";"      -> let_stmt
    | expr ";"                     -> expr_stmt

?expr: term
     | expr "+" term               -> add
     | expr "-" term               -> sub
?term: factor
     | term "*" factor             -> mul
     | term "/" factor             -> div
?factor: NUMBER                    -> number
       | NAME                      -> var
       | "(" expr ")"

%import common.CNAME -> NAME
%import common.INT -> NUMBER
%import common.WS_INLINE
%import common.NEWLINE
%ignore WS_INLINE
%ignore NEWLINE
%ignore /\/\/[^\n]*/               // line comments

Tolerant tricks:
	•	If your language has more constructs, start by recognizing them (even if you ignore inside) so the parser doesn’t choke.
	•	You can extend rules later without rewriting lint rules.

⸻

2) Parser + AST with positions

# parser.py
from dataclasses import dataclass
from typing import List, Union
from lark import Lark, Transformer, Token, Tree
from pathlib import Path

grammar = Path("grammar.lark").read_text()
_parser = Lark(grammar, parser="lalr", propagate_positions=True)

# AST
@dataclass
class Program: statements: List["Stmt"]
class Stmt: ...
@dataclass
class Let(Stmt): name: str; value: "Expr"; line: int; col: int
@dataclass
class ExprStmt(Stmt): expr: "Expr"; line: int; col: int

class Expr: ...
@dataclass
class Number(Expr): value: int; line: int; col: int
@dataclass
class Var(Expr): name: str; line: int; col: int
@dataclass
class BinOp(Expr): op: str; left: Expr; right: Expr; line: int; col: int

class ToAST(Transformer):
    def let_stmt(self, items):
        name, expr = items
        t: Token = name.meta if hasattr(name, "meta") else None
        return Let(name.value, expr, expr.line, expr.col)
    def expr_stmt(self, items):
        e = items[0]; return ExprStmt(e, e.line, e.col)

    def number(self, items):
        tok: Token = items[0]
        return Number(int(tok.value), tok.line, tok.column)
    def var(self, items):
        tok: Token = items[0]
        return Var(tok.value, tok.line, tok.column)

    def add(self, items):  return self._bin("+", items)
    def sub(self, items):  return self._bin("-", items)
    def mul(self, items):  return self._bin("*", items)
    def div(self, items):  return self._bin("/", items)
    def _bin(self, op, items):
        a, b = items
        return BinOp(op, a, b, a.line, a.col)

def parse(src: str) -> Program:
    tree: Tree = _parser.parse(src)
    ast = ToAST().transform(tree)
    return Program(ast if isinstance(ast, list) else [ast])

propagate_positions=True gives you line/column for tokens, perfect for lint messages.

⸻

3) Linter core + rule API

# linter.py
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Set, TypeVar, Union
from parser import Program, Let, ExprStmt, Number, Var, BinOp, Expr

@dataclass
class Finding:
    rule: str
    line: int
    col: int
    message: str
    fix: Optional[str] = None

RuleFn = Callable[[Program], Iterable[Finding]]
_RULES: Dict[str, RuleFn] = {}

def rule(name: str):
    def deco(fn: RuleFn):
        _RULES[name] = fn
        return fn
    return deco

def lint(program: Program, enabled: Optional[Set[str]] = None) -> List[Finding]:
    enabled = enabled or set(_RULES.keys())
    out: List[Finding] = []
    for name in enabled:
        out.extend(_RULES[name](program))
    # stable order: by line,col, then rule
    return sorted(out, key=lambda f: (f.line, f.col, f.rule))

Example rules
	1.	No unused let (simple, local scope).
	2.	No shadowing (name declared twice).
	3.	Discourage magic numbers (except 0/1).

# rules.py
from typing import Set
from linter import rule, Finding
from parser import Program, Let, ExprStmt, Var, Number, BinOp, Expr

def _walk_expr(e: Expr):
    if isinstance(e, BinOp):
        yield from _walk_expr(e.left); yield from _walk_expr(e.right)
    else:
        yield e

@rule("no-unused-let")
def no_unused_let(prog: Program):
    declared: Set[str] = set()
    used: Set[str] = set()
    for s in prog.statements:
        if isinstance(s, Let):
            declared.add(s.name)
            for n in _walk_expr(s.value):
                if isinstance(n, Var): used.add(n.name)
        elif isinstance(s, ExprStmt):
            for n in _walk_expr(s.expr):
                if isinstance(n, Var): used.add(n.name)
    for name in sorted(declared - used):
        # find the line/col from first declaration
        for s in prog.statements:
            if isinstance(s, Let) and s.name == name:
                yield Finding("no-unused-let", s.line, s.col, f"Variable '{name}' is never used")

@rule("no-shadowing")
def no_shadowing(prog: Program):
    seen: Set[str] = set()
    for s in prog.statements:
        if isinstance(s, Let):
            if s.name in seen:
                yield Finding("no-shadowing", s.line, s.col, f"Variable '{s.name}' shadows a previous declaration")
            seen.add(s.name)

@rule("no-magic-numbers")
def no_magic_numbers(prog: Program):
    allowed = {0, 1}
    for s in prog.statements:
        nodes = []
        if isinstance(s, Let): nodes.append(s.value)
        elif isinstance(s, ExprStmt): nodes.append(s.expr)
        for e in nodes:
            for n in _walk_expr(e):
                if isinstance(n, Number) and n.value not in allowed:
                    yield Finding("no-magic-numbers", n.line, n.col, f"Magic number {n.value}; consider a named constant")


⸻

4) CLI wrapper

# cli.py
import sys, json
from parser import parse
from linter import lint
from rules import *  # registers rules

def main():
    src = sys.stdin.read()
    prog = parse(src)
    findings = lint(prog)
    for f in findings:
        print(f"{f.line}:{f.col} {f.rule}: {f.message}")
    # or: print(json.dumps([f.__dict__ for f in findings], indent=2))

if __name__ == "__main__":
    main()

Use:

python cli.py < sample.src


⸻

5) Tests (pytest)

Drive everything with tests first.

# tests/test_lint_basic.py
import pytest
from parser import parse
from linter import lint
from rules import *  # register

def issues(src):
    return [(f.rule, f.message) for f in lint(parse(src))]

def test_no_issues():
    assert issues("let x = 1; x + 1;") == []

def test_unused_let():
    out = issues("let a = 2 + 3;")
    assert ("no-unused-let", "Variable 'a' is never used") in out

def test_shadowing():
    out = issues("let a = 1; let a = 2;")
    assert any(r == "no-shadowing" for r, _ in out)

def test_magic_numbers():
    out = issues("let x = 42;")
    assert any(r == "no-magic-numbers" for r, _ in out)

Golden tests are also nice: keep a cases/ folder with inputs and expected outputs (text files). Your test runs the linter and compares output.

⸻

6) Ignoring and config (quick pattern)
	•	Support // lint-disable no-magic-numbers comments: record disabled ranges in lexing or do a quick text pass mapping lines → disabled rules.
	•	Config file (YAML/JSON): which rules are enabled and severities. Pass that into lint(program, enabled=...).

Example ignore pass:

def parse_ignores(src: str):
    # returns dict[line_number] -> set(rule_names)
    ignores = {}
    for i, line in enumerate(src.splitlines(), start=1):
        if "//" in line and "lint-disable" in line:
            after = line.split("lint-disable",1)[1]
            rules = [r.strip() for r in after.split() if r.strip()]
            ignores[i] = set(rules or ["*"])
    return ignores

# then filter findings whose (line) is ignored for that rule or "*"


⸻

7) Growing the linter
	•	Add more grammar productions only when a rule needs them.
	•	Keep rules pure and side‑effect free; they just return Findings.
	•	Add autofix by attaching fix suggestions (e.g., “extract constant”), and a separate apply‑fixes step if you want formatting.

⸻

If you share a slice of your language (keywords, statements, tricky bits), I’ll tailor the grammar and write the first 2–3 rules specifically for it, plus pytest cases you can run immediately.