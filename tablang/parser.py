from typing import Dict
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Protocol
from typing import Type

import pandas as pd  # type: ignore

from tablang.ast import Module
from tablang.ast import Definition
from tablang.ast import Transform
from tablang.ast import Test
from tablang.ast import RuleBlock
from tablang.ast import AliasBlock
from tablang.ast import HeaderBlock
from tablang.ast import ValueBlock
from tablang.ast import HeaderRule
from tablang.ast import ValueRule
from tablang.ast import Pipeline
from tablang.ast import Operation
from tablang.ast import RValue
from tablang.ast import Header
from tablang.ast import Name
from tablang.ast import ColumnSelector
from tablang.ast import Conditional
from tablang.ast import Map
from tablang.ast import Expr
from tablang.ast import String
from tablang.ast import Number
from tablang.ast import Pattern
from tablang.token import Token
from tablang.token import TokenKind


TRANSFORM = 'transform'
TEST = 'test'
ALIASES = 'aliases'
HEADERS = 'headers'
VALUES = 'values'
IF = 'if'
ELSE = 'else'
KEYWORDS = {
    TRANSFORM,
    TEST,
    ALIASES,
    HEADERS,
    VALUES,
    IF,
    ELSE,
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


# TODO turn this into module or something
#      and protocol for e.g. num_args
class MapImpl(Protocol):
    num_args: int


# TODO maybe have protocol for header and value maps
class AddImpl(MapImpl):
    num_args = 1

    def map_value(self, s: pd.Series, arg1: int) -> pd.Series:
        return s + arg1


class MultImpl(MapImpl):
    num_args = 1

    def map_value(self, s: pd.Series, arg1: int) -> pd.Series:
        return s * arg1


MAP_IMPL_REGISTRY: Dict[str, Type[MapImpl]] = {
    ADD: AddImpl,
    MULT: MultImpl,
}


class Parser:
    def __init__(self, tokens: List[Token], filename: str) -> None:
        self.tokens = tokens
        self.filename = filename

        self.token_index = -1
        self.cur_token = Token(TokenKind.INVALID, None, (0, 0))

    def error(self, message: str) -> NoReturn:
        print('Syntax Error:')
        print(message)
        print(f'In file {self.filename}.')
        exit(1)

    def error_expecting(self, *kinds: TokenKind) -> None:
        if len(kinds) == 1:
            kind = kinds[0]
            message = (
                f'Expected token {kind.name}, '
                f'but found {self.cur_token.kind.name} '
                f'at {self.cur_token.loc}.'
            )
        else:
            names_of_kinds = [kind.name for kind in kinds]
            message = (
                f'Expecing one of {names_of_kinds}, but found '
                f'{self.cur_token.kind.name} at {self.cur_token.loc}.'
            )
        self.error(message)

    def eat(self) -> None:
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.cur_token = self.tokens[self.token_index]
        else:
            self.error('Unexpected end of file.')

    @property
    def next_token(self) -> Token:
        if self.token_index + 1 < len(self.tokens):
            return self.tokens[self.token_index]
        elif self.token_index + 1 == len(self.tokens):
            self.error(f'Unexpected end of file at {self.cur_token}')
        else:
            self.error('Unexpected end of file')

    def eat_expecting(self, *kinds: TokenKind) -> None:
        self.eat()
        if self.cur_token.kind not in {*kinds}:
            self.error_expecting(*kinds)

    def expect_and_eat(self, *kinds: TokenKind) -> None:
        if self.cur_token.kind not in {*kinds}:
            self.error_expecting(*kinds)
        self.eat()

    def expect(self, *kinds: TokenKind) -> None:
        if self.cur_token.kind not in {*kinds}:
            self.error_expecting(*kinds)

    def eat_newlines_expecting_at_least_one(self) -> None:
        self.expect_and_eat(TokenKind.NEWLINE)
        while self.cur_token.kind == TokenKind.NEWLINE:
            self.eat()

    def eat_any_newlines(self) -> None:
        while self.cur_token.kind == TokenKind.NEWLINE:
            self.eat()

    @staticmethod
    def assume_lexeme(lexeme: Optional[str]) -> str:
        assert lexeme is not None, (
            f'found {TokenKind.NAME.name} token with no lexeme'
        )
        return lexeme

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
        self.expect(TokenKind.EOF)
        return Module(definitions)

    def parse_definition(self) -> Definition:
        if self.cur_token.lexeme == TRANSFORM:
            transform = self.parse_transform()
            return transform
        elif self.cur_token.lexeme == TEST:
            test = self.parse_test()
            return test
        assert 0, 'should be at a definition'

    def parse_transform(self) -> Transform:
        self.expect_and_eat(TokenKind.NAME)
        lexeme = self.assume_lexeme(self.cur_token.lexeme)
        if lexeme in RESERVED_NAMES:
            self.error(
                f'Name {lexeme} is a reserved word an cannot be used as a '
                'Transform name'
            )
        self.expect_and_eat(TokenKind.NAME)
        self.eat_any_newlines()
        self.expect_and_eat(TokenKind.LBRACKET)
        self.eat_any_newlines()
        rule_blocks: List[RuleBlock] = []
        while self.cur_token.kind != TokenKind.RBRACKET:
            rule_block = self.parse_rule_block()
            rule_blocks.append(rule_block)
        self.eat_any_newlines()
        self.expect_and_eat(TokenKind.RBRACKET)
        self.eat_any_newlines()
        return Transform(Name(lexeme), rule_blocks)

    def parse_test(self) -> Test:
        # TODO
        return Test()

    def parse_rule_block(self) -> RuleBlock:
        self.expect(TokenKind.NAME)
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
        self.expect_and_eat(TokenKind.NAME)
        self.eat_any_newlines()
        self.expect_and_eat(TokenKind.LBRACKET)
        self.eat_any_newlines()
        header_rules: List[HeaderRule] = []
        while self.cur_token.kind != TokenKind.RBRACKET:
            header_rule = self.parse_header_rule()
            header_rules.append(header_rule)
        self.eat_any_newlines()
        self.expect_and_eat(TokenKind.RBRACKET)
        self.eat_any_newlines()
        return HeaderBlock(header_rules)

    def parse_header_rule(self) -> HeaderRule:
        # we check for 'headers' specifically in parse_rule_block
        header = self.parse_header()
        self.expect_and_eat(TokenKind.ARROW)
        pipeline = self.parse_execution()
        self.eat_newlines_expecting_at_least_one()
        return HeaderRule(header, pipeline)

    def parse_header(self) -> Header:
        header: Header
        if self.cur_token.kind == TokenKind.STRING:
            header = self.parse_string()
        elif self.cur_token.kind == TokenKind.NAME:
            header = self.parse_name()
        elif self.cur_token.kind == TokenKind.PATTERN:
            header = self.parse_pattern()
        else:
            self.error_expecting(
                TokenKind.STRING,
                TokenKind.NAME,
                TokenKind.PATTERN,
            )
        return header

    def parse_value_block(self) -> ValueBlock:
        # we check for 'values' specifically in parse_rule_block
        self.expect_and_eat(TokenKind.NAME)
        self.eat_any_newlines()
        self.expect_and_eat(TokenKind.LBRACKET)
        self.eat_any_newlines()
        value_rules: List[ValueRule] = []
        while self.cur_token.kind != TokenKind.RBRACKET:
            value_rule = self.parse_value_rule()
            value_rules.append(value_rule)
        self.eat_any_newlines()
        self.expect_and_eat(TokenKind.RBRACKET)
        self.eat_any_newlines()
        return ValueBlock(value_rules)

    def parse_value_rule(self) -> ValueRule:
        rvalue = self.parse_rvalue()
        self.expect_and_eat(TokenKind.ARROW)
        pipeline = self.parse_execution()
        self.eat_any_newlines()
        return ValueRule(rvalue, pipeline)

    def parse_rvalue(self) -> RValue:
        rvalue: RValue
        if self.cur_token.kind == TokenKind.NAME:
            rvalue = self.parse_name()
        elif self.cur_token.kind == TokenKind.STRING:
            rvalue = self.parse_string()
        elif self.cur_token.kind == TokenKind.NUMBER:
            rvalue = self.parse_number()
        elif self.cur_token.kind == TokenKind.PATTERN:
            rvalue = self.parse_pattern()
        elif self.cur_token.kind == TokenKind.LBRACE:
            rvalue = self.parse_column_selector()
        else:
            self.error_expecting(
                TokenKind.NAME,
                TokenKind.STRING,
                TokenKind.NUMBER,
                TokenKind.PATTERN,
                TokenKind.LBRACE,
            )
        return rvalue

    def parse_execution(self) -> Pipeline:
        if self.next_token.kind == TokenKind.LBRACKET:
            operations = self.parse_multi_line_pipeline()
        else:
            operations = self.parse_single_line_pipeline()
        return Pipeline(operations)

    def parse_single_line_pipeline(self) -> List[Operation]:
        pipeline = self.parse_pipeline()
        return pipeline

    def parse_multi_line_pipeline(self) -> List[Operation]:
        # TODO
        pass

    def parse_pipeline(self) -> List[Operation]:
        if self.cur_token.kind == TokenKind.PIPE:
            self.eat()
        operations: List[Operation] = []
        operation = self.parse_operation()
        operations.append(operation)
        while self.cur_token.kind == TokenKind.PIPE:
            self.eat()
            operation = self.parse_operation()
            operations.append(operation)
        return operations

    def parse_operation(self) -> Operation:
        operation: Operation
        if self.cur_token.kind == TokenKind.NAME:
            lexeme = self.assume_lexeme(self.cur_token.lexeme)
            if lexeme == IF:
                operation = self.parse_conditional()
            else:
                operation = self.parse_map()
        else:
            operation = self.parse_expr()
        return operation

    def parse_conditional(self) -> Conditional:
        # TODO
        ...

    def parse_map(self) -> Map:
        name = self.parse_name()
        if name.data not in MAP_IMPL_REGISTRY:
            self.error(f'Unrecognized map \'{name}\'.')
        map_impl = MAP_IMPL_REGISTRY[name.data]
        args: List[RValue] = []
        for _ in range(map_impl.num_args):
            arg = self.parse_rvalue()
            args.append(arg)
        return Map(name, args)

    def parse_expr(self) -> Expr:
        expr: Expr
        if self.cur_token.kind == TokenKind.NUMBER:
            expr = self.parse_number()
        elif self.cur_token.kind == TokenKind.STRING:
            expr = self.parse_string()
        else:
            # TODO for now assume string or number literal
            assert 0
        return expr

    def parse_string(self) -> String:
        self.expect(TokenKind.STRING)
        lexeme = self.assume_lexeme(self.cur_token.lexeme)
        self.eat()
        return String(lexeme)

    def parse_pattern(self) -> Pattern:
        self.expect(TokenKind.PATTERN)
        lexeme = self.assume_lexeme(self.cur_token.lexeme)
        self.eat()
        return Pattern(lexeme)

    def parse_name(self) -> Name:
        self.expect(TokenKind.NAME)
        lexeme = self.assume_lexeme(self.cur_token.lexeme)
        self.eat()
        return Name(lexeme)

    def parse_number(self) -> Number:
        self.expect(TokenKind.NUMBER)
        lexeme = self.assume_lexeme(self.cur_token.lexeme)
        self.eat()
        data = int(lexeme)
        return Number(data)

    def parse_column_selector(self) -> ColumnSelector:
        self.expect_and_eat(TokenKind.LBRACE)
        header = self.parse_header()
        self.expect_and_eat(TokenKind.RBRACE)
        return ColumnSelector(header)
