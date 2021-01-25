from typing import List
from typing import NoReturn

from tablang.token import Position
from tablang.token import Token
from tablang.token import TokenKind


class Lexer:
    def __init__(self, src: str, filename: str) -> None:
        self.src = src
        self.filename = filename
        self.pos = Position(1, 0)

        self.tokens: List[Token]

        self.reached_eof = False
        self.src_index = -1
        self.cur_char: str = ''

    def error(self, message: str) -> NoReturn:
        print(message)
        print(f'In file {self.filename} at {self.pos.loc}.')
        exit(1)

    def eat(self) -> None:
        if self.reached_eof:
            self.error('Unexpected end of file.')
        self.src_index += 1
        if self.src_index < len(self.src):
            self.cur_char = self.src[self.src_index]
        else:
            self.reached_eof = True
            self.cur_char = ''

        self.pos.advance()

    @property
    def next_char(self) -> str:
        if self.src_index + 1 < len(self.src):
            return self.src[self.src_index + 1]
        elif self.src_index + 1 == len(self.src):
            self.error(f'Unexpected end of file at {self.cur_char}')
        else:
            self.error('Unexpected end of file.')

    def lex(self) -> List[Token]:
        self.tokens = []
        self.eat()
        while not self.reached_eof:
            if self.cur_char == ' ' or self.cur_char == '\t':
                pass
            elif self.cur_char == '{':
                self.tokens.append(
                    Token(TokenKind.LBRACKET, '{', self.pos.loc)
                )
            elif self.cur_char == '}':
                self.tokens.append(
                    Token(TokenKind.RBRACKET, '}', self.pos.loc)
                )
            elif self.cur_char == '[':
                self.tokens.append(
                    Token(TokenKind.LBRACE, '[', self.pos.loc)
                )
            elif self.cur_char == ']':
                self.tokens.append(
                    Token(TokenKind.RBRACE, ']', self.pos.loc)
                )
            elif self.cur_char == '(':
                self.tokens.append(
                    Token(TokenKind.LPAREN, '(', self.pos.loc)
                )
            elif self.cur_char == ')':
                self.tokens.append(
                    Token(TokenKind.RPAREN, ')', self.pos.loc)
                )
            elif self.cur_char == '=':
                self.lex_eq()
            elif self.cur_char == '|':
                self.tokens.append(Token(TokenKind.PIPE, '|', self.pos.loc))
            elif self.cur_char == '*':
                self.tokens.append(Token(TokenKind.MULT, '*', self.pos.loc))
            elif self.cur_char == '/':
                self.tokens.append(Token(TokenKind.DIV, '/', self.pos.loc))
            elif self.cur_char == '+':
                self.tokens.append(Token(TokenKind.ADD, '+', self.pos.loc))
            elif self.cur_char == '%':
                self.tokens.append(Token(TokenKind.MOD, '%', self.pos.loc))
            elif self.cur_char == '!':
                self.tokens.append(Token(TokenKind.NOT, '!', self.pos.loc))
            elif self.cur_char == '\n':
                self.lex_newline()
            elif self.cur_char == '\'':
                self.lex_string()
            elif self.cur_char == '_' or self.cur_char.isalpha():
                self.lex_name()
            elif self.cur_char.isdigit():
                self.lex_number()
            elif self.cur_char == '/':
                self.lex_pattern()
            elif self.cur_char == '#':
                self.lex_comment()
            elif self.cur_char == '-':
                self.lex_arrow_or_sub()
            else:
                self.tokens.append(
                    Token(TokenKind.INVALID, None, self.pos.loc)
                )

            self.eat()

        self.tokens.append(Token(TokenKind.EOF, None, self.pos.loc))

        return self.tokens

    def lex_newline(self) -> None:
        self.tokens.append(Token(TokenKind.NEWLINE, None, self.pos.loc))
        self.pos.newline()

    def lex_number(self) -> None:
        initial_loc = self.pos.loc
        value = ''
        while self.cur_char.isdigit():
            value += self.cur_char
            self.eat()
        self.tokens.append(Token(TokenKind.NUMBER, value, initial_loc))

    def lex_name(self) -> None:
        initial_loc = self.pos.loc
        value = ''
        while (
            self.cur_char == '_' or
            self.cur_char.isalpha() or
            self.cur_char.isdigit()
        ):
            value += self.cur_char
            self.eat()
        self.tokens.append(Token(TokenKind.NAME, value, initial_loc))

    def lex_string(self) -> None:
        initial_loc = self.pos.loc
        self.eat()
        value = ''
        escaping = False
        while not escaping and self.cur_char != '\'':
            if self.cur_char == '\\':
                escaping = True
            else:
                value += self.cur_char
                escaping = False
            self.eat()
        self.tokens.append(Token(TokenKind.STRING, value, initial_loc))

    def lex_pattern(self) -> None:
        initial_loc = self.pos.loc
        value = ''
        escaping = False
        while not escaping and self.cur_char != '/':
            if self.cur_char == '\\':
                escaping = True
            else:
                value += self.cur_char
                escaping = False
            self.eat()
        self.tokens.append(Token(TokenKind.PATTERN, value, initial_loc))

    def lex_comment(self) -> None:
        while self.cur_char != '\n':
            self.eat()
        self.pos.newline()

    def lex_arrow_or_sub(self) -> None:
        initial_loc = self.pos.loc
        if self.next_char == '>':
            self.eat()
            value = f'-{self.cur_char}'
            self.tokens.append(Token(TokenKind.ARROW, value, initial_loc))
        else:
            self.tokens.append(Token(TokenKind.SUB, '-', initial_loc))

    def lex_eq(self) -> None:
        if self.next_char == '=':
            self.tokens.append(Token(TokenKind.DEQ, '==', self.pos.loc))
            self.eat()
        else:
            self.tokens.append(Token(TokenKind.EQ, '=', self.pos.loc))
