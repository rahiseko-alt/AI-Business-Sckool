"""氏名の正規化。吸収するのは空白と全角半角・大文字小文字の違いだけ。

字が違うもの（太郎/太朗、互換漢字の神/神）や読みの一致は扱わない。それは人が決める。
"""

import re
import unicodedata
from enum import StrEnum

_SPACES = re.compile(r"\s+")


class NameDiff(StrEnum):
    IDENTICAL = "IDENTICAL"
    FORMAT_ONLY = "FORMAT_ONLY"   # 空白・全角半角・大文字小文字のみ違う
    DIFFERENT = "DIFFERENT"


def _is_width_variant(ch: str) -> bool:
    return "！" <= ch <= "～" or "｡" <= ch <= "ﾟ" or ch == "　"


def fold_width(value: str) -> str:
    """全角英数記号・半角カナ・全角空白だけを揃える。漢字には触れない。"""
    # 連続する全角半角文字ごとに NFKC をかける（ｶﾞ→ガ のように濁点ごと畳むため）。
    # 文字列全体に NFC/NFKC をかけると互換漢字（神→神）まで畳まれるので避ける。
    out, run = [], []
    for ch in value + "\0":
        if _is_width_variant(ch):
            run.append(ch)
            continue
        if run:
            out.append(unicodedata.normalize("NFKC", "".join(run)))
            run = []
        out.append(ch)
    return "".join(out)[:-1]


def normalize_token(value: str) -> str:
    """クラス名などの比較用。全角半角と大文字小文字を揃え、前後の空白を除く。"""
    return fold_width(value).strip().upper()


def normalize_name(original: str) -> str:
    return _SPACES.sub("", normalize_token(original))


def compare_names(a: str, b: str) -> NameDiff:
    if a == b:
        return NameDiff.IDENTICAL
    if normalize_name(a) == normalize_name(b):
        return NameDiff.FORMAT_ONLY
    return NameDiff.DIFFERENT
