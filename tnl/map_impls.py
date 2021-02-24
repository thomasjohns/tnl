from typing import Callable
from typing import Dict
from typing import Protocol
from typing import Type

import pandas as pd  # type: ignore

from tnl.ast import Number
from tnl.ast import String


# TODO: is there a better way to represent types here?
#       we currently have some `# type: ignore` comments
#       elsewhere (at least in `tnl/vm.py`).


MAP_VALUES_IMPL_REGISTRY: Dict[str, Type['MapImpl']] = {}
MAP_STRING_IMPL_REGISTRY: Dict[str, Type['MapImpl']] = {}


def register_impl(map_name: str) -> Callable[['Type[MapImpl]'], None]:
    def wrapper(cls: 'Type[MapImpl]') -> None:
        if hasattr(cls, 'map_values'):
            MAP_VALUES_IMPL_REGISTRY[map_name] = cls
        if hasattr(cls, 'map_string'):
            MAP_STRING_IMPL_REGISTRY[map_name] = cls

    return wrapper


class MapImpl(Protocol):
    num_args: int


@register_impl(map_name='add')
class AddImpl(MapImpl):
    num_args = 1

    @staticmethod
    def map_values(s: pd.Series, *args: Number) -> pd.Series:
        return s + args[0].data

    # TODO: this is an example - add others later when we get
    #       to code generation
    # @staticmethod
    # def gen_map_values(series_ref: str, *args: Number) -> str:
    #     # think this will just generate code for right hand side
    #     return f'({series_ref} + 1)'


@register_impl(map_name='mult')
class MultImpl(MapImpl):
    num_args = 1

    @staticmethod
    def map_values(s: pd.Series, *args: Number) -> pd.Series:
        return s * args[0].data


@register_impl(map_name='replace')
class ReplaceImpl(MapImpl):
    num_args = 2

    @staticmethod
    def map_values(s: pd.Series, *args: String) -> pd.Series:
        return s.str.replace(args[0].data, args[1].data)

    @staticmethod
    def map_string(s: str, *args: String) -> str:
        return s.replace(args[0].data, args[1].data)


@register_impl(map_name='replace_last')
class ReplaceLastImpl(MapImpl):
    num_args = 2

    @staticmethod
    def _replace_last_in_str(s: str, from_str: str, to_str: str) -> str:
        l = s.rsplit(from_str, 1)
        return to_str.join(l)

    @classmethod
    def map_values(cls, s: pd.Series, *args: String) -> pd.Series:
        return s.apply(
            lambda x: cls._replace_last_in_str(x, args[0].data, args[1].data)
        )

    @classmethod
    def map_string(cls, s: str, *args: String) -> str:
        return cls._replace_last_in_str(s, args[0].data, args[1].data)


@register_impl(map_name='trim')
class TrimImpl(MapImpl):
    num_args = 0

    @staticmethod
    def map_values(s: pd.Series) -> pd.Series:
        return s.str.strip()

    @staticmethod
    def map_string(s: str) -> str:
        return s.strip()


@register_impl(map_name='slice')
class SliceImpl(MapImpl):
    num_args = 2

    @staticmethod
    def map_values(s: pd.Series, *args: Number) -> pd.Series:
        return s.str.slice(start=args[0].data, stop=args[1].data)

    @staticmethod
    def map_string(s: str, *args: Number) -> str:
        return s[args[0].data:args[1].data]


@register_impl(map_name='title')
class TitleImpl(MapImpl):
    num_args = 0

    @staticmethod
    def map_values(s: pd.Series) -> pd.Series:
        return s.str.title()

    @staticmethod
    def map_string(s: str) -> str:
        return s.title()


@register_impl(map_name='upper')
class UpperImpl(MapImpl):
    num_args = 0

    @staticmethod
    def map_values(s: pd.Series) -> pd.Series:
        return s.str.upper()

    @staticmethod
    def map_string(s: str) -> str:
        return s.upper()


MAP_IMPL_REGISTRY = {**MAP_VALUES_IMPL_REGISTRY, **MAP_STRING_IMPL_REGISTRY}
BUILT_IN_FUNCTIONS = set(MAP_IMPL_REGISTRY.keys())
