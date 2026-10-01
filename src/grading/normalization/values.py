"""セルの値の解釈。数値以外の記号は、採点ルールが定めた markers に載っているものしか意味を持たない。"""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from grading.domain.enums import ValueKind
from grading.normalization.names import fold_width

_NUMBER = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")


@dataclass(frozen=True)
class ParsedValue:
    kind: ValueKind
    number: Decimal | None
    original: str | None


def parse_value(original: object, markers: Mapping[str, ValueKind]) -> ParsedValue:
    raw = None if original is None else str(original)
    if isinstance(original, bool):
        return ParsedValue(ValueKind.UNKNOWN, None, raw)
    if isinstance(original, (int, float, Decimal)):
        text = str(original)
    else:
        text = fold_width(raw or "").strip()
    if text == "":
        return ParsedValue(ValueKind.BLANK, None, raw)
    if _NUMBER.match(text):
        number = Decimal(text)
        return ParsedValue(ValueKind.ZERO if number == 0 else ValueKind.NUMBER, number, raw)
    normalized_markers = {fold_width(k).strip(): v for k, v in markers.items()}
    if text in normalized_markers:
        return ParsedValue(normalized_markers[text], None, raw)
    return ParsedValue(ValueKind.UNKNOWN, None, raw)
