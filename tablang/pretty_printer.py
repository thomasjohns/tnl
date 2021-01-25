from tablang.ast import ASTNode
from tablang.ast import Module
from tablang.ast import Transform
from tablang.ast import Test
from tablang.ast import AliasBlock
from tablang.ast import HeaderBlock
from tablang.ast import ValueBlock
from tablang.ast import AliasRule
from tablang.ast import HeaderRule
from tablang.ast import ValueRule
from tablang.ast import Pipeline
from tablang.ast import BinaryOp
from tablang.ast import UnaryOp
from tablang.ast import Conditional
from tablang.ast import Map
from tablang.ast import ColumnSelector
from tablang.ast import Name
from tablang.ast import String
from tablang.ast import Number
from tablang.ast import Pattern


def print_module(ast: Module, indent: int = 4) -> None:
    ast_printer = CodePrinter(indent)
    ast_printer.visit(ast)


class CodePrinter:
    def __init__(self, indent: int) -> None:
        self.indent = 4
        self.cur_indent = 0

    def visit(self, node: ASTNode) -> None:
        node_type = node.__class__.__name__
        node_visit = f'visit_{node_type}'
        getattr(self, node_visit)(node)

    def visit_Module(self, node: Module) -> None:
        # TODO
        pass

    def visit_Transform(self, node: Transform) -> None:
        # TODO
        pass

    def visit_Test(self, node: Test) -> None:
        # TODO
        pass

    def visit_AliasBlock(self, node: AliasBlock) -> None:
        # TODO
        pass

    def visit_HeaderBlock(self, node: HeaderBlock) -> None:
        # TODO
        pass

    def visit_ValueBlock(self, node: ValueBlock) -> None:
        # TODO
        pass

    def visit_AliasRule(self, node: AliasRule) -> None:
        # TODO
        pass

    def visit_HeaderRule(self, node: HeaderRule) -> None:
        # TODO
        pass

    def visit_ValueRule(self, node: ValueRule) -> None:
        # TODO
        pass

    def visit_Pipeline(self, node: Pipeline) -> None:
        # TODO
        pass

    def visit_BinaryOp(self, node: BinaryOp) -> None:
        # TODO
        pass

    def visit_UnaryOp(self, node: UnaryOp) -> None:
        # TODO
        pass

    def visit_Conditional(self, node: Conditional) -> None:
        # TODO
        pass

    def visit_Map(self, node: Map) -> None:
        # TODO
        pass

    def visit_ColumnSelector(self, node: ColumnSelector) -> None:
        # TODO
        pass

    def visit_Name(self, node: Name) -> None:
        # TODO
        pass

    def visit_String(self, node: String) -> None:
        # TODO
        pass

    def visit_Number(self, node: Number) -> None:
        # TODO
        pass

    def visit_Pattern(self, node: Pattern) -> None:
        # TODO
        pass
