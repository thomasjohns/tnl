from typing import List
from typing import NoReturn

from proto.ast import Module
from proto.ast import Definition
from proto.ast import Transform
from proto.ast import Test
from proto.ast import RuleBlock
from proto.ast import AliasBlock
from proto.ast import HeaderBlock
from proto.ast import ValueBlock
from proto.ast import Name
from proto.token import Token
from proto.token import TokenKind


TRANSFORM = 'transform'
TEST = 'test'
ALIASES = 'aliases'
HEADERS = 'headers'
VALUES = 'values'
KEYWORDS = {
    TRANSFORM,
    TEST,
    ALIASES,
    HEADERS,
    VALUES,
}

# TODO: perhaps there is be a better way to manage build-in functions
TRIM = 'trim'
TITLE = 'title'
REPLACE = 'replace'
ADD = 'add'
MULT = 'mult'
SQUARE = 'square'
BUILT_IN_FUNCTIONS = {
    TRIM,
    TITLE,
    REPLACE,
    ADD,
    MULT,
    SQUARE,
}

RESERVED_NAMES = KEYWORDS | BUILT_IN_FUNCTIONS


class Parser:
    def __init__(self, tokens: List[Token], filename: str) -> None:
        self.tokens = tokens
        self.filename = filename

        self.token_index = -1
        self.cur_token = Token(TokenKind.INVALID, None, (0, 0))

    def error(self, message: str) -> NoReturn:
        print('Syntax Error:', message)
        print(f'In file {self.filename}.')
        exit(1)

    def error_expecting(self, *kinds: TokenKind) -> None:
        if len(kinds) == 1:
            kind = kinds[0]
            message = (
                f'Expected token {kind.name}, '
                f'but found {self.cur_token.kind.name}.'
            )
        else:
            message = ''
        self.error(message)

    def eat(self) -> None:
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.cur_token = self.tokens[self.token_index]
        else:
            self.error('Unexpected end of file.')

    def eat_expecting(self, *kinds: TokenKind) -> None:
        self.eat()
        if self.cur_token.kind not in {*kinds}:
            self.error_expecting(*kinds)

    def eat_expecting_at_least_one_newline(self) -> None:
        self.eat_expecting(TokenKind.NEWLINE)
        while self.cur_token.kind == TokenKind.NEWLINE:
            self.eat()

    @property
    def at_definition(self) -> bool:
        return (
            self.cur_token.kind == TokenKind.NAME and
            self.cur_token.lexeme in {TRANSFORM, TEST}
        )

    def parse(self) -> Module:
        self.eat()
        module = self.parse_module()
        return module

    def parse_module(self) -> Module:
        definitions: List[Definition] = []
        while self.at_definition:
            definition = self.parse_definition()
            definitions.append(definition)
        if self.cur_token.kind != TokenKind.EOF:
            value = self.cur_token.lexeme or ''
            self.error(f'Unexpected token {value} at {self.cur_token.loc}')
        return Module(definitions)

    def parse_definition(self) -> Definition:
        self.eat()
        if self.cur_token.lexeme == TRANSFORM:
            transform = self.parse_transform()
            return transform
        elif self.cur_token.lexeme == TEST:
            test = self.parse_test()
            return test
        assert 0, 'should be at a definition'

    def parse_transform(self) -> Transform:
        self.eat_expecting(TokenKind.NAME)
        lexeme = self.cur_token.lexeme
        assert lexeme is not None, (
            f'found {TokenKind.NAME.name} token with no lexeme'
        )
        if lexeme in RESERVED_NAMES:
            self.error(
                f'Name {lexeme} is a reserved word an cannot be used as a '
                'Transform name'
            )
        self.eat_expecting(TokenKind.LBRACKET)
        self.eat_expecting_at_least_one_newline()
        rule_blocks: List[RuleBlock] = []
        while self.cur_token.kind != TokenKind.RBRACKET:
            rule_block = self.parse_rule_block()
            rule_blocks.append(rule_block)
        self.eat_expecting_at_least_one_newline()
        return Transform(Name(lexeme), rule_blocks)

    def parse_test(self) -> Test:
        # TODO
        return Test()

    def parse_rule_block(self) -> RuleBlock:
        self.eat_expecting(TokenKind.NAME)
        rule_kind = self.cur_token.lexeme
        rule_block: RuleBlock
        if rule_kind == ALIASES:
            rule_block = self.parse_alias_block()
        elif rule_kind == HEADERS:
            rule_block = self.parse_header_block()
        elif rule_kind == VALUES:
            rule_block = self.parse_value_block()
        else:
            self.error(
                f'Expected {ALIASES}, {HEADERS}, or {VALUES}, '
                f'but found {rule_kind}'
            )
        return rule_block

    def parse_alias_block(self) -> AliasBlock:
        # TODO
        return AliasBlock([])

    def parse_header_block(self) -> HeaderBlock:
        # TODO
        return HeaderBlock([])

    def parse_value_block(self) -> ValueBlock:
        # TODO
        return ValueBlock([])
