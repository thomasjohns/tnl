from typing import Protocol

import pandas as pd  # type: ignore

from tnl.ast import Number
from tnl.ast import String


# TODO: is there a better way to represent types here?
#       we currently have some `# type: ignore` comments
#       elsewhere (at least in `tnl/vm.py`).


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


MAP_VALUES_IMPL_REGISTRY = {
    'add': AddImpl,
    'mult': MultImpl,
    'replace': ReplaceImpl,
    'trim': TrimImpl,
}
MAP_STRING_IMPL_REGISTRY = {
    'replace': ReplaceImpl,
    'trim': TrimImpl,
}
MAP_IMPL_REGISTRY = {**MAP_VALUES_IMPL_REGISTRY, **MAP_STRING_IMPL_REGISTRY}

BUILT_IN_FUNCTIONS = set(MAP_IMPL_REGISTRY.keys())
