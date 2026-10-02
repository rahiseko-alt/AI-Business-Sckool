"""通知表（1人1枚、印刷用 HTML。PDF にして一括印刷する）。

ひな形は利用者の Google スプレッドシート「AIビジネス専門学校_通知表」。科目の並び・形態・単位はそこから写した。
利用者の回答（2026-10-02）:
- 学生が受けていない科目（国際の総合ビジネス概論・総合の国際社会・異文化理解）は行ごと載せない
- 前期の科目の下に「前期計」の行を置く（ひな形は「後期」の行に前期の合計が出ていた）
- 発行日は印刷する日。上の「発行日」欄と下の「発行年月日」は同じ日
- 出席時数＝授業時数−欠席−遅刻÷3（成績の出席率と同じ数え方）。授業時数は受けている全科目の授業数（×を除く）の合計
- 点数は小数第1位まで（第2位を四捨五入）。評定は成績表のまま
点数・評定・氏名は成績表（AI計算版）の値、出席は同じブックに写した出席簿から数える。
分からないもの（対応の無い科目・評定がABCDE以外・出席が数えられない）は推測せず止める。
"""

import datetime as dt
import html
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

from grading.export.linked import describe
from grading.importing.attendance import SubjectCount, unify_subject

# （通知表の科目名, 形態, 単位, 成績表の科目名）。ひな形の前期13行の順
TEMPLATE = (
    ("ビジネス日本語Ⅰ", "講義", 2, "ビジネス日本語"),
    ("マーケティングⅠ", "講義", 2, "マーケティング"),
    ("AI演習（実践）Ⅰ", "講義", 3, "AI演習（実践）"),
    ("ビジネスプレゼンテーションⅠ", "講義", 3, "ビジネスプレゼンテーション"),
    ("ビジネス演習（理論）Ⅰ", "講義", 3, "ビジネス演習（理論）"),
    ("就職指導キャリアガイダンス", "講義", 2, "就職指導キャリアガイダンス"),
    ("日本語能力強化演習", "講義", 3, "日本語能力強化演習"),
    ("ビジネス演習（実践）Ⅰ", "講義", 2, "ビジネス演習（実践）"),
    ("ビジネス情報リテラシー", "講義", 2, "ビジネス情報リテラシー"),
    ("総合ビジネス概論Ⅰ", "講義", 2, "総合ビジネス概論"),
    ("国際社会・異文化理解Ⅰ", "講義", 2, "国際理解"),
    ("日本語運用力強化演習", "講義", 1, "日本語運用力強化演習"),
    ("キャリア形成演習Ⅰ", "講義", 1, "キャリア形成演習"),
)
# 出席簿の科目名（揃えた後）→ 成績表の科目名（揃えた後）。名前が同じものは書かない
REGISTER_NAMES = {"AI演習": unify_subject("AI演習（実践）"), "国際社会I:異文化理解": "国際理解"}
GRADES = ("A", "B", "C", "D", "E")


class ReportCardError(Exception):
    """通知表を作れない（推測が要る）とき。"""


@dataclass(frozen=True)
class Line:
    name: str
    kind: str
    credits: int
    score: float
    grade: str

    @property
    def earned(self) -> int | None:
        return None if self.grade == "E" else self.credits


@dataclass(frozen=True)
class Card:
    dept: str
    student_id: str
    name_en: str
    name_ja: str
    lines: tuple[Line, ...]
    hours: int              # 授業時数
    attended: Fraction      # 出席時数（丸めない）

    @property
    def credits_set(self) -> int:
        return sum(l.credits for l in self.lines)

    @property
    def credits_earned(self) -> int:
        return sum(l.earned or 0 for l in self.lines)

    @property
    def rate(self) -> Fraction:
        return self.attended / self.hours


def _clean(text: object) -> str:
    return " ".join(str(text or "").replace("　", " ").split())


def read_cards(ws, dept: str, counts: Mapping[tuple[str, str], SubjectCount]) -> list[Card]:
    """ws: AI計算版のシート（値で読んだもの）。counts: その学科の出席簿を subject_counts で数えたもの。"""
    template = {unify_subject(g): (n, k, c) for n, k, c, g in TEMPLATE}
    order = [unify_subject(g) for *_, g in TEMPLATE]
    d = describe(ws, dept, dept, {})
    unknown = [s.name for s in d.subjects if unify_subject(s.name) not in template]
    if unknown:
        raise ReportCardError(f"{dept}: 通知表のひな形に無い科目 {unknown}")
    per_student: dict[str, dict[str, list]] = {}
    for (sid, subject), c in counts.items():
        name = REGISTER_NAMES.get(subject, subject)
        per_student.setdefault(sid, {}).setdefault(name, []).append(c)
    cards = []
    for r in d.rows:
        sid = str(ws.cell(r, 2).value).strip()
        lines, hours, attended = [], 0, Fraction(0)
        for s in sorted(d.subjects, key=lambda s: order.index(unify_subject(s.name))):
            taken = [ws.cell(r, c).value for c in s.items if isinstance(ws.cell(r, c).value, (int, float))]
            if not taken:
                continue
            grade, score = ws.cell(r, s.grade).value, ws.cell(r, s.total).value
            if grade not in GRADES or not isinstance(score, (int, float)):
                raise ReportCardError(f"{dept} {sid} {s.name}: 評定 {grade!r}・点数 {score!r} を読めない")
            found = per_student.get(sid, {}).get(unify_subject(s.name), [])
            if len(found) != 1:
                raise ReportCardError(f"{dept} {sid} {s.name}: 出席簿で授業を数えられない（{len(found)}件）")
            c = found[0]
            hours += c.sessions
            attended += c.sessions - c.absent - Fraction(c.late, 3)
            name, kind, credits = template[unify_subject(s.name)]
            lines.append(Line(name, kind, credits, score, grade))
        if not lines:
            raise ReportCardError(f"{dept} {sid}: 受けている科目が1つも無い")
        cards.append(Card(dept, sid, _clean(ws.cell(r, 3).value), _clean(ws.cell(r, 4).value), tuple(lines), hours, attended))
    return cards


# ---------- 表示 ----------

def _one_decimal(value) -> str:
    """小数第1位まで（第2位を四捨五入）。整数はそのまま。"""
    if isinstance(value, Fraction):
        d = Decimal(value.numerator) / Decimal(value.denominator)
    else:
        d = Decimal(repr(float(value)))
    d = d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return str(d.to_integral_value()) if d == d.to_integral_value() else str(d)


def _date(d: dt.date) -> str:
    return f"{d.year}年{d.month}月{d.day}日"


def _e(text: object) -> str:
    return html.escape("" if text is None else str(text))


CSS = """
@page { size: A4 portrait; margin: 12mm 12mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "IPAGothic", "Noto Sans JP", "Hiragino Sans", "Yu Gothic", sans-serif; color: #000; background: #fff;
       font-size: 9.5pt; }
.page { width: 186mm; margin: 0 auto; page-break-after: always; position: relative; }
.page:last-child { page-break-after: auto; }
.top { display: flex; justify-content: space-between; align-items: flex-start; }
.school { font-size: 10pt; line-height: 1.5; }
.school b { font-size: 12pt; }
.notice { font-size: 9pt; border: 1px solid #000; padding: 1mm 3mm; }
h1 { text-align: center; font-size: 18pt; letter-spacing: 1em; margin: 3mm 0 3mm; }
h2 { font-size: 10.5pt; margin: 3mm 0 1.2mm; border-left: 3px solid #000; padding-left: 2mm; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 0.6pt solid #000; padding: 0.4mm 1.5mm; height: 4.9mm; }
th { background: #e8e8e8; font-weight: normal; white-space: nowrap; }
td.n { text-align: right; font-variant-numeric: tabular-nums; }
td.c { text-align: center; }
.profile th { width: 17mm; }
.two { display: flex; gap: 4mm; }
.two > div { flex: 1; min-width: 0; }
.year { text-align: left; background: #fff; font-weight: bold; border: none; padding-left: 0; }
.term td { background: #f4f4f4; font-weight: bold; }
.sum td { font-weight: bold; }
.subject { white-space: nowrap; font-size: 8.5pt; }
.remarks { border: 0.6pt solid #000; padding: 1.5mm 2mm; min-height: 10mm; }
.foot { display: flex; justify-content: space-between; margin-top: 5mm; }
.foot .right { text-align: right; line-height: 1.7; }
/* E の科目: 白黒印刷でも分かるよう黒地に白文字 */
.fail td { background: #000; color: #fff; }
/* スタンプ: 枠と文字だけの朱色（中は透明）。まっすぐ押し、記入済みの内容には重ねない */
.stamp { position: absolute; border: 2.6mm double rgba(200, 16, 16, .72); border-radius: 1.2mm;
         color: rgba(200, 16, 16, .72); font-weight: bold; white-space: nowrap; line-height: 1.15; pointer-events: none; }
/* 位置1: まだ空欄の後期の欄（成績欄の中央） */
.stamp.body { left: 50%; top: 181mm; transform: translate(-50%, -50%); font-size: 52pt; letter-spacing: .12em; padding: 2mm 9mm; }
.stamp.body.long { font-size: 40pt; letter-spacing: .02em; padding: 2mm 6mm; }
/* 位置2: 題名「通知表」の右（題名と学生欄のあいだの余白） */
.stamp.title { right: 0; top: 8.5mm; font-size: 25pt; letter-spacing: .1em; padding: 0.3mm 4mm; border-width: 2mm; }
.stamp.title.long { font-size: 17pt; letter-spacing: .02em; padding: 1mm 3mm; }
"""

ROWS_PER_TERM = 13


def _attendance(card: Card | None) -> str:
    def row(label, hours, attended, bold=False):
        cls = ' class="sum"' if bold else ""
        if hours is None:
            return f"<tr{cls}><th>{label}</th><td></td><td></td><td></td></tr>"
        return (f'<tr{cls}><th>{label}</th><td class="n">{hours}</td><td class="n">{_one_decimal(attended)}</td>'
                f'<td class="n">{_one_decimal(attended / hours * 100)}%</td></tr>')
    head = "<tr><th>区分</th><th>授業時数</th><th>出席時数</th><th>出席率</th></tr>"
    if card is None:
        body = row("前期", None, None) + row("後期", None, None) + row("年間合計", None, None, True)
    else:
        body = (row("前期", card.hours, card.attended) + row("後期", None, None)
                + row("年間合計", card.hours, card.attended, True))
    return f"<table>{head}{body}</table>"


def _grades(card: Card | None, year: str, black_e: bool = False) -> str:
    head = "<tr><th>授業科目</th><th>点数</th><th>評定</th><th>形態</th><th>設定</th><th>取得</th></tr>"
    blank = "<tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>"
    out = [f"<table>{head}", '<tr class="term"><td colspan="6">前期</td></tr>']
    lines = card.lines if card else ()
    for l in lines:
        tr = '<tr class="fail">' if black_e and l.grade == "E" else "<tr>"
        out.append(f'{tr}<td class="subject">{_e(l.name)}</td><td class="n">{_one_decimal(l.score)}</td>'
                   f'<td class="c">{_e(l.grade)}</td><td class="c">{_e(l.kind)}</td><td class="n">{l.credits}</td>'
                   f'<td class="n">{"－" if l.earned is None else l.earned}</td></tr>')
    out += [blank] * (ROWS_PER_TERM - len(lines) - 1)
    if card:
        out.append(f'<tr class="sum"><td>前期計</td><td></td><td></td><td></td><td class="n">{card.credits_set}</td>'
                   f'<td class="n">{card.credits_earned}</td></tr>')
    else:
        out.append('<tr class="sum"><td>前期計</td><td></td><td></td><td></td><td></td><td></td></tr>')
    out.append('<tr class="term"><td colspan="6">後期</td></tr>')
    out += [blank] * (ROWS_PER_TERM - 1)
    total = f'<td class="n">{card.credits_set}</td><td class="n">{card.credits_earned}</td>' if card else "<td></td><td></td>"
    out.append(f'<tr class="sum"><td colspan="4">{year} 合計取得単位数</td>{total}</tr></table>')
    return "".join(out)


def _page(card: Card, issued: dt.date, black_e: bool = False, stamp: str | None = None, place: str = "body") -> str:
    mark = ""
    if stamp and any(l.grade == "E" for l in card.lines):
        size = " long" if len(stamp) > 6 else ""
        mark = f'<div class="stamp {place}{size}">{_e(stamp)}</div>'
    return f"""<section class="page">{mark}
<div class="top"><div class="school">学校法人海鵬学園<br><b>AIビジネス専門学校</b></div>
<div class="notice">この書類は成績証明書ではありません</div></div>
<h1>通知表</h1>
<table class="profile">
<tr><th>学科</th><td>{_e(card.dept)}</td><th>日本語氏名</th><td>{_e(card.name_ja)}</td><th>学籍番号</th><td>{_e(card.student_id)}</td></tr>
<tr><th>学年</th><td>1年</td><th>英語氏名</th><td>{_e(card.name_en)}</td><th>発行日</th><td>{_date(issued)}</td></tr>
<tr><th>対象期間</th><td colspan="5">2026年度 前期</td></tr>
</table>
<h2>出席（1年・2年／前期・後期）</h2>
<div class="two"><div><table><tr><th class="year">1年（2026年度）</th></tr></table>{_attendance(card)}</div>
<div><table><tr><th class="year">2年（2027年度）</th></tr></table>{_attendance(None)}</div></div>
<h2>成績・単位</h2>
<div class="two"><div><table><tr><th class="year">1年</th></tr></table>{_grades(card, "1年", black_e)}</div>
<div><table><tr><th class="year">2年</th></tr></table>{_grades(None, "2年")}</div></div>
<h2>特記事項</h2>
<div class="remarks">該当なし</div>
<div class="foot"><div>記載の期間における出席及び成績は、上記のとおりです。</div>
<div class="right">発行年月日　{_date(issued)}<br>学校法人海鵬学園　AIビジネス専門学校</div></div>
</section>"""


def render_html(cards: Sequence[Card], issued: dt.date, black_e: bool = False, stamp: str | None = None,
                place: str = "body") -> str:
    """black_e: E の科目の行を黒地に白文字にする。stamp: E のある学生のページに押すスタンプの文字。
    place: スタンプの位置。"body"＝空欄の後期の欄、"title"＝題名「通知表」の右。"""
    if place not in ("body", "title"):
        raise ValueError(place)
    pages = "\n".join(_page(c, issued, black_e, stamp, place) for c in cards)
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>通知表 2026年度前期</title>'
            f"<style>{CSS}</style></head><body>\n{pages}\n</body></html>")
