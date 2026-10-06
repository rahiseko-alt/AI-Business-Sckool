"""最終出力。BLOCKED・欠損・検算の食い違いが1件でも残る場合は完成版を出さない。"""

from grading.export.gate import FinalizationReport, check_finalizable
from grading.export.provenance import provenance

__all__ = ["FinalizationReport", "check_finalizable", "provenance"]
