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
from tnl.ast import Boolean


class ASTVisitor:

    def visit(self, node: ASTNode) -> None:
        node_type = node.__class__.__name__
        node_visit = f'visit_{node_type}'
        getattr(self, node_visit)(node)

    def visit_Module(self, node: Module) -> None:
        for definition in node.definitions:
            self.visit(definition)

    def visit_Transform(self, node: Transform) -> None:
        for rule_block in node.rule_blocks:
            self.visit(rule_block)

    def visit_Test(self, node: Test) -> None:
        # TODO
        pass

    def visit_AliasBlock(self, node: AliasBlock) -> None:
        # TODO
        pass

    def visit_HeaderBlock(self, node: HeaderBlock) -> None:
        for header_rule in node.header_rules:
            self.visit(header_rule)

    def visit_ValueBlock(self, node: ValueBlock) -> None:
        for value_rule in node.value_rules:
            self.visit(value_rule)

    def visit_AliasRule(self, node: AliasRule) -> None:
        # TODO
        pass

    def visit_HeaderRule(self, node: HeaderRule) -> None:
        self.visit(node.header)
        self.visit(node.pipeline)

    def visit_ValueRule(self, node: ValueRule) -> None:
        self.visit(node.rvalue)
        self.visit(node.pipeline)

    def visit_Pipeline(self, node: Pipeline) -> None:
        for operation in node.operations:
            self.visit(operation)

    def visit_BinaryOp(self, node: BinaryOp) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: UnaryOp) -> None:
        self.visit(node.expr)

    def visit_Conditional(self, node: Conditional) -> None:
        self.visit(node.test)
        self.visit(node.true_pipeline)
        if node.false_pipeline is not None:
            self.visit(node.false_pipeline)

    def visit_Map(self, node: Map) -> None:
        self.visit(node.name)
        for arg in node.args:
            self.visit(arg)

    def visit_ColumnSelector(self, node: ColumnSelector) -> None:
        self.visit(node.header)

    def visit_Name(self, node: Name) -> None:
        pass

    def visit_String(self, node: String) -> None:
        pass

    def visit_Number(self, node: Number) -> None:
        pass

    def visit_Pattern(self, node: Pattern) -> None:
        pass

    def visit_Boolean(self, node: Boolean) -> None:
        pass
