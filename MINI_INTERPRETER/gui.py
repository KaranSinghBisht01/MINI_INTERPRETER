"""
GUI for the Mini Interpreter — Premium Redesign
Modern dark theme with animated pipeline visualizer.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import tokenizer
import parser as parser_module
import ir_generator
import ir_executor
import time
import threading

# ══════════════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE
# ══════════════════════════════════════════════════════════════════════════════
BG          = "#0d0d14"      
SURFACE     = "#13131f"      
SURFACE2    = "#1a1a2e"      
BORDER      = "#2a2a45"      
MUTED       = "#3d3d5c"      

TEXT        = "#e8e8f0"      
TEXT_DIM    = "#7070a0"      
TEXT_BRIGHT = "#ffffff"      

ACCENT      = "#7c6af7"      
ACCENT2     = "#a78bfa"      
GREEN       = "#4ade80"      
ORANGE      = "#fb923c"      
CYAN        = "#22d3ee"      
PINK        = "#f472b6"      
YELLOW      = "#facc15"     


STAGE_COLORS = [CYAN, YELLOW, ORANGE, GREEN]
STAGE_NAMES  = ["Tokenizer", "Parser", "IR Generator", "Executor"]
STAGE_ICONS  = ["◈", "◉", "◎", "◆"]


SAMPLES = {
    "Arithmetic" : "3 + 5 * 2",
    "If-Else"    : "if 10 > 5 : 100 else 200",
    "Nested Math": "(3 + 4) * (2 - 1)",
    "Comparison" : "10 == 10",
    "Print"      : "print 3 + 4",
    "Negative"   : "-5 + 3",
}



def make_hover(widget, normal_bg, hover_bg, normal_fg=TEXT, hover_fg=TEXT_BRIGHT):
    widget.bind("<Enter>",  lambda e: widget.config(bg=hover_bg,  fg=hover_fg))
    widget.bind("<Leave>",  lambda e: widget.config(bg=normal_bg, fg=normal_fg))


def format_ast(node, indent=0):
    if node is None:
        return "None"
    if not isinstance(node, tuple):
        return str(node)
    pad  = "  " * indent
    nt   = node[0]
    if nt == "NUMBER":    return f"Num({node[1]})"
    if nt == "IDENTIFIER":return f"Var({node[1]})"
    if nt == "program":
        parts = [format_ast(s, indent + 1) for s in node[1]]
        return "Program(\n" + ",\n".join(f"{pad}  {p}" for p in parts) + f"\n{pad})"
    if nt == "if":
        return (f"If(\n{pad}  cond = {format_ast(node[1], indent+1)},\n"
                f"{pad}  then = {format_ast(node[2], indent+1)},\n"
                f"{pad}  else = {format_ast(node[3], indent+1)}\n{pad})")
    if nt == "assign": return f"Assign( {node[1]} ← {format_ast(node[2], indent+1)} )"
    if nt == "print":  return f"Print( {format_ast(node[1], indent+1)} )"
    if nt == "negate": return f"Neg( {format_ast(node[1], indent+1)} )"
    return (f"Op({nt},\n{pad}  L = {format_ast(node[1], indent+1)},\n"
            f"{pad}  R = {format_ast(node[2], indent+1)}\n{pad})")


root = tk.Tk()
root.title("Mini Interpreter  ·  Compiler Design")
root.geometry("1050x820")
root.minsize(800, 650)
root.configure(bg=BG)


FT = lambda s, w="normal": ("Segoe UI",   s, w)
FC = lambda s, w="normal": ("Consolas",   s, w)

header = tk.Frame(root, bg=SURFACE, pady=0)
header.pack(fill=tk.X)


stripe = tk.Canvas(header, height=3, bg=BG, highlightthickness=0)
stripe.pack(fill=tk.X)

def _draw_stripe(c):
    c.update_idletasks()
    w = c.winfo_width()
    steps = 60
    cols  = ["#7c6af7","#6d5ce7","#8b78fa","#a78bfa",
             "#c084fc","#e879f9","#f472b6","#fb7185",
             "#fb923c","#facc15","#4ade80","#22d3ee",
             "#38bdf8","#818cf8","#7c6af7"]
    seg = max(1, w // len(cols))
    for i, col in enumerate(cols):
        c.create_rectangle(i*seg, 0, (i+1)*seg+2, 3, fill=col, outline="")

stripe.bind("<Configure>", lambda e: _draw_stripe(stripe))

inner_head = tk.Frame(header, bg=SURFACE, padx=28, pady=18)
inner_head.pack(fill=tk.X)

tk.Label(inner_head, text="⬡  Mini Interpreter",
         font=("Segoe UI", 22, "bold"), fg=TEXT_BRIGHT, bg=SURFACE).pack(side=tk.LEFT)

tk.Label(inner_head,
         text="Tokenizer  →  Parser  →  IR Generator  →  Executor",
         font=FT(10), fg=TEXT_DIM, bg=SURFACE).pack(side=tk.LEFT, padx=16, pady=6)

version_lbl = tk.Label(inner_head, text="v2.0", font=FT(9),
                       fg=ACCENT2, bg=SURFACE)
version_lbl.pack(side=tk.RIGHT)


pipe_frame = tk.Frame(root, bg=BG, pady=10)
pipe_frame.pack(fill=tk.X, padx=24)

stage_labels  = []
stage_frames  = []
connector_cvs = []

def _add_connector(parent, color=BORDER):
    cv = tk.Canvas(parent, width=40, height=28, bg=BG, highlightthickness=0)
    cv.pack(side=tk.LEFT)
    cv.create_line(0, 14, 40, 14, fill=color, width=2, dash=(4,3))
    connector_cvs.append(cv)
    return cv

for i, (name, icon, color) in enumerate(zip(STAGE_NAMES, STAGE_ICONS, STAGE_COLORS)):
    if i > 0:
        _add_connector(pipe_frame)

    sf = tk.Frame(pipe_frame, bg=SURFACE2, padx=14, pady=8,
                  highlightbackground=BORDER, highlightthickness=1)
    sf.pack(side=tk.LEFT)

    tk.Label(sf, text=icon, font=FT(16), fg=MUTED, bg=SURFACE2).pack(side=tk.LEFT, padx=(0,6))
    lbl = tk.Label(sf, text=name, font=FT(10, "bold"), fg=TEXT_DIM, bg=SURFACE2)
    lbl.pack(side=tk.LEFT)

    stage_frames.append(sf)
    stage_labels.append(lbl)


def _set_stage(idx, active=True):
    """Light up / dim a pipeline stage."""
    col   = STAGE_COLORS[idx] if active else TEXT_DIM
    bg_col= SURFACE  if active else SURFACE2
    brd   = STAGE_COLORS[idx] if active else BORDER

    sf  = stage_frames[idx]
    lbl = stage_labels[idx]
    sf.config( bg=bg_col, highlightbackground=brd)
    lbl.config(bg=bg_col, fg=col)
    # also update the icon label (first child)
    for child in sf.winfo_children():
        child.config(bg=bg_col)
        if isinstance(child, tk.Label) and child != lbl:
            child.config(fg=col)


def _reset_stages():
    for i in range(4):
        _set_stage(i, False)



body = tk.Frame(root, bg=BG)
body.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 8))

body.columnconfigure(0, weight=2)
body.columnconfigure(1, weight=3)
body.rowconfigure(0, weight=1)

# ── LEFT COLUMN ──────────────────────────────────────────────────────────────
left = tk.Frame(body, bg=BG)
left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
left.rowconfigure(1, weight=1)
left.columnconfigure(0, weight=1)

# Sample buttons
sample_card = tk.Frame(left, bg=SURFACE2,
                       highlightbackground=BORDER, highlightthickness=1)
sample_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

tk.Label(sample_card, text="SAMPLES", font=FT(8, "bold"),
         fg=TEXT_DIM, bg=SURFACE2, padx=12, pady=8).pack(anchor=tk.W)

btn_row = tk.Frame(sample_card, bg=SURFACE2, padx=8)
btn_row.pack(fill=tk.X, pady=(0, 8))

for name in SAMPLES:
    b = tk.Button(btn_row, text=name, font=FT(9),
                  bg=SURFACE, fg=TEXT_DIM, activebackground=ACCENT,
                  activeforeground=TEXT_BRIGHT, relief=tk.FLAT,
                  padx=8, pady=4, cursor="hand2",
                  command=lambda n=name: _load_sample(n))
    b.pack(side=tk.LEFT, padx=3)
    make_hover(b, SURFACE, ACCENT, TEXT_DIM, TEXT_BRIGHT)

# Source code editor
editor_card = tk.Frame(left, bg=SURFACE,
                       highlightbackground=BORDER, highlightthickness=1)
editor_card.grid(row=1, column=0, sticky="nsew")
editor_card.rowconfigure(1, weight=1)
editor_card.columnconfigure(0, weight=1)

editor_hdr = tk.Frame(editor_card, bg=SURFACE, padx=12, pady=10)
editor_hdr.grid(row=0, column=0, sticky="ew")
tk.Label(editor_hdr, text="📝  SOURCE CODE", font=FT(9, "bold"),
         fg=ACCENT2, bg=SURFACE).pack(side=tk.LEFT)
tk.Label(editor_hdr, text="Mini-lang", font=FT(8),
         fg=TEXT_DIM, bg=SURFACE).pack(side=tk.RIGHT)

input_text = tk.Text(editor_card, font=FC(12), wrap=tk.WORD,
                     bg=SURFACE2, fg=TEXT, insertbackground=ACCENT2,
                     relief=tk.FLAT, padx=16, pady=12,
                     selectbackground=ACCENT, selectforeground=TEXT_BRIGHT,
                     undo=True, tabs="2c")
input_text.grid(row=1, column=0, sticky="nsew")

sb_in = tk.Scrollbar(editor_card, orient=tk.VERTICAL,
                     command=input_text.yview, bg=SURFACE)
sb_in.grid(row=1, column=1, sticky="ns")
input_text.config(yscrollcommand=sb_in.set)
input_text.insert(tk.END, "if 10 > 5 : 100 else 200")

# ── Action buttons ───────────────────────────────────────────────────────────
action_row = tk.Frame(left, bg=BG, pady=10)
action_row.grid(row=2, column=0, sticky="ew")

run_btn = tk.Button(action_row, text="▶  Run Code",
                    font=FT(11, "bold"), bg=ACCENT, fg=TEXT_BRIGHT,
                    activebackground=ACCENT2, activeforeground=TEXT_BRIGHT,
                    relief=tk.FLAT, padx=22, pady=9, cursor="hand2",
                    command=lambda: _run_threaded())
run_btn.pack(side=tk.LEFT, padx=(0, 8))
make_hover(run_btn, ACCENT, ACCENT2)

clr_btn = tk.Button(action_row, text="✕  Clear",
                    font=FT(11, "bold"), bg=SURFACE2, fg=TEXT_DIM,
                    activebackground=MUTED, activeforeground=TEXT_BRIGHT,
                    relief=tk.FLAT, padx=18, pady=9, cursor="hand2",
                    command=lambda: _clear())
clr_btn.pack(side=tk.LEFT)
make_hover(clr_btn, SURFACE2, MUTED, TEXT_DIM, TEXT_BRIGHT)

# ── RIGHT COLUMN ─────────────────────────────────────────────────────────────
right = tk.Frame(body, bg=BG)
right.grid(row=0, column=1, sticky="nsew")
right.rowconfigure(0, weight=1)
right.columnconfigure(0, weight=1)

out_card = tk.Frame(right, bg=SURFACE,
                    highlightbackground=BORDER, highlightthickness=1)
out_card.grid(row=0, column=0, sticky="nsew")
out_card.rowconfigure(1, weight=1)
out_card.columnconfigure(0, weight=1)

out_hdr = tk.Frame(out_card, bg=SURFACE, padx=12, pady=10)
out_hdr.grid(row=0, column=0, sticky="ew")
tk.Label(out_hdr, text="📊  INTERPRETER OUTPUT", font=FT(9, "bold"),
         fg=ACCENT2, bg=SURFACE).pack(side=tk.LEFT)

output_box = tk.Text(out_card, font=FC(11), wrap=tk.WORD,
                     bg="#0a0a12", fg=TEXT,
                     relief=tk.FLAT, padx=16, pady=12,
                     state=tk.DISABLED,
                     selectbackground=ACCENT,
                     selectforeground=TEXT_BRIGHT)
output_box.grid(row=1, column=0, sticky="nsew")

sb_out = tk.Scrollbar(out_card, orient=tk.VERTICAL,
                      command=output_box.yview, bg=SURFACE)
sb_out.grid(row=1, column=1, sticky="ns")
output_box.config(yscrollcommand=sb_out.set)

# tag styles
output_box.tag_config("stage",    foreground=ACCENT,  font=FT(10, "bold"))
output_box.tag_config("divider",  foreground=MUTED)
output_box.tag_config("token_t",  foreground=CYAN,    font=FC(10, "bold"))
output_box.tag_config("token_v",  foreground=TEXT)
output_box.tag_config("ast",      foreground=YELLOW)
output_box.tag_config("ir_idx",   foreground=MUTED,   font=FC(10))
output_box.tag_config("ir_op",    foreground=ORANGE,  font=FC(10, "bold"))
output_box.tag_config("result",   foreground=GREEN,   font=FC(11, "bold"))
output_box.tag_config("err_hdr",  foreground=PINK,    font=FT(10, "bold"))
output_box.tag_config("err_msg",  foreground=PINK)
output_box.tag_config("dim",      foreground=TEXT_DIM)
output_box.tag_config("success_bg",foreground=GREEN,  font=FT(10, "bold"))

# ══════════════════════════════════════════════════════════════════════════════
#  STATUS BAR
# ══════════════════════════════════════════════════════════════════════════════
status_bar = tk.Frame(root, bg=SURFACE, pady=5,
                      highlightbackground=BORDER, highlightthickness=1)
status_bar.pack(fill=tk.X, side=tk.BOTTOM)

status_lbl = tk.Label(status_bar, text="  ●  Ready",
                      font=FT(9), fg=GREEN, bg=SURFACE, anchor=tk.W)
status_lbl.pack(side=tk.LEFT, padx=10)

tk.Label(status_bar, text="Mini Interpreter v2.0  ·  Compiler Design Project",
         font=FT(9), fg=TEXT_DIM, bg=SURFACE).pack(side=tk.RIGHT, padx=10)


def _set_status(msg, color=GREEN):
    status_lbl.config(text=f"  ●  {msg}", fg=color)

# ══════════════════════════════════════════════════════════════════════════════
#  OUTPUT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _out(*args):
    """Append text with optional tag."""
    output_box.config(state=tk.NORMAL)
    if len(args) == 1:
        output_box.insert(tk.END, args[0])
    else:
        output_box.insert(tk.END, args[0], args[1])
    output_box.config(state=tk.DISABLED)


def _out_clear():
    output_box.config(state=tk.NORMAL)
    output_box.delete("1.0", tk.END)
    output_box.config(state=tk.DISABLED)


def _section(title, tag="stage", icon=""):
    _out(f"\n{icon}  {title}\n", tag)
    _out("─" * 58 + "\n", "divider")

# ══════════════════════════════════════════════════════════════════════════════
#  CORE LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def _load_sample(name):
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, SAMPLES[name])
    _set_status(f"Sample loaded: {name}", ACCENT2)


def _clear():
    input_text.delete("1.0", tk.END)
    _out_clear()
    _reset_stages()
    _set_status("Cleared", TEXT_DIM)


def _animate_stage(idx):
    """Flash a stage on (runs on main thread)."""
    for j in range(4):
        _set_stage(j, j == idx)
    root.update_idletasks()


def _run_threaded():
    run_btn.config(state=tk.DISABLED, text="⏳  Running…")
    _set_status("Running…", YELLOW)
    t = threading.Thread(target=_run_pipeline, daemon=True)
    t.start()


def _run_pipeline():
    code = input_text.get("1.0", tk.END).strip()
    _out_clear()
    _reset_stages()

    if not code:
        root.after(0, lambda: messagebox.showwarning(
            "No Input", "Please enter some code to run."))
        root.after(0, _restore_btn)
        return

    try:
        # ── Stage 1: Tokenize ────────────────────────────────────────────────
        root.after(0, lambda: _animate_stage(0))
        root.after(0, lambda: _set_status("Tokenizing…", CYAN))
        time.sleep(0.18)

        tokens = tokenizer.tokenize(code)

        def _show_tokens():
            _section("TOKENS", "stage", "◈")
            col_w = max((len(str(t[0])) for t in tokens), default=8) + 2
            for tok in tokens:
                _out(f"  {str(tok[0]):<{col_w}}", "token_t")
                _out(f"│  {tok[1]}\n", "token_v")
            _out("\n")
        root.after(0, _show_tokens)
        time.sleep(0.18)

        # ── Stage 2: Parse ───────────────────────────────────────────────────
        root.after(0, lambda: _animate_stage(1))
        root.after(0, lambda: _set_status("Parsing…", YELLOW))
        time.sleep(0.18)

        ast = parser_module.parse(tokens)

        def _show_ast():
            _section("ABSTRACT SYNTAX TREE", "stage", "◉")
            _out(f"  {format_ast(ast)}\n\n", "ast")
        root.after(0, _show_ast)
        time.sleep(0.18)

        # ── Stage 3: IR Generation ───────────────────────────────────────────
        root.after(0, lambda: _animate_stage(2))
        root.after(0, lambda: _set_status("Generating IR…", ORANGE))
        time.sleep(0.18)

        ir_code = ir_generator.generate_ir(ast)

        def _show_ir():
            _section("INTERMEDIATE REPRESENTATION (IR)", "stage", "◎")
            for i, instr in enumerate(ir_code):
                parts = instr.split(None, 1)
                _out(f"  {i:02d}  ", "ir_idx")
                _out(f"{parts[0]:<12}", "ir_op")
                if len(parts) > 1:
                    _out(f"{parts[1]}\n", "token_v")
                else:
                    _out("\n")
            _out("\n")
        root.after(0, _show_ir)
        time.sleep(0.18)

        # ── Stage 4: Execute ─────────────────────────────────────────────────
        root.after(0, lambda: _animate_stage(3))
        root.after(0, lambda: _set_status("Executing…", GREEN))
        time.sleep(0.18)

        result = ir_executor.execute_ir(ir_code)

        def _show_result():
            _section("OUTPUT", "stage", "◆")
            if result.get("output"):
                _out(f"  Printed   ", "dim")
                _out(f"{result['output']}\n", "result")
            if result.get("result") is not None:
                _out(f"  Result    ", "dim")
                _out(f"{result['result']}\n", "result")
            if result.get("variables"):
                _out(f"  Variables ", "dim")
                _out(f"{result['variables']}\n", "result")
            _out("\n")
            _out("  ✔  Execution complete\n", "success_bg")
            _set_status("Done — execution complete ✔", GREEN)
        root.after(0, _show_result)

    except SyntaxError as e:
        _show_error(f"Syntax Error", str(e))
    except NameError as e:
        _show_error("Name Error", str(e))
    except ZeroDivisionError as e:
        _show_error("Division by Zero", str(e))
    except Exception as e:
        _show_error("Unexpected Error", str(e))

    root.after(0, _restore_btn)


def _show_error(kind, msg):
    def _inner():
        _out(f"\n  ✕  {kind}\n", "err_hdr")
        _out("─" * 58 + "\n", "divider")
        _out(f"  {msg}\n", "err_msg")
        _set_status(f"{kind}: {msg}", PINK)
    root.after(0, _inner)


def _restore_btn():
    run_btn.config(state=tk.NORMAL, text="▶  Run Code")

# ══════════════════════════════════════════════════════════════════════════════
#  KEYBOARD SHORTCUT  Ctrl+Enter → Run
# ══════════════════════════════════════════════════════════════════════════════
root.bind_all("<Control-Return>", lambda e: _run_threaded())

# ══════════════════════════════════════════════════════════════════════════════
#  WELCOME MESSAGE
# ══════════════════════════════════════════════════════════════════════════════
def _welcome():
    _out("  Welcome to Mini Interpreter v2.0\n", "stage")
    _out("─" * 58 + "\n", "divider")
    _out("  Write any expression in the editor and click\n", "dim")
    _out("  ▶ Run Code  or press  Ctrl+Enter\n\n", "dim")
    _out("  Supported syntax:\n", "dim")
    samples_info = [
        ("Arithmetic :", "3 + 5 * 2"),
        ("Comparison :", "10 > 5"),
        ("If-Else    :", "if 10 > 5 : 100 else 200"),
        ("Assignment :", "x = 42"),
        ("Print      :", "print 3 + 4"),
        ("Negative   :", "-5 + 3"),
    ]
    for label, example in samples_info:
        _out(f"  {label}  ", "dim")
        _out(f"{example}\n", "ast")
    _out("\n")

_welcome()

root.mainloop()