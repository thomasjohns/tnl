from typing import List
from typing import Union


Definition = Union['Transform', 'Test']
RuleBlock = Union['AliasBlock', 'HeaderBlock', 'ValueBlock']
Header = Union['Name', 'Literal']
Value = Union['Name', 'Literal']
Argument = Union['Name', 'Literal']


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
    def __init__(self, value: Value, pipeline: 'Pipeline') -> None:
        self.value = value
        self.pipeline = pipeline


class Pipeline(ASTNode):
    def __init__(self, functions: List['Function']) -> None:
        self.functions = functions


class Function(ASTNode):
    def __init__(self, name: 'Name', args: List[Argument]) -> None:
        self.name = name
        self.args = args


class Name(ASTNode):
    def __init__(self, data: str) -> None:
        self.data = data


class Literal(ASTNode):
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
