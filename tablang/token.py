from enum import auto, Enum
from typing import Optional
from typing import Tuple


class TokenKind(Enum):
    ARROW = '->'
    LBRACKET = '{'
    RBRACKET = '}'
    LBRACE = '['
    RBRACE = ']'
    LPAREN = '('
    RPAREN = ')'
    DEQ = '=='
    EQ = '='
    PIPE = '|'
    MULT = '*'
    DIV = '/'
    ADD = '+'
    SUB = '-'
    MOD = '%'
    NOT = '!'
    NEWLINE = '\n'
    NAME = auto()
    KEWORD = auto()
    STRING = auto()
    NUMBER = auto()
    PATTERN = auto()
    INVALID = auto()
    EOF = auto()


class Position:
    def __init__(self, line: int, col: int) -> None:
        self.line = line
        self.col = col

    def advance(self) -> None:
        self.col += 1

    def newline(self) -> None:
        self.line += 1
        self.col = 1

    @property
    def loc(self) -> Tuple[int, int]:
        return (self.line, self.col)


class Token:
    def __init__(
        self,
        kind: TokenKind,
        lexeme: Optional[str],
        loc: Tuple[int, int],
    ) -> None:
        self.kind = kind
        self.lexeme = lexeme
        self.loc = loc

    def __str__(self) -> str:
        name_with_comma = f'{self.kind.name},'
        lexeme_str = self.lexeme or 'None'
        lexeme_str_with_commma = f'{lexeme_str},'
        return f'{name_with_comma:10} {lexeme_str_with_commma:10} {self.loc}'
