"""氏名の正規化。吸収するのは空白と全角半角・大文字小文字の違いだけ。

字が違うもの（太郎/太朗）や読みの一致は扱わない。それは人が決める。
"""

import re
import unicodedata
from enum import StrEnum

_SPACES = re.compile(r"\s+")


class NameDiff(StrEnum):
    IDENTICAL = "IDENTICAL"
    FORMAT_ONLY = "FORMAT_ONLY"   # 空白・全角半角・大文字小文字のみ違う
    DIFFERENT = "DIFFERENT"


def normalize_token(value: str) -> str:
    """クラス名・メール等の比較用。全角半角と大文字小文字を揃え、前後の空白を除く。"""
    return unicodedata.normalize("NFKC", value).strip().upper()


def normalize_name(original: str) -> str:
    return _SPACES.sub("", normalize_token(original))


def compare_names(a: str, b: str) -> NameDiff:
    if a == b:
        return NameDiff.IDENTICAL
    if normalize_name(a) == normalize_name(b):
        return NameDiff.FORMAT_ONLY
    return NameDiff.DIFFERENT
