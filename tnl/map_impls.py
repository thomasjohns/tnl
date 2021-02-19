from typing import Protocol

import pandas as pd  # type: ignore

from tnl.ast import Number
from tnl.ast import String


# FIXME: need a better way to represent types


class MapImpl(Protocol):
    num_args: int


class AddImpl(MapImpl):
    num_args = 1

    @staticmethod
    def map_values(s: pd.Series, *args: Number) -> pd.Series:
        return s + args[0].data


class MultImpl(MapImpl):
    num_args = 1

    @staticmethod
    def map_values(s: pd.Series, *args: Number) -> pd.Series:
        return s * args[0].data


class ReplaceImpl(MapImpl):
    num_args = 2

    @staticmethod
    def map_values(s: pd.Series, *args: String) -> pd.Series:
        return s.str.replace(args[0].data, args[1].data)

    @staticmethod
    def map_string(s: str, *args: String) -> str:
        return s.replace(args[0].data, args[1].data)


class TrimImpl(MapImpl):
    num_args = 0

    @staticmethod
    def map_values(s: pd.Series) -> pd.Series:
        return s.str.strip()

    @staticmethod
    def map_string(s: str) -> str:
        return s.strip()


MAP_IMPL_REGISTRY = {
    'add': AddImpl,
    'mult': MultImpl,
    # 'square': SquareImpl,  # FIXME
    'replace': ReplaceImpl,
    'trim': TrimImpl,
    # 'title': TitleImpl,  # FIXME
}

BUILT_IN_FUNCTIONS = set(MAP_IMPL_REGISTRY.keys())
