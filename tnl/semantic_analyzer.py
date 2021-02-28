import re

from typing import List
from typing import Optional

from tnl.ast import ASTNode
from tnl.ast import Map
from tnl.ast import Pattern
from tnl.ast_visitor import ASTVisitor
from tnl.token import Position


class SemanticError:
    def __init__(self, message: str, pos: Optional[Position] = None) -> None:
        self.message = message
        self.pos = pos

    def __str__(self) -> str:
        if self.pos is not None:
            return f'{self.message} at {self.pos}.'
        else:
            return f'{self.message}.'


def analyze(ast: ASTNode) -> List[SemanticError]:
    analyzer = SemanticAnalyzer(ast)
    errors = analyzer.analyze()
    return errors


class SemanticAnalyzer(ASTVisitor):
    def __init__(self, ast: ASTNode) -> None:
        self.ast = ast
        self.errors: List[SemanticError] = []

    def analyze(self) -> List[SemanticError]:
        self.errors = []
        self.visit(self.ast)
        return self.errors

    def visit_Map(self, node: Map) -> None:
        # TODO make sure format string is well formed
        pass

    def visit_Pattern(self, node: Pattern) -> None:
        try:
            node.compile()
        except re.error:
            error = SemanticError(f'Invalid regex pattern /{node.data}/')
            self.errors.append(error)
