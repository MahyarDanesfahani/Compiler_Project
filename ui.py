"""Small Tkinter UI for demonstrating Phase 1 manual lexical analysis."""

from __future__ import annotations

import csv
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from scanner import TableDrivenScanner


BASE = Path(__file__).parent


class LexerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NovaScript+ | Phase 1 Manual Lexer")
        self.geometry("1100x700")
        self.minsize(850, 550)
        self._build()
        self._load_sample(BASE / "samples" / "valid.ns")

    def _build(self):
        toolbar = ttk.Frame(self, padding=8)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Open source", command=self._open).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Scan", command=self._scan).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Show DFA table", command=self._show_table).pack(side="left", padx=4)
        self.file_label = ttk.Label(toolbar, text="No file selected")
        self.file_label.pack(side="left", padx=14)

        panes = ttk.PanedWindow(self, orient="vertical")
        panes.pack(fill="both", expand=True, padx=8, pady=4)
        source_frame = ttk.LabelFrame(panes, text="Source program")
        result_frame = ttk.Frame(panes)
        panes.add(source_frame, weight=1)
        panes.add(result_frame, weight=2)

        self.source = tk.Text(source_frame, wrap="none", font=("Consolas", 11), undo=True)
        self.source.pack(fill="both", expand=True, padx=5, pady=5)

        notebook = ttk.Notebook(result_frame)
        notebook.pack(fill="both", expand=True)
        token_tab = ttk.Frame(notebook)
        error_tab = ttk.Frame(notebook)
        table_tab = ttk.Frame(notebook)
        nfa_tab = ttk.Frame(notebook)
        notebook.add(token_tab, text="Tokens")
        notebook.add(error_tab, text="Errors")
        notebook.add(table_tab, text="DFA transition table")
        notebook.add(nfa_tab, text="NFA diagram")

        self.tokens = tk.Text(token_tab, wrap="none", font=("Consolas", 10), state="disabled")
        self.tokens.pack(fill="both", expand=True)
        self.errors = tk.Text(error_tab, wrap="word", font=("Consolas", 10), state="disabled")
        self.errors.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_tab, show="headings")
        self.table.pack(fill="both", expand=True)
        self.nfa = tk.Text(nfa_tab, wrap="word", font=("Consolas", 11), state="disabled")
        self.nfa.pack(fill="both", expand=True, padx=8, pady=8)
        self._show_nfa()
        self._show_table()

    def _load_sample(self, path: Path):
        self.source.delete("1.0", "end")
        self.source.insert("1.0", path.read_text(encoding="utf-8"))
        self.file_label.configure(text=str(path.name))
        self._scan()

    def _open(self):
        path = filedialog.askopenfilename(
            title="Open NovaScript+ source", filetypes=[("NovaScript+", "*.ns"), ("All files", "*.*")]
        )
        if path:
            self._load_sample(Path(path))

    def _scan(self):
        scanner = TableDrivenScanner(BASE / "transition_table.csv")
        tokens, errors = scanner.scan(self.source.get("1.0", "end-1c"))
        token_lines = [f"{t.kind:<14} {t.lexeme!r:<14} line={t.line:<3} column={t.column}" for t in tokens]
        error_lines = errors or ["No lexical errors."]
        self._replace(self.tokens, "\n".join(token_lines))
        self._replace(self.errors, "\n".join(error_lines))

    def _show_table(self):
        with (BASE / "transition_table.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        self.table.delete(*self.table.get_children())
        self.table["columns"] = rows[0]
        for heading in rows[0]:
            self.table.heading(heading, text=heading)
            self.table.column(heading, width=100, anchor="center")
        for row in rows[1:]:
            self.table.insert("", "end", values=row)

    def _show_nfa(self):
        text = """NFA diagrams used in Phase 1

Identifier:
  I0 --letter or _--> I1 (final)
  I1 --letter, digit, or _--> I1

Integer:
  N0 --digit--> N1 (final)
  N1 --digit--> N1

Single-character tokens:
  S --+--> PLUS (final)
  S --=--> EQUAL (final)
  S --(--> LPAREN (final)
  S --)--> RPAREN (final)

The complete Graphviz source is stored in nfa_dfa.dot.
The DFA transition table is shown in the adjacent tab.
"""
        self._replace(self.nfa, text)

    @staticmethod
    def _replace(widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")


if __name__ == "__main__":
    try:
        LexerUI().mainloop()
    except tk.TclError as error:
        messagebox.showerror("UI error", str(error))
