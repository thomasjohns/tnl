from tablang.ast import ASTNode
from tablang.ast import Module


def print_module(ast: Module, indent: int = 4) -> None:
    ast_printer = ASTPrinter(indent)
    ast_printer.visit(ast)


class ASTPrinter:
    def __init__(self, indent: int) -> None:
        self.indent = 4
        self.cur_indent = 0

    def visit(self, node: ASTNode) -> None:
        pass
