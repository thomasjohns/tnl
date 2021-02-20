import pandas as pd  # type: ignore

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
from tnl.map_impls import MAP_VALUES_IMPL_REGISTRY
from tnl.map_impls import MAP_STRING_IMPL_REGISTRY


def transform(ast: Module, data: pd.DataFrame) -> pd.DataFrame:
    vm = VM(data)
    vm.execute(ast)
    return vm.data


class VM:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def execute(self, node: Module) -> None:
        self.visit(node)

    def visit(self, node: ASTNode) -> None:
        node_type = node.__class__.__name__
        node_visit = f'visit_{node_type}'
        getattr(self, node_visit)(node)

    def visit_Module(self, node: Module) -> None:
        for definition in node.definitions:
            self.visit(definition)

    def visit_Transform(self, node: Transform) -> None:
        # TODO for now ignore the `name`
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
        # TODO handle pattern later
        # TODO handle name later (look up in symbol table
        assert isinstance(node.header, String)
        from_str = node.header.data
        to_str = self.exec_string_pipeline(node.pipeline, from_str)
        self.data = self.data.rename(columns={from_str: to_str})

    def visit_ValueRule(self, node: ValueRule) -> None:
        # TODO handle pattern later
        # TODO handle name later (look up in symbol table
        assert isinstance(node.rvalue, ColumnSelector)
        # TODO: consider copy perf later
        # TODO: we may want to provide a way for user to learn that
        #       their rule didn't apply to any header
        if node.rvalue.header.data in self.data.columns:
            s_before = self.data[node.rvalue.header.data].copy()
            s_after = self.exec_values_pipeline(node.pipeline, s_before)
            self.data[node.rvalue.header.data] = s_after

    def exec_string_pipeline(self, node: Pipeline, s: str) -> str:
        for operation in node.operations:
            if isinstance(operation, String):
                s = operation.data
            elif isinstance(operation, Map):
                map_impl = MAP_STRING_IMPL_REGISTRY[operation.name.data]
                s = map_impl.map_string(s, *operation.args)  # type: ignore
            else:
                # FIXME
                assert 0, 'not implemented'
        return s

    def exec_values_pipeline(self, node: Pipeline, s: pd.Series) -> pd.Series:
        for operation in node.operations:
            if isinstance(operation, ColumnSelector):
                # TODO consider copy perf later
                s = self.data[operation.header].copy()
            elif isinstance(operation, String):
                s = pd.Series(operation.data for _ in range(len(self.data)))
            elif isinstance(operation, Number):
                s = pd.Series(operation.data for _ in range(len(self.data)))
            elif isinstance(operation, Map):
                map_impl = MAP_VALUES_IMPL_REGISTRY[operation.name.data]
                s = map_impl.map_values(s, *operation.args)  # type: ignore
            else:
                # FIXME
                assert 0, 'not implemented'
        return s

    def visit_Pipeline(self, node: Pipeline) -> None:
        assert 0, 'Failed to capture Pipeline in VM.'

    def visit_BinaryOp(self, node: BinaryOp) -> None:
        # FIXME
        pass

    def visit_UnaryOp(self, node: UnaryOp) -> None:
        # FIXME
        pass

    def visit_Conditional(self, node: Conditional) -> None:
        # FIXME
        pass

    def visit_Map(self, node: Map) -> None:
        # FIXME
        pass

    def visit_ColumnSelector(self, node: ColumnSelector) -> None:
        # FIXME
        pass

    def visit_Name(self, node: Name) -> None:
        # FIXME
        pass

    def visit_String(self, node: String) -> str:
        # FIXME
        pass

    def visit_Number(self, node: Number) -> None:
        # FIXME
        pass

    def visit_Pattern(self, node: Pattern) -> None:
        # TODO
        pass
