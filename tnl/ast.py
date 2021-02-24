import re
from typing import Literal as TypeLiteral
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union


Definition = Union['Transform', 'Test']
RuleBlock = Union['AliasBlock', 'HeaderBlock', 'ValueBlock']
Header = Union['Name', 'String', 'Pattern']
# TODO: check to see if these lints are flake8 bugs
UnaryOpOp = TypeLiteral['-', '!']  # noqa F722
BinaryOpOp = TypeLiteral['*', '/', '%', '+', '-']  # noqa F722


class ASTNode:
    pass


class Module(ASTNode):
    def __init__(self, definitions: List[Definition]) -> None:
        self.definitions = definitions


class Transform(ASTNode):
    def __init__(self, name: 'Name', rule_blocks: List[RuleBlock]) -> None:
        self.name = name
        self.rule_blocks = rule_blocks


class Test(ASTNode):
    # TODO
    pass


class AliasBlock(ASTNode):
    def __init__(self, alias_rules: List['AliasRule']) -> None:
        self.alias_rules = alias_rules


class HeaderBlock(ASTNode):
    def __init__(self, header_rules: List['HeaderRule']) -> None:
        self.header_rules = header_rules


class ValueBlock(ASTNode):
    def __init__(self, value_rules: List['ValueRule']) -> None:
        self.value_rules = value_rules


class AliasRule(ASTNode):
    def __init__(self, name: 'Name', value: 'Literal') -> None:
        self.name = name
        self.value = value


class HeaderRule(ASTNode):
    def __init__(self, header: Header, pipeline: 'Pipeline') -> None:
        self.header = header
        self.pipeline = pipeline


class ValueRule(ASTNode):
    def __init__(self, rvalue: 'RValue', pipeline: 'Pipeline') -> None:
        self.rvalue = rvalue
        self.pipeline = pipeline


class Pipeline(ASTNode):
    def __init__(self, operations: List['Operation']) -> None:
        self.operations = operations


class Operation(ASTNode):
    pass


class Expr(Operation):
    pass


class BinaryOp(Expr):
    def __init__(self, op: BinaryOpOp, left: Expr, right: Expr) -> None:
        self.op = op
        self.left = left
        self.right = right


class UnaryOp(Expr):
    def __init__(self, op: UnaryOpOp, expr: Expr) -> None:
        self.op = op
        self.expr = expr


# TODO: make something like LogicalOp for easier semantic analysis
#       the negation, unary_op vs binary_op might be interesting
class Conditional(Operation):
    def __init__(
        self,
        test: Expr,
        true_pipeline: Pipeline,
        false_pipeline: Optional[Pipeline],
    ) -> None:
        self.test = test
        self.true_pipeline = true_pipeline
        self.false_pipeline = false_pipeline


class Map(Operation):
    def __init__(self, name: 'Name', args: Tuple['RValue', ...]) -> None:
        self.name = name
        self.args = args


class RValue(Expr):
    pass


class ColumnSelector(RValue):
    def __init__(self, header: Header) -> None:
        self.header = header


class Name(RValue):
    def __init__(self, data: str) -> None:
        self.data = data


class Literal(RValue):
    pass


class String(Literal):
    def __init__(self, data: str) -> None:
        self.data = data


class Number(Literal):
    def __init__(self, data: int) -> None:
        self.data = data


class Pattern(Literal):
    def __init__(self, data: str) -> None:
        self.data = data
        self._compiled_pattern: Optional[re.Pattern[str]] = None

    def get_compiled_pattern(self) -> re.Pattern[str]:
        if self._compiled_pattern is None:
            self._compiled_pattern = re.compile(self.data)
        return self._compiled_pattern
