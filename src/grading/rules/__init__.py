"""科目ごとの Rule Master（配点・満点・ABCDE基準・記号の意味・欠席/未提出の扱い）。

欠けている項目は推測で埋めず RuleError にする。端数処理（丸め）は持たない。別科目のルールは参照できない。
"""

from grading.rules.master import Component, Policy, RuleBook, RuleError, SubjectRule

__all__ = ["Component", "Policy", "RuleBook", "RuleError", "SubjectRule"]
