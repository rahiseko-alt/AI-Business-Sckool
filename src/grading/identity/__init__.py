"""学生名寄せ。CONFIRMED / LIKELY / AMBIGUOUS / UNMATCHED。

CONFIRMED になるのは、学籍番号・メール・学校固有IDのいずれかで1人に決まり、
他の手がかりと食い違わないときだけ。氏名だけでは LIKELY 止まりで、確定には人の回答が要る。
"""

from grading.identity.resolver import IdentityClaim, Match, Student, resolve

__all__ = ["IdentityClaim", "Match", "Student", "resolve"]
