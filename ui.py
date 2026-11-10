"""The window for phase 1 (dark theme).

It only calls Scanner.scan() and shows the result. The scanning itself is not in this file.
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from scanner import Scanner

BASE = Path(__file__).parent

# ---- colors and fonts ----
# background colors
BG, PANEL, EDITOR, BORDER = "#0e1117", "#161b22", "#0b0f14", "#2a3140"
# text and other colors
FG, MUTED, ACCENT, GOOD, BAD = "#e6edf3", "#8b949e", "#58a6ff", "#3fb950", "#ff7b72"
UI_FONT, CODE_FONT = ("Segoe UI", 10), ("Consolas", 12)

# color of each token kind (used in the editor and in the token table)
KIND_COLORS = {
    "KEYWORD_INT": "#d2a8ff", "KEYWORD_IF": "#d2a8ff", "IDENTIFIER": "#79c0ff",
    "INTEGER_LITERAL": "#ffa657", "FLOAT_LITERAL": "#ffa657", "PLUS": "#7ee787", "EQUAL": "#7ee787",
    "KEYWORD_FLOAT": "#d2a8ff", "KEYWORD_BOOL": "#d2a8ff", "KEYWORD_CHAR": "#d2a8ff",
    "KEYWORD_STRING": "#d2a8ff", "KEYWORD_FUNC": "#d2a8ff", "KEYWORD_IF": "#d2a8ff",
    "KEYWORD_ELIF": "#d2a8ff", "KEYWORD_ELSE": "#d2a8ff", "KEYWORD_WHILE": "#d2a8ff",
    "KEYWORD_FOR": "#d2a8ff", "KEYWORD_FOREACH": "#d2a8ff", "KEYWORD_RETURN": "#d2a8ff",
    "KEYWORD_BREAK": "#d2a8ff", "KEYWORD_CONTINUE": "#d2a8ff", "KEYWORD_PRINT": "#d2a8ff",
    "KEYWORD_INPUT": "#d2a8ff", "KEYWORD_IN": "#d2a8ff", "KEYWORD_TRUE": "#79c0ff", "KEYWORD_FALSE": "#79c0ff",
    "STRING_LITERAL": "#a5d6ff", "CHAR_LITERAL": "#a5d6ff", "SEMICOLON": "#e3b341",
    "LPAREN": "#e3b341", "RPAREN": "#e3b341", "LBRACE": "#e3b341", "RBRACE": "#e3b341",
}


def column_ids(count):
    """Names for the table columns: c0, c1, c2 ... (plain strings)"""
    return [f"c{i}" for i in range(count)]


class LexerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NovaScript+  ·  Phase 2 Lexer")
        self.geometry("1250x780")
        self.minsize(950, 620)
        self.configure(bg=BG)
        self.scanner = Scanner(BASE / "transition_table.csv")
        self.images = []              # we must keep the images in a list, otherwise tkinter deletes them
        self.used_tags = set()        # tags the last scan added to the editor, so we can remove them next time
        self._apply_style()
        self._build_header()
        self._build_console()         # the console is packed first (at the bottom) so the editor cannot hide it
        self._build_main()
        self._load_file(BASE / "samples" / "basic.ns")

    # ---- style (colors of the widgets) ----
    def _apply_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=BG, foreground=FG, fieldbackground=PANEL, bordercolor=BORDER,
                    lightcolor=BG, darkcolor=BG, troughcolor=BG, font=UI_FONT)
        s.configure("TButton", background=PANEL, foreground=FG, padding=(16, 8), borderwidth=0,
                    focusthickness=0, focuscolor=PANEL)
        s.map("TButton", background=[("active", "#232b3a")])
        s.configure("Accent.TButton", background=ACCENT, foreground="#0b0f14", font=("Segoe UI", 10, "bold"))
        s.map("Accent.TButton", background=[("active", "#79b8ff")])
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG, foreground=MUTED, padding=(18, 9), borderwidth=0)
        s.map("TNotebook.Tab", background=[("selected", PANEL)], foreground=[("selected", FG)])
        s.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=28, borderwidth=0)
        s.map("Treeview", background=[("selected", "#264f78")], foreground=[("selected", "#ffffff")])
        s.configure("Treeview.Heading", background="#1f2633", foreground=FG, relief="flat",
                    padding=7, font=("Segoe UI", 10, "bold"))
        s.map("Treeview.Heading", background=[("active", "#2a3345")])
        s.configure("TScrollbar", background="#2a3140", troughcolor=PANEL, arrowcolor=MUTED, borderwidth=0)
        s.configure("TPanedwindow", background=BG)

    # ---- building the window ----
    def _build_header(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(bar, text="NovaScript+", bg=BG, fg=FG, font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Label(bar, text="Phase 2  ·  complete lexer with panic-mode recovery", bg=BG, fg=MUTED,
                 font=UI_FONT).pack(side="left", padx=14, pady=(10, 0))
        self.status = tk.Label(bar, bg=PANEL, fg=MUTED, font=("Segoe UI", 10, "bold"), padx=14, pady=6)
        self.status.pack(side="right")

        tools = tk.Frame(self, bg=BG)
        tools.pack(fill="x", padx=20, pady=(8, 6))
        ttk.Button(tools, text="Open file", command=self._open).pack(side="left", padx=(0, 8))
        ttk.Button(tools, text="Scan  (F5)", style="Accent.TButton", command=self._scan).pack(side="left", padx=(0, 8))
        ttk.Button(tools, text="Clear", command=self._clear).pack(side="left")
        self.file_label = tk.Label(tools, bg=BG, fg=MUTED, font=UI_FONT)
        self.file_label.pack(side="left", padx=16)
        self.bind("<F5>", lambda event: self._scan())

    def _build_console(self):
        box = tk.Frame(self, bg=PANEL)
        box.pack(side="bottom", fill="x", padx=20, pady=(6, 18))
        tk.Label(box, text="CONSOLE", bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x", padx=14, pady=(10, 2))
        self.console = tk.Text(box, height=6, bg=PANEL, fg=FG, font=("Consolas", 11), bd=0,
                               highlightthickness=0, padx=14, pady=4, state="disabled")
        self.console.pack(fill="x", pady=(0, 8))
        self.console.tag_configure("ok", foreground=GOOD)
        self.console.tag_configure("bad", foreground=BAD)

    def _build_main(self):
        panes = ttk.PanedWindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=20, pady=6)
        panes.add(self._build_editor(panes), weight=1)
        panes.add(self._build_tabs(panes), weight=1)

    def _build_editor(self, parent):
        card = tk.Frame(parent, bg=PANEL)
        tk.Label(card, text="SOURCE PROGRAM", bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "bold"),
                 anchor="w").pack(fill="x", padx=14, pady=(10, 6))
        body = tk.Frame(card, bg=EDITOR)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.numbers = tk.Text(body, width=4, bg=EDITOR, fg=MUTED, font=CODE_FONT, bd=0, padx=8, pady=10,
                               highlightthickness=0, state="disabled", takefocus=0, cursor="arrow")
        self.numbers.pack(side="left", fill="y")
        self.scrollbar = ttk.Scrollbar(body, command=self._scroll_both)
        self.scrollbar.pack(side="right", fill="y")
        self.editor = tk.Text(body, bg=EDITOR, fg=FG, insertbackground=FG, selectbackground="#264f78",
                              font=CODE_FONT, bd=0, padx=10, pady=10, highlightthickness=0, wrap="none",
                              undo=True, yscrollcommand=self._on_editor_scroll)
        self.editor.pack(side="left", fill="both", expand=True)
        self.editor.tag_configure("error", background="#5c1f24", foreground="#ffa198", underline=True)
        self.editor.bind("<KeyRelease>", lambda event: self._update_numbers())
        return card

    def _build_tabs(self, parent):
        tabs = ttk.Notebook(parent)
        self.token_table = self._table_tab(tabs, "Tokens", ("#", "Lexeme", "Kind", "Line", "Column"))
        return tabs

    def _table_tab(self, tabs, title, headings):
        frame = tk.Frame(tabs, bg=PANEL)
        tabs.add(frame, text=title)
        table = ttk.Treeview(frame, columns=column_ids(len(headings)), show="headings")
        for column, name in zip(column_ids(len(headings)), headings):
            table.heading(column, text=name)
            table.column(column, width=64, minwidth=44, anchor="center")
        bar = ttk.Scrollbar(frame, command=table.yview)
        table.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        table.pack(fill="both", expand=True)
        return table

    def _image_tab(self, tabs, title, filename):
        frame = tk.Frame(tabs, bg=PANEL)
        tabs.add(frame, text=title)
        canvas = tk.Canvas(frame, bg=PANEL, highlightthickness=0)
        vbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-1 if event.delta > 0 else 1, "units"))
        try:
            image = tk.PhotoImage(file=str(BASE / "diagrams" / filename))
        except tk.TclError:
            canvas.create_text(20, 20, anchor="nw", fill=MUTED, font=UI_FONT, text=f"diagrams/{filename} not found")
            return
        self.images.append(image)
        canvas.create_image(10, 10, anchor="nw", image=image)
        canvas.configure(scrollregion=(0, 0, image.width() + 20, image.height() + 20))

    # ---- line numbers (they scroll together with the editor) ----
    def _scroll_both(self, *args):
        self.editor.yview(*args)
        self.numbers.yview(*args)

    def _on_editor_scroll(self, first, last):
        # move the scrollbar and the line numbers together
        self.scrollbar.set(first, last)
        self.numbers.yview_moveto(first)

    def _update_numbers(self):
        count = int(self.editor.index("end-1c").split(".")[0])
        self.numbers.configure(state="normal")
        self.numbers.delete("1.0", "end")
        self.numbers.insert("1.0", "\n".join(str(i) for i in range(1, count + 1)))
        self.numbers.configure(state="disabled")

    # ---- buttons ----
    def _open(self):
        path = filedialog.askopenfilename(title="Open NovaScript+ source",
                                          filetypes=[("NovaScript+", "*.ns"), ("All files", "*.*")])
        if path:
            self._load_file(Path(path))

    def _load_file(self, path):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            self._write_console([(f"✗ Cannot open {path.name}: {error}", "bad")])
            return
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)
        self.file_label.configure(text=path.name)
        self._update_numbers()
        self._scan()

    def _clear(self):
        self.editor.delete("1.0", "end")
        self.token_table.delete(*self.token_table.get_children())
        self.file_label.configure(text="")
        self.status.configure(text="● Ready", fg=MUTED)
        self._write_console([])
        self._update_numbers()

    def _scan(self):
        # get the text, scan it, then show the tokens, the colors and the console
        tokens, errors = self.scanner.scan(self.editor.get("1.0", "end-1c"))
        self._show_tokens(tokens)
        self._color_editor(tokens, errors)
        lines = [(f"✗ {error}", "bad") for error in errors]
        if errors:
            lines.append((f"✗ Scan finished with {len(errors)} error(s); {len(tokens)} valid tokens.", "bad"))
            self.status.configure(text=f"● {len(errors)} lexical error(s)", fg=BAD)
        else:
            lines.append((f"✓ Scan finished: {len(tokens)} tokens, no lexical errors.", "ok"))
            self.status.configure(text=f"● {len(tokens)} tokens · no errors", fg=GOOD)
        self._write_console(lines)

    # ---- showing the results ----
    def _show_tokens(self, tokens):
        self.token_table.delete(*self.token_table.get_children())
        for number, t in enumerate(tokens, start=1):
            self.token_table.tag_configure(t.kind, foreground=KIND_COLORS.get(t.kind, FG))
            self.token_table.insert("", "end", values=(number, t.lexeme, t.kind, t.line, t.column), tags=(t.kind,))
        self.token_table.column("c2", width=130)

    def _color_editor(self, tokens, errors):
        # remove the colors of the last scan first
        for tag in self.used_tags:
            self.editor.tag_remove(tag, "1.0", "end")
        self.used_tags = {"error"}
        # color every token, then mark every error
        for t in tokens:
            self.editor.tag_configure(t.kind, foreground=KIND_COLORS.get(t.kind, FG))
            self._tag(t.kind, t.line, t.column, len(t.lexeme))
            self.used_tags.add(t.kind)
        for e in errors:
            self._tag("error", e.line, e.column, len(e.char))
        self.editor.tag_raise("error")

    def _tag(self, name, line, column, length):
        # our columns start at 1 but tkinter starts at 0, so we use column - 1
        start = f"{line}.{column - 1}"
        self.editor.tag_add(name, start, f"{start}+{length}c")

    def _write_console(self, lines):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        for text, tag in lines:
            self.console.insert("end", text + "\n", tag)
        self.console.configure(state="disabled")


if __name__ == "__main__":
    try:
        LexerUI().mainloop()
    except (tk.TclError, OSError) as error:
        print(f"UI could not start: {error}")
