"""
* String Utils
"""
# Standard Library Imports
from contextlib import suppress
from enum import Enum, EnumMeta
from functools import cached_property
from typing import Any

# Third Party Imports
import yarl

# Maps strings to boolean values
STR_BOOL_MAP = {
    '1': True,
    'y': True,
    't': True,
    'on': True,
    'yes': True,
    'true': True,
    '0': False,
    'n': False,
    'f': False,
    'no': False,
    'off': False,
    'false': False
}

"""
* String Util classes
"""


class StrEnumMeta(EnumMeta):
    """Metaclass for StrEnum."""

    def __contains__(cls, item: str) -> bool:
        return item in cls._value2member_map_


class StrEnum(str, Enum, metaclass=StrEnumMeta):
    """Enum where the value is always a string."""

    def __str__(self) -> str:
        return self.value

    @cached_property
    def value(self) -> str:
        return str(self._value_)

    @cached_property
    def Default(self) -> str:
        return "default"


class ConsoleMessages(StrEnum):
    error = "#a84747"
    warning = "#d4c53d"
    success = "#59d461"
    info = "#6bbcfa"


"""
* URL Util Classes
"""


class URLEnumMeta(EnumMeta):
    """Metaclass for StrEnum."""

    def __contains__(cls, item: yarl.URL) -> bool:
        return item in cls._value2member_map_


class URLEnum(Enum, metaclass=URLEnumMeta):
    """Enum where the value is always a URL object with an HTTPS scheme."""

    def __str__(self):
        return str(self.value)

    def __truediv__(self, value):
        return self.value / value

    def __getattr__(self, item: str) -> Any:
        """Access anything except _value_, value, and __contains__ from the URL object."""
        if item not in ['_value_', 'value', '__contains__']:
            return self.value.__getattribute__(item)
        return self.__getattribute__(item)


"""
* Util Funcs
"""


def str_to_bool(st: str) -> bool:
    """
    Converts a truthy string value to a bool. Conversion is case-insensitive.
    @param st: True values are y, yes, t, true, on and 1.
    False values are n, no, f, false, off and 0.
    @return: Adjacent boolean value.
    @raise: ValueError if string provided isn't a recognized truthy expression.
    """
    try:
        return STR_BOOL_MAP[st.lower()]
    except KeyError:
        raise ValueError(f"Couldn't discern boolean value of string '{st}'!")


def str_to_bool_safe(st: str, default: bool = False) -> bool:
    """Utility wrapper for str_to_bool, returns default if error is raised."""
    with suppress(Exception):
        return str_to_bool(st)
    return default
