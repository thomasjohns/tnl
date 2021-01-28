from typing import Callable
from typing import List

import pandas as pd  # type: ignore

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


HeaderMap = Callable[[str], str]


def transform(ast: Module, df: pd.DataFrame) -> pd.DataFrame:
    vm = VM(df)
    vm.execute(ast)
    return vm.df


class VM:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

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
        # FIXME
        pass

    def visit_AliasRule(self, node: AliasRule) -> None:
        # TODO
        pass

    def visit_HeaderRule(self, node: HeaderRule) -> None:
        # TODO handle pattern later
        # TODO handle name later (look up in symbol table
        assert isinstance(node.header, String)
        from_str = node.header.data
        maps = self.visit_header_Pipeline(node.pipeline)
        to_str = from_str[:]
        for m in maps:
            to_str = m(to_str)
        self.df = self.df.rename(columns={from_str: to_str})

    def visit_ValueRule(self, node: ValueRule) -> None:
        # FIXME
        pass

    # TODO we may need the concept of a HeaderPipeline that does
    #      HeaderTransform's (Callable[str, str]) and a ValuePipeline
    #      that does pandas dataframe transforms
    #      (Callable[pd.DataFrame, pd.DataFrame]). We may also need
    #      HeaderMap's and ValueMap's etc.
    #      The different kinds of Pipelines could possibly share a lot of
    #      code, and maybe all of the pretty printing code.
    #
    #      Or setting a context could do it?
    #
    #      Or maybe visit_header_Map
    #               visit_value_Map
    #
    #      See aboce visit_Pipeline call in visit_HeaderRule.
    #      Maybe caller has all needed context?
    #
    #      Or are they always string tranforms, and the parent knows
    #      whether to apply to string or apply to pandas series using
    #      .apply?
    def visit_header_Pipeline(self, node: Pipeline) -> List[HeaderMap]:
        maps: List[HeaderMap] = []
        for operation in node.operations:
            # FIXME hardcode for now
            if isinstance(operation, String):
                m = lambda s: operation.data  # noqa: E731
                maps.append(m)
        return maps

    def visit_Pipeline(self, node: Pipeline) -> None:
        # FIXME maybe don't need this function
        pass

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
