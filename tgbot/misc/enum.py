from enum import EnumType, Enum
from typing import Generator


def two_enums_get_by_key(
        enum1: EnumType, enum2: EnumType
) -> Generator[Enum, None, None]:
    for key, value in enum1.__members__.items():
        yield getattr(enum2, key)
