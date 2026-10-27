"""Phase 1: table-driven manual lexical scanner for NovaScript+ subset."""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path


ACCEPTING = {
    "qaccept_id": "IDENTIFIER",
    "qaccept_int": "INTEGER",
    "qaccept_plus": "PLUS",
    "qaccept_equal": "EQUAL",
    "qaccept_lparen": "LPAREN",
    "qaccept_rparen": "RPAREN",
}
BASE_ACCEPTING = {
    "q1": "IDENTIFIER", "q2": "INTEGER", "q3": "PLUS",
    "q4": "EQUAL", "q5": "LPAREN", "q6": "RPAREN",
}
KEYWORDS = {"int": "KEYWORD_INT", "if": "KEYWORD_IF"}


@dataclass(frozen=True)
class Token:
    kind: str
    lexeme: str
    line: int
    column: int


class TableDrivenScanner:
    def __init__(self, table_path: str | Path):
        self.table, self.states = self._load_table(Path(table_path))

    @staticmethod
    def _load_table(path: Path):
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        states = {row["state"] for row in rows}
        table = {(row["state"], column): row[column]
                 for row in rows for column in row if column != "state"}
        return table, states

    @staticmethod
    def _classify(char: str) -> str:
        if char.isalpha() or char == "_":
            return "letter"
        if char.isdigit():
            return "digit"
        return {"+": "+", "=": "=", "(": "(", ")": ")"}.get(char,
               "whitespace" if char.isspace() else "other")

    def scan(self, source: str):
        tokens: list[Token] = []
        errors: list[str] = []
        index, line, column = 0, 1, 1
        while index < len(source):
            if source[index].isspace():
                line, column = self._advance(source[index], line, column)
                index += 1
                continue
            start_index, start_line, start_column = index, line, column
            state = "q0"
            while index < len(source):
                category = self._classify(source[index])
                next_state = self.table.get((state, category), "qerr")
                if next_state == "qerr" or next_state in ACCEPTING:
                    break
                state = next_state
                line, column = self._advance(source[index], line, column)
                index += 1
            if index == start_index:
                errors.append(f"Lexical error at line {line}, column {column}: invalid character {source[index]!r}")
                line, column = self._advance(source[index], line, column)
                index += 1
                continue
            if state not in BASE_ACCEPTING:
                errors.append(f"Lexical error at line {start_line}, column {start_column}: invalid token {source[start_index:index]!r}")
                continue
            lexeme = source[start_index:index]
            kind = KEYWORDS.get(lexeme, BASE_ACCEPTING[state])
            tokens.append(Token(kind, lexeme, start_line, start_column))
        return tokens, errors

    @staticmethod
    def _advance(char: str, line: int, column: int):
        return (line + 1, 1) if char == "\n" else (line, column + 1)


def main():
    base = Path(__file__).parent
    source_path = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "samples" / "valid.ns"
    scanner = TableDrivenScanner(base / "transition_table.csv")
    tokens, errors = scanner.scan(source_path.read_text(encoding="utf-8"))
    print("TOKENS")
    for token in tokens:
        print(f"{token.kind:<14} {token.lexeme!r:<12} line={token.line} column={token.column}")
    print("\nERRORS")
    print("No lexical errors." if not errors else "\n".join(errors))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
