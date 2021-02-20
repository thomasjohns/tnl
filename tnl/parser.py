from typing import List
from typing import NoReturn
from typing import Optional

from tnl.ast import Module
from tnl.ast import Definition
from tnl.ast import Transform
from tnl.ast import Test
from tnl.ast import RuleBlock
from tnl.ast import AliasBlock
from tnl.ast import HeaderBlock
from tnl.ast import ValueBlock
from tnl.ast import HeaderRule
from tnl.ast import ValueRule
from tnl.ast import Pipeline
from tnl.ast import Operation
from tnl.ast import RValue
from tnl.ast import Header
from tnl.ast import Name
from tnl.ast import ColumnSelector
from tnl.ast import Conditional
from tnl.ast import Map
from tnl.ast import Expr
from tnl.ast import String
from tnl.ast import Number
from tnl.ast import Pattern
from tnl.token import Token
from tnl.token import TokenKind
from tnl.map_impls import BUILT_IN_FUNCTIONS
from tnl.map_impls import MAP_IMPL_REGISTRY


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

RESERVED_NAMES = KEYWORDS | BUILT_IN_FUNCTIONS


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
        self.eat_any_newlines()
        while self.at_definition:
            definition = self.parse_definition()
            definitions.append(definition)
            self.eat_any_newlines()
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

    def parse_execution(self) -> Pipeline:
        if self.next_token.kind == TokenKind.LBRACKET:
            operations = self.parse_multi_line_pipeline()
        else:
            operations = self.parse_single_line_pipeline()
        return Pipeline(operations)

    def parse_single_line_pipeline(self) -> List[Operation]:
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

    def parse_multi_line_pipeline(self) -> List[Operation]:
        self.expect_and_eat(TokenKind.LBRACKET)
        self.eat_any_newlines()
        operations: List[Operation] = []
        while self.cur_token.kind != TokenKind.RBRACKET:
            more_operations = self.parse_single_line_pipeline()
            operations.extend(more_operations)
            self.eat_any_newlines()
        self.expect_and_eat(TokenKind.RBRACKET)
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
            self.error(f'Unrecognized map \'{name.data}\'.')
        map_impl = MAP_IMPL_REGISTRY[name.data]
        args_list: List[RValue] = []
        for _ in range(map_impl.num_args):
            arg = self.parse_rvalue()
            args_list.append(arg)
        return Map(name, tuple(args_list))

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

    def parse_expr(self) -> Expr:
        expr: Expr
        if self.cur_token.kind == TokenKind.NUMBER:
            expr = self.parse_number()
        elif self.cur_token.kind == TokenKind.STRING:
            expr = self.parse_string()
        else:
            # TODO for now assume string or number literal
            assert 0, self.cur_token
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
