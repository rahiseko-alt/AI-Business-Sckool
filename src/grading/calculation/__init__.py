"""決定論的な採点計算と ABCDE 変換。LLM は関与しない。

問題が1つでもあれば得点は作らず、見つかった問題をすべて返す。
"""

from grading.calculation.engine import CalcProblem, ComponentScore, ItemValue, SubjectResult, calculate

__all__ = ["CalcProblem", "ComponentScore", "ItemValue", "SubjectResult", "calculate"]
