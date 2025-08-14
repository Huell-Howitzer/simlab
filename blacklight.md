Awesome project. You can make GDB feel “yours” by packaging a tiny toolkit of Python commands, printers, and helpers that you import inside GDB. Below is a minimal-but-powerful starter package you can grow over time.

What you’ll get
	•	A normal Python package you can keep in a repo (pip‑installable if you want).
	•	An install() function that registers your commands, pretty‑printers, and frame filters with one line in GDB.
	•	A few useful sample commands:
	•	pp-expr <expr> — evaluate and pretty‑print a C/C++ expression from GDB.
	•	ret — run until the current function returns, then print the return value (works for typical C++ ABIs).
	•	bk-here [cond] — make a breakpoint at the current line (optionally conditional).
	•	bk-on-throw [Type] — stop when a C++ exception is thrown (optionally filter by type substring).
	•	dump-locals [path] — dump local variables to JSON.
	•	An example pretty‑printer and a frame filter skeleton you can extend.

⸻

Package layout

gdb_tools/
  __init__.py
  commands.py
  printers.py
  frames.py
  util.py
pyproject.toml
README.md


⸻

pyproject.toml (optional, handy for pip install -e .)

[project]
name = "gdb-tools"
version = "0.1.0"
description = "Personal GDB extensions (commands, printers, frame filters)"
authors = [{ name = "You" }]
requires-python = ">=3.8"
dependencies = []

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

Tip: GDB embeds its own Python. To avoid version mismatch headaches, keep this package pure‑Python with no external deps, or vendor tiny utilities inside the package.

⸻

gdb_tools/init.py

# gdb_tools/__init__.py
from .commands import register_commands
from .printers import register_printers
from .frames import register_frame_filters

def install():
    """Call this from inside GDB to register everything."""
    register_commands()
    register_printers()
    register_frame_filters()


⸻

gdb_tools/util.py

# gdb_tools/util.py
import gdb
import json

def print_info(msg: str):
    gdb.write(f"[gdb-tools] {msg}\n", gdb.STDLOG)

def print_err(msg: str):
    gdb.write(f"[gdb-tools ERROR] {msg}\n", gdb.STDERR)

def eval_expr(expr: str):
    """Parse & evaluate a C/C++ expression in the current context."""
    return gdb.parse_and_eval(expr)

def dump_to_json(path: str, obj) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def frame_locals_to_dict(frame=None):
    if frame is None:
        frame = gdb.selected_frame()
    syms = frame.block()
    out = {}
    while syms:
        for sym in syms:
            if not sym.is_argument and not sym.is_variable:
                continue
            try:
                val = sym.value(frame)
                out[sym.print_name] = str(val)
            except Exception:
                out[sym.print_name] = "<unavailable>"
        syms = syms.superblock
    return out


⸻

gdb_tools/commands.py

# gdb_tools/commands.py
import gdb
from .util import print_info, print_err, eval_expr, dump_to_json, frame_locals_to_dict

class PpExpr(gdb.Command):
    """pp-expr <expr>
Pretty-print a C/C++ expression using GDB's printer stack."""
    def __init__(self):
        super().__init__("pp-expr", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        arg = arg.strip()
        if not arg:
            print_err("Usage: pp-expr <expr>")
            return
        try:
            val = eval_expr(arg)
            gdb.write(val.format_string() + "\n")
        except Exception as e:
            print_err(f"Failed: {e}")

class RetPrint(gdb.Command):
    """ret
Continue until the current function returns, then print the return value."""
    def __init__(self):
        super().__init__("ret", gdb.COMMAND_RUNNING)

    def invoke(self, arg, from_tty):
        # Set a finish breakpoint and hook its stop to print the value.
        fb = gdb.FinishBreakpoint(gdb.newest_frame(), internal=True)
        fb.silent = True
        def on_finish(bp):
            try:
                if hasattr(bp, "return_value") and bp.return_value is not None:
                    gdb.write(f"Return value: {bp.return_value}\n")
                else:
                    gdb.write("Function returned (no value or unavailable)\n")
            finally:
                bp.delete()
            return False  # resume normal stop handling
        fb.stop = on_finish
        gdb.execute("continue")

class BkHere(gdb.Command):
    """bk-here [cond]
Set a breakpoint at the current line; optionally add a condition."""
    def __init__(self):
        super().__init__("bk-here", gdb.COMMAND_BREAKPOINTS)

    def invoke(self, arg, from_tty):
        frame = gdb.selected_frame()
        sal = frame.find_sal()
        spec = f"{sal.symtab.filename}:{sal.line}"
        bp = gdb.Breakpoint(spec)
        cond = arg.strip()
        if cond:
            bp.condition = cond
            gdb.write(f"Breakpoint {bp.number} at {spec} if ({cond})\n")
        else:
            gdb.write(f"Breakpoint {bp.number} at {spec}\n")

class BkOnThrow(gdb.Command):
    """bk-on-throw [TypeSubstr]
Break when a C++ exception is thrown (optionally filter by type substring)."""
    def __init__(self):
        super().__init__("bk-on-throw", gdb.COMMAND_BREAKPOINTS)

    def invoke(self, arg, from_tty):
        # This uses 'catch throw' under the hood, then optionally filters in stop().
        bp = gdb.Breakpoint("throw", type=gdb.BP_CATCHPOINT)
        needle = arg.strip()
        if needle:
            def stop(bp_):
                try:
                    etype = gdb.parse_and_eval("$_exception")
                    if needle in str(etype):
                        return True
                    return False
                except Exception:
                    # If we can't examine the exception, stop anyway.
                    return True
            bp.stop = stop
            gdb.write(f"Catchpoint {bp.number} on throw (filter: '{needle}')\n")
        else:
            gdb.write(f"Catchpoint {bp.number} on throw (no filter)\n")

class DumpLocals(gdb.Command):
    """dump-locals [path]
Dump locals of the selected frame to JSON (default: /tmp/gdb_locals.json)."""
    def __init__(self):
        super().__init__("dump-locals", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        path = arg.strip() or "/tmp/gdb_locals.json"
        try:
            d = frame_locals_to_dict()
            dump_to_json(path, d)
            print_info(f"Wrote {path}")
        except Exception as e:
            print_err(f"Failed: {e}")

def register_commands():
    PpExpr()
    RetPrint()
    BkHere()
    BkOnThrow()
    DumpLocals()


⸻

gdb_tools/printers.py

# gdb_tools/printers.py
import gdb
from .util import print_info

# Example pretty-printer for a trivial user-defined type:
# struct Vec2 { float x; float y; };
class Vec2Printer:
    def __init__(self, val):
        self.val = val
    def to_string(self):
        try:
            x = float(self.val["x"])
            y = float(self.val["y"])
            return f"Vec2(x={x}, y={y})"
        except Exception:
            return "Vec2(?)"

class PrinterCollection:
    def __init__(self):
        self.matchers = []
    def add(self, predicate, factory):
        self.matchers.append((predicate, factory))
    def __call__(self, val):
        t = val.type.strip_typedefs()
        for pred, fac in self.matchers:
            if pred(t):
                return fac(val)
        return None

printers = PrinterCollection()

def _is_vec2(t):
    # Adjust this to your namespace/name as needed
    return t.code == gdb.TYPE_CODE_STRUCT and t.tag and t.tag.endswith("Vec2")

printers.add(_is_vec2, Vec2Printer)

def register_printers():
    obj = gdb.current_objfile() or gdb
    gdb.printing.register_pretty_printer(obj, printers, replace=True)
    print_info("pretty-printers registered")


⸻

gdb_tools/frames.py

# gdb_tools/frames.py
import gdb
from .util import print_info

# Frame filters let you redact or group noisy frames (e.g., STL, coroutine shims)
class SimpleFrameFilter:
    def __init__(self):
        self.name = "gdb-tools-filter"
        self.priority = 100
        self.enabled = True

    def filter(self, it):
        for f in it:
            # Example: hide frames with names like "__gnu_cxx::" (tweak as you like)
            try:
                name = f.function() or ""
                if "__gnu_cxx::" in name:
                    continue
            except Exception:
                pass
            yield f

def register_frame_filters():
    gff = gdb.frame_filters
    gff["gdb-tools"] = SimpleFrameFilter()
    print_info("frame filter registered")


⸻

How to use it in GDB

Option A: Quick import (dev mode)
	1.	Put the repo somewhere (e.g., ~/src/gdb-tools).
	2.	Add this to ~/.gdbinit so GDB can import it:

python
import sys
sys.path.insert(0, "/home/you/src")  # parent directory that contains gdb_tools/
import gdb_tools
gdb_tools.install()
end


	3.	Launch GDB. You’ll see [gdb-tools] pretty-printers registered etc.
	4.	Use your commands:

(gdb) pp-expr my_vec
(gdb) bk-here i == 3
(gdb) ret
(gdb) dump-locals /tmp/locals.json



Option B: Pip install (editable)

pip install -e .

Then in ~/.gdbinit:

python
import gdb_tools
gdb_tools.install()
end

Option C: Per‑binary auto‑load

Place a file named your_program-gdb.py next to the executable:

# your_program-gdb.py
import sys
sys.path.insert(0, "/home/you/src")  # ensure importable
import gdb_tools
gdb_tools.install()

If GDB blocks auto-load, add a safe path in ~/.gdbinit:

add-auto-load-safe-path /home/you/src


⸻

Extending the toolkit
	•	Add more commands: create another gdb.Command subclass in commands.py, then register it in register_commands().
	•	Targeted pretty‑printers: in printers.py, add more printers.add(predicate, factory) lines for your types (e.g., std::optional<T> wrappers, handle-like IDs, etc.).
	•	Quality-of-life helpers: add gdb.events hooks (e.g., print thread when a new thread starts), set default breakpoints on startup, etc.
	•	Project/local overrides: you can make gdb_tools/site.py read an environment variable (e.g., GDB_TOOLS_RC) to load project-specific settings without forking the package.

⸻

A couple of handy patterns you might want next

1) One‑shot conditional breakpoint with action

class When(gdb.Command):
    """when <cond> --action '<gdb cmd>'
Break when <cond> first becomes true; then run action and resume."""
    def __init__(self):
        super().__init__("when", gdb.COMMAND_BREAKPOINTS)
    def invoke(self, arg, from_tty):
        try:
            cond, action = arg.split("--action", 1)
            cond = cond.strip()
            action = action.strip().strip("'").strip('"')
        except ValueError:
            gdb.write("Usage: when <cond> --action '<gdb cmd>'\n")
            return
        bp = gdb.Breakpoint("*$pc", internal=True, temporary=True)
        def stop(bp_):
            try:
                ok = bool(gdb.parse_and_eval(cond))
            except Exception:
                ok = False
            if ok:
                if action:
                    gdb.execute(action)
                return True   # stop here
            return False      # keep running
        bp.stop = stop
        gdb.execute("continue")

2) Inspect memory as typed array

class Peek(gdb.Command):
    """peek <type> <addr> <count>"""
    def __init__(self):
        super().__init__("peek", gdb.COMMAND_DATA)
    def invoke(self, arg, from_tty):
        ty_s, addr_s, cnt_s = arg.split()
        ty = gdb.lookup_type(ty_s)
        addr = int(gdb.parse_and_eval(addr_s))
        cnt = int(cnt_s)
        inferior = gdb.selected_inferior()
        size = int(ty.sizeof)
        data = inferior.read_memory(addr, size * cnt).tobytes()
        for i in range(cnt):
            chunk = data[i*size:(i+1)*size]
            val = gdb.Value(chunk).cast(ty.pointer()).dereference()
            gdb.write(f"[{i}] {val}\n")

(You’d register them the same way in register_commands().)

⸻

Notes on C++ return values (ret)
	•	FinishBreakpoint.return_value is supported on “normal” returns. It may be unavailable (e.g., optimized out, tail‑calls, void functions, or architecture quirks). The command handles that case and still tells you the function returned.

⸻

Next steps (pick any):
	•	Tell me the C++ types you debug most (STL containers, your own math structs, etc.), and I’ll add targeted pretty‑printers.
	•	Want a TUI side panel with live locals/threads? We can make a tiny curses‑free display using gdb.events + gdb.execute("dashboard ...") style printing.
	•	If you use LLDB sometimes, I can mirror these commands for LLDB with its Python API.

If you drop this into a repo and add the ~/.gdbinit snippet, you’ll have a solid, extendable foundation—no more retyping incantations every session.