from tnl.ast import ASTNode
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


def print_module_ast(ast: Module, indent_spaces: int = 2) -> None:
    ast_printer = ASTPrinter(indent_spaces)
    ast_printer.visit(ast)


class ASTPrinter:
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

    def visit(self, node: ASTNode) -> None:
        node_type = node.__class__.__name__
        node_visit = f'visit_{node_type}'
        getattr(self, node_visit)(node)

    def visit_Module(self, node: Module) -> None:
        self.indenting_print('Module(')
        self.indent()
        if node.definitions:
            for definition in node.definitions:
                self.visit(definition)
                print(',')
            self.dedent()
            self.indenting_print(')')
        else:
            print(')')
            self.dedent()

    def visit_Transform(self, node: Transform) -> None:
        self.indenting_print('Transform(')
        self.indent()
        self.indenting_print('name=', end='')
        self.visit(node.name)
        print(',')
        if node.rule_blocks:
            self.indenting_print('rule_blocks=[')
            self.indent()
            for rule_block in node.rule_blocks:
                self.visit(rule_block)
            self.dedent()
            self.indenting_print('],')
        else:
            self.indenting_print('rule_blocks=[],')
        self.dedent()
        self.indenting_print(')', end='')

    def visit_Test(self, node: Test) -> None:
        # TODO
        pass

    def visit_AliasBlock(self, node: AliasBlock) -> None:
        # TODO
        pass

    def visit_HeaderBlock(self, node: HeaderBlock) -> None:
        self.indenting_print('HeaderBlock(')
        self.indent()
        self.indenting_print('header_rules=[', end='')
        if node.header_rules:
            print()
            self.indent()
            for header_rule in node.header_rules:
                self.visit(header_rule)
            self.dedent()
            self.indenting_print('],')
        else:
            print('],')
        self.dedent()
        self.indenting_print('),')

    def visit_ValueBlock(self, node: ValueBlock) -> None:
        self.indenting_print('ValueBlock(')
        self.indent()
        self.indenting_print('value_rules=[', end='')
        if node.value_rules:
            print()
            self.indent()
            for value_rule in node.value_rules:
                self.visit(value_rule)
            self.dedent()
            self.indenting_print('],')
        else:
            print('],')
        self.dedent()
        self.indenting_print(')')

    def visit_AliasRule(self, node: AliasRule) -> None:
        # TODO
        pass

    def visit_HeaderRule(self, node: HeaderRule) -> None:
        self.indenting_print('HeaderRule(')
        self.indent()
        self.indenting_print('header=', end='')
        self.visit(node.header)
        print(',')
        self.indenting_print('pipeline=', end='')
        self.visit(node.pipeline)
        print(',')
        self.dedent()
        self.indenting_print('),')

    def visit_ValueRule(self, node: ValueRule) -> None:
        self.indenting_print('ValueRule(')
        self.indent()
        self.indenting_print('rvalue=', end='')
        self.visit(node.rvalue)
        print(',')
        self.indenting_print('pipeline=', end='')
        self.visit(node.pipeline)
        print(',')
        self.dedent()
        self.indenting_print('),')

    def visit_Pipeline(self, node: Pipeline) -> None:
        print('Pipeline(')
        self.indent()
        self.indenting_print('operations=[', end='')
        if node.operations:
            print()
            self.indent()
            for operation in node.operations:
                self.indenting_print(end='')
                self.visit(operation)
                print(',')
            self.dedent()
            self.indenting_print('],')
        else:
            print('],')
        self.dedent()
        self.indenting_print(')', end='')

    def visit_BinaryOp(self, node: BinaryOp) -> None:
        self.indenting_print('BinaryOp(')
        self.indent()
        self.indenting_print('left=', end='')
        self.visit(node.left)
        print(',')
        self.indenting_print(f'op={node.op},')
        self.indenting_print('right=', end='')
        self.visit(node.right)
        print(',')
        self.dedent()
        self.indenting_print(')')

    def visit_UnaryOp(self, node: UnaryOp) -> None:
        self.indenting_print('UnaryOp(')
        self.indent()
        self.indenting_print(f'op={node.op},')
        self.indenting_print('expr=', end='')
        self.visit(node.expr)
        print(',')
        self.dedent()
        self.indenting_print(')')

    def visit_Conditional(self, node: Conditional) -> None:
        self.indenting_print('Conditional(')
        self.indent()
        self.indenting_print('test=', end='')
        self.visit(node.test)
        print(',')
        self.indenting_print('true_pipeline=', end='')
        self.visit(node.true_pipeline)
        print(',')
        self.indenting_print('false_pipeline=', end='')
        if node.false_pipeline is not None:
            self.visit(node.false_pipeline)
        else:
            print('None', end='')
        print(',')
        self.dedent()
        self.indenting_print(')')

    def visit_Map(self, node: Map) -> None:
        print('Map(')
        self.indent()
        self.indenting_print('name=', end='')
        self.visit(node.name)
        print(',')
        self.indenting_print('args=[', end='')
        if node.args:
            print()
            self.indent()
            for arg in node.args:
                self.indenting_print(end='')
                self.visit(arg)
                print(',')
            self.dedent()
            self.indenting_print('],')
        else:
            print('],')
        self.dedent()
        self.indenting_print(')', end='')

    def visit_ColumnSelector(self, node: ColumnSelector) -> None:
        print('ColumnSelector(header=', end='')
        self.visit(node.header)
        print(')', end='')

    def visit_Name(self, node: Name) -> None:
        print(f'Name(data=\'{node.data}\')', end='')

    def visit_String(self, node: String) -> None:
        print(f'String(data=\'{node.data}\')', end='')

    def visit_Number(self, node: Number) -> None:
        print(f'Number(data=\'{node.data}\')', end='')

    def visit_Pattern(self, node: Pattern) -> None:
        # TODO
        pass
