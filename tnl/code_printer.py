from tnl.ast import Module
from tnl.ast import Transform
from tnl.ast import Test
from tnl.ast import AliasBlock
from tnl.ast import HeaderBlock
from tnl.ast import ValueBlock
from tnl.ast import AliasRule
from tnl.ast import HeaderRule
from tnl.ast import ValueRule
from tnl.ast import Pipeline
from tnl.ast import BinaryOp
from tnl.ast import UnaryOp
from tnl.ast import Conditional
from tnl.ast import Map
from tnl.ast import ColumnSelector
from tnl.ast import Name
from tnl.ast import String
from tnl.ast import Number
from tnl.ast import Pattern
from tnl.ast import Boolean
from tnl.ast_visitor import ASTVisitor


def print_module_code(ast: Module, indent_spaces: int = 4) -> None:
    ast_printer = CodePrinter(indent_spaces)
    ast_printer.visit(ast)


class CodePrinter(ASTVisitor):
    def __init__(self, indent_spaces: int) -> None:
        self.indent_spaces = indent_spaces
        self.cur_indent_spaces = 0

    def indent(self) -> None:
        self.cur_indent_spaces += self.indent_spaces

    def dedent(self) -> None:
        self.cur_indent_spaces -= self.indent_spaces

    def indenting_print(self, message: str = '', end: str = '\n') -> None:
        print(' ' * self.cur_indent_spaces, end='')
        print(message, end=end)

    def visit_Module(self, node: Module) -> None:
        for definition in node.definitions:
            self.visit(definition)

    def visit_Transform(self, node: Transform) -> None:
        self.indenting_print('transform ', end='')
        self.visit(node.name)
        print(' {')
        self.indent()
        for rule_block in node.rule_blocks:
            self.visit(rule_block)
        self.dedent()
        self.indenting_print('}')

    def visit_Test(self, node: Test) -> None:
        # TODO
        pass

    def visit_AliasBlock(self, node: AliasBlock) -> None:
        # TODO
        pass

    def visit_HeaderBlock(self, node: HeaderBlock) -> None:
        self.indenting_print('headers {')
        self.indent()
        for header_rule in node.header_rules:
            self.visit(header_rule)
        self.dedent()
        self.indenting_print('}')

    def visit_ValueBlock(self, node: ValueBlock) -> None:
        self.indenting_print('values {')
        self.indent()
        for value_rule in node.value_rules:
            self.visit(value_rule)
        self.dedent()
        self.indenting_print('}')

    def visit_AliasRule(self, node: AliasRule) -> None:
        # TODO
        pass

    def visit_HeaderRule(self, node: HeaderRule) -> None:
        self.indenting_print(end='')
        self.visit(node.header)
        if len(node.pipeline.operations) > 1:
            print(' -> {')
            self.indent()
            self.visit(node.pipeline)
            self.dedent()
            self.indenting_print('}')
        else:
            print(' -> ', end='')
            self.visit(node.pipeline)
            print()

    def visit_ValueRule(self, node: ValueRule) -> None:
        self.indenting_print(end='')
        self.visit(node.rvalue)
        if len(node.pipeline.operations) > 1:
            print(' -> {')
            self.indent()
            self.visit(node.pipeline)
            self.dedent()
            self.indenting_print('}')
        else:
            print(' -> ', end='')
            self.visit(node.pipeline)
            print()

    def visit_Pipeline(self, node: Pipeline) -> None:
        if len(node.operations) > 1:
            for operation in node.operations:
                self.indenting_print('| ', end='')
                self.visit(operation)
                print()
        elif len(node.operations) == 1:
            self.visit(node.operations[0])
        else:
            print('{}')

    def visit_BinaryOp(self, node: BinaryOp) -> None:
        print('(', end='')
        self.visit(node.left)
        print(f' {node.op} ', end='')
        self.visit(node.right)
        print(')', end='')

    def visit_UnaryOp(self, node: UnaryOp) -> None:
        print(f'({node.op} ', end='')
        self.visit(node.expr)
        print(')', end='')

    def visit_Conditional(self, node: Conditional) -> None:
        self.indenting_print('if ', end='')
        self.visit(node.test)
        print(' {')
        self.indent()
        self.visit(node.true_pipeline)
        self.dedent()
        self.indenting_print('}', end='')
        if node.false_pipeline is not None:
            print(' else {')
            self.indent()
            self.visit(node.false_pipeline)
            self.dedent()
            self.indenting_print('}')
        else:
            print()

    def visit_Map(self, node: Map) -> None:
        self.visit(node.name)
        for arg in node.args:
            print(' ', end='')
            self.visit(arg)

    def visit_ColumnSelector(self, node: ColumnSelector) -> None:
        print('[', end='')
        self.visit(node.header)
        print(']', end='')

    def visit_Name(self, node: Name) -> None:
        print(node.data, end='')

    def visit_String(self, node: String) -> None:
        print(f'\'{node.data}\'', end='')

    def visit_Number(self, node: Number) -> None:
        print(node.data, end='')

    def visit_Pattern(self, node: Pattern) -> None:
        print(f'/{node.data}/', end='')

    def visit_Boolean(self, node: Boolean) -> None:
        print(f'{node.data}', end='')
