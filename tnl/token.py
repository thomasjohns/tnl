from enum import auto
from enum import Enum
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
    TRUE = 'True'
    FALSE = 'False'
    STRING = auto()
    NUMBER = auto()
    PATTERN = auto()
    INVALID = auto()
    EOF = auto()


class Position:
    def __init__(self, filename: str, line: int, col: int) -> None:
        self.filename = filename
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
