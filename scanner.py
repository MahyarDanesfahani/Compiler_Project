"""Phase 2 lexer implemented with PLY."""
from dataclasses import dataclass
from pathlib import Path
import sys
import ply.lex as lex

KEYWORDS = {w: "KEYWORD_" + w.upper() for w in "int float bool char string func if elif else while for foreach in return break continue print input true false".split()}
tokens = tuple("ID INTEGER_LITERAL FLOAT_LITERAL HEX_LITERAL STRING_LITERAL CHAR_LITERAL PLUS MINUS STAR SLASH PERCENT EQUAL EQUAL_EQUAL NOT_EQUAL LESS LESS_EQUAL GREATER GREATER_EQUAL AND OR NOT SEMICOLON COMMA LPAREN RPAREN LBRACE RBRACE LBRACKET RBRACKET".split()) + tuple(KEYWORDS.values())
t_PLUS=r"\+"; t_MINUS=r"-"; t_STAR=r"\*"; t_SLASH=r"/"; t_PERCENT=r"%"; t_EQUAL_EQUAL=r"=="; t_NOT_EQUAL=r"!="; t_LESS_EQUAL=r"<="; t_GREATER_EQUAL=r">="; t_LESS=r"<"; t_GREATER=r">"; t_EQUAL=r"="; t_NOT=r"!"; t_AND=r"&&"; t_OR=r"\|\|"; t_SEMICOLON=r";"; t_COMMA=r","; t_LPAREN=r"\("; t_RPAREN=r"\)"; t_LBRACE=r"\{"; t_RBRACE=r"\}"; t_LBRACKET=r"\["; t_RBRACKET=r"\]"; t_ignore=" \t\r"
def t_COMMENT(t):
    r"//[^\n]*|/\*[\s\S]*?\*/"; t.lexer.lineno += t.value.count("\n")
def t_FLOAT_LITERAL(t):
    r"(?:\d+\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)"; return t
def t_HEX_LITERAL(t):
    r"0[xX][0-9a-fA-F]+"; return t
def t_INTEGER_LITERAL(t):
    r"\d+"; return t
def t_STRING_LITERAL(t):
    r'"(?:\\.|[^"\\])*"'; return t
def t_CHAR_LITERAL(t):
    r"'(?:\\.|[^'\\])'"; return t
def t_ID(t):
    r"[A-Za-z_]\w*"; t.type=KEYWORDS.get(t.value,"ID"); return t
def t_newline(t):
    r"\n+"; t.lexer.lineno += len(t.value)
@dataclass(frozen=True)
class Token: kind:str; lexeme:str; line:int; column:int
@dataclass(frozen=True)
class LexError:
    line:int; column:int; char:str
    def __str__(self): return f"Lexical error at line {self.line}, column {self.column}: invalid character {self.char!r}"
def t_error(t):
    t.value=t.value[0]; t.lexer.skip(1); t.type="ERROR"; return t
class Scanner:
    def __init__(self, table_path=None): self.lexer=lex.lex(module=sys.modules[__name__], optimize=False)
    def scan(self, source):
        self.lexer.lineno=1; self.lexer.input(source); out=[]; errors=[]
        while (tok:=self.lexer.token()):
            line_start=source.rfind("\n",0,tok.lexpos)+1; col=tok.lexpos-line_start+1
            (errors if tok.type=="ERROR" else out).append(LexError(tok.lineno,col,tok.value) if tok.type=="ERROR" else Token(tok.type,tok.value,tok.lineno,col))
        return out, errors
if __name__=="__main__":
    p=Path(sys.argv[1]); ts,es=Scanner().scan(p.read_text(encoding="utf-8")); print(*ts,sep="\n"); print(*es,sep="\n")
