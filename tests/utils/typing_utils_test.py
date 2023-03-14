import dataclasses
import typing
from typing import Optional

from aws_assume_role.utils import typing_utils


@dataclasses.dataclass
class TypingExample:
    string_field: str
    null_field: Optional[str]
    numeric_optional_field: Optional[int]
    none_field: Optional[str] = None

def test_is_optional_method():

    hints = typing.get_type_hints(TypingExample.__new__(TypingExample).__class__)

    assert typing_utils.is_optional(hints['string_field']) == False
    assert typing_utils.is_optional(hints['null_field'])
    assert typing_utils.is_optional(hints['numeric_optional_field'])
    assert typing_utils.is_optional(hints['none_field'])
