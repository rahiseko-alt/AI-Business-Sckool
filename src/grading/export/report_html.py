"""紙やスマートフォンで読む成績資料（HTML。PDF にもできる）。

Excel 版と同じ内容を、1人1科目ずつ縦に並べる。計算式はふつうの書き方で書き、電卓で確かめられるようにする。
「検算」欄は、計算エンジンとは別の手順で元の値から計算し直した結果。
"""

import html
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from grading.domain.enums import DataStatus
from grading.export.gate import FinalizationReport
from grading.export.workbook import KIND_LABEL, STATUS_LABEL, Entry, EvidenceRef, Notice, _name, _plain, _short, _usage, problem_lines
from grading.identity import Student
from grading.rules import Policy, RuleBook
from grading.validation import Matrix, recheck

CSS = """
:root { --ink:#1f2328; --muted:#59636e; --line:#d0d7de; --ok:#e2efda; --warn:#fff2cc; --stop:#f8cbad; --head:#dde7f3; }
* { box-sizing:border-box; }
body { font-family:"Noto Sans CJK JP","Hiragino Sans","Yu Gothic","WenQuanYi Zen Hei",sans-serif; color:var(--ink);
       background:#fff; margin:0; padding:24px 16px; line-height:1.6; font-size:14px; }
main { max-width:900px; margin:0 auto; }
h1 { font-size:22px; margin:0 0 12px; } h2 { font-size:18px; margin:32px 0 8px; border-bottom:2px solid var(--line); }
h3 { font-size:15px; margin:0; }
.banner { padding:12px 16px; border-radius:6px; font-weight:bold; }
.banner.ok { background:var(--ok); } .banner.stop { background:var(--stop); }
.banner ul { margin:6px 0 0; font-weight:normal; }
table { border-collapse:collapse; width:100%; margin:6px 0; }
th, td { border:1px solid var(--line); padding:4px 6px; text-align:left; vertical-align:top; }
th { background:var(--head); white-space:nowrap; }
td.num { text-align:right; font-variant-numeric:tabular-nums; }
.tag { display:inline-block; padding:0 6px; border-radius:4px; font-size:12px; }
.s-ok { background:var(--ok); } .s-warn { background:var(--warn); } .s-stop { background:var(--stop); }
.card { border:1px solid var(--line); border-radius:6px; padding:12px; margin:14px 0; page-break-inside:avoid; }
.card.warn { border-left:6px solid #e0b400; } .card.stop { border-left:6px solid #d9534f; } .card.ok { border-left:6px solid #5a9e3a; }
.calc { margin:8px 0 0; padding:8px 10px; background:#f6f8fa; border-radius:4px; }
.calc div { margin:2px 0; } .muted { color:var(--muted); font-size:12px; }
.table-wrap { overflow-x:auto; }
@media print { body { padding:0; font-size:11px; } h2 { page-break-after:avoid; } }
"""


def _e(text: object) -> str:
    return html.escape("" if text is None else str(text))


def _status_tag(status: DataStatus | None) -> str:
    if status is None:
        return '<span class="tag s-stop">停止</span>'
    cls = {DataStatus.CONFIRMED: "s-ok", DataStatus.WARNING: "s-warn"}.get(status, "s-stop")
    return f'<span class="tag {cls}">{STATUS_LABEL[status]}</span>'


def write_html_report(
    path: str | Path,
    *,
    students: Mapping[str, Student],
    rules: RuleBook,
    entries: Sequence[Entry],
    matrix: Matrix,
    report: FinalizationReport,
    locate: Callable[[int | str], EvidenceRef],
    evidence_owner: Callable[[int | str], str | None],
    notices: Sequence[Notice] = (),
    title: str = "成績資料",
) -> Path:
    out: list[str] = [f'<!doctype html><html lang="ja"><head><meta charset="utf-8">'
                      f'<meta name="viewport" content="width=device-width, initial-scale=1">'
                      f"<title>{_e(title)}</title><style>{CSS}</style></head><body><main>"]
    out.append(f"<h1>{_e(title)}</h1>")
    if report.can_finalize:
        out.append('<div class="banner ok">完成：止める理由はありません。</div>')
    else:
        items = "".join(f"<li>{_e(r)}</li>" for r in report.reasons)
        out.append(f'<div class="banner stop">未完成：次の理由が解消するまで、成績として使わないでください。<ul>{items}</ul></div>')
    out.append('<p class="muted">点数は丸めていません。割り切れない値は分数で示しています。小数点の最終調整は人が行ってください。</p>')

    out += _notices(students, entries, notices)
    out += _grades(students, entries)
    out += _matrix(students, matrix)
    out.append("<h2>内訳と根拠（1人1科目ずつ）</h2>")
    out.append('<p class="muted">元の値が根拠の資料・セルと同じかを確かめ、計算式を電卓でたどれば検算できます。'
               "「検算」欄は、システムが別の手順で元の値から計算し直した結果です。</p>")
    for e in entries:
        out += _card(students, rules, e, locate, evidence_owner)
    out += _rules(rules)
    out.append("</main></body></html>")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    return path


def _notices(students, entries, notices) -> list[str]:
    rows = [(n.level, n.student_key, n.subject, n.text) for n in notices]
    for e in entries:
        rows += [("停止", e.student_key, e.subject, line) for line in problem_lines(e)]
        if e.result:
            rows += [("要確認", e.student_key, e.subject, n) for n in e.result.notes]
    rows.sort(key=lambda r: r[0] != "停止")
    out = ["<h2>確認事項</h2>"]
    if not rows:
        return out + ["<p>確認事項はありません。</p>"]
    out.append('<div class="table-wrap"><table><tr><th>区分</th><th>学生</th><th>科目</th><th>内容</th></tr>')
    for level, key, subject, text in rows:
        number, name, _ = _name(students, key) if key else ("", "", "")
        cls = "s-stop" if level == "停止" else "s-warn"
        out.append(f'<tr><td><span class="tag {cls}">{_e(level)}</span></td><td>{_e(number)} {_e(name)}</td>'
                   f"<td>{_e(subject or '')}</td><td>{_e(text)}</td></tr>")
    return out + ["</table></div>"]


def _grades(students, entries) -> list[str]:
    out = ["<h2>成績表</h2>", '<div class="table-wrap"><table><tr><th>学籍番号</th><th>氏名</th><th>クラス</th>'
           "<th>科目</th><th>合計</th><th>評価</th><th>状態</th></tr>"]
    for e in entries:
        number, name, cls = _name(students, e.student_key)
        total = _plain(e.result.total) if e.result else "—"
        grade = e.result.grade if e.result else "—"
        out.append(f"<tr><td>{_e(number)}</td><td>{_e(name)}</td><td>{_e(cls)}</td><td>{_e(e.subject)}</td>"
                   f'<td class="num">{_e(total)}</td><td>{_e(grade)}</td>'
                   f"<td>{_status_tag(e.result.status if e.result else None)}</td></tr>")
    return out + ["</table></div>"]


def _matrix(students, matrix: Matrix) -> list[str]:
    out = ["<h2>完全性（学生×科目）</h2>",
           '<p class="muted">OK＝確定 / OK(要確認) / ??＝止まっている / NG＝データなし / —＝履修なし</p>',
           '<div class="table-wrap"><table><tr><th>学生</th>' + "".join(f"<th>{_e(s)}</th>" for s in matrix.subjects) + "</tr>"]
    fills = {"OK": "s-ok", "OK(要確認)": "s-warn", "??": "s-stop", "NG": "s-stop"}
    for key in matrix.students:
        number, name, _ = _name(students, key)
        cells = "".join(f'<td><span class="tag {fills.get(matrix.cells[key][s].value, "")}">'
                        f"{_e(matrix.cells[key][s].value)}</span></td>" for s in matrix.subjects)
        out.append(f"<tr><td>{_e(number)} {_e(name)}</td>{cells}</tr>")
    return out + ["</table></div>"]


def _card(students, rules: RuleBook, e: Entry, locate, evidence_owner) -> list[str]:
    number, name, cls = _name(students, e.student_key)
    state = e.result.status if e.result else None
    kind = {DataStatus.CONFIRMED: "ok", DataStatus.WARNING: "warn"}.get(state, "stop")
    out = [f'<section class="card {kind}"><h3>{_e(e.subject)}　{_e(number)} {_e(name)}（{_e(cls)}）　{_status_tag(state)}</h3>']
    try:
        rule = rules.get(e.subject)
    except KeyError:
        return out + ["<p>この科目の採点ルールがありません。計算していません。</p></section>"]
    by_item = {v.item: v for v in e.values}
    out.append('<div class="table-wrap"><table><tr><th>評価項目</th><th>項目</th><th>元の値</th><th>扱い</th>'
               "<th>使う点 / 満点</th><th>根拠（資料 / シート / セル）</th></tr>")
    for comp in rule.components:
        for item in comp.items:
            v = by_item.get(item)
            cap = rule.max_scores[item]
            if v is None:
                out.append(f"<tr><td>{_e(comp.name)}</td><td>{_e(item)}</td><td>—</td>"
                           '<td><span class="tag s-stop">値がありません</span></td><td></td><td></td></tr>')
                continue
            use, how = _usage(rule, v, cap)
            used = "—" if use == "stop" else ("除外" if use is None else f"{_plain(use)} / {_plain(cap)}")
            how_html = f'<span class="tag s-stop">{_e(how)}</span>' if use == "stop" else _e(how)
            ref = locate(v.evidence_id)
            original = v.value.original if v.value.original not in (None, "") else "（空欄）"
            out.append(f"<tr><td>{_e(comp.name)}</td><td>{_e(item)}</td><td>{_e(original)}"
                       f'<div class="muted">{_e(KIND_LABEL[v.value.kind])}</div></td><td>{how_html}</td>'
                       f'<td class="num">{_e(used)}</td>'
                       f"<td>{_e(ref.file_name)} / {_e(ref.sheet_name or '')} / {_e(ref.cell or '')}</td></tr>")
    out.append("</table></div>")

    if e.result is None:
        reasons = "".join(f"<li>{_e(line)}</li>" for line in problem_lines(e))
        return out + [f'<div class="calc"><b>計算していません。</b><ul>{reasons}</ul></div></section>']

    r = e.result
    lines = []
    for comp, score in zip(rule.components, r.components):
        pts, caps = [], []
        for item in comp.items:
            use, _ = _usage(rule, by_item[item], rule.max_scores[item])
            if use is not None:
                pts.append(_plain(use))
                caps.append(_plain(rule.max_scores[item]))
        lines.append(f"{_e(comp.name)}：({' + '.join(pts)}) ÷ ({' + '.join(caps)}) × {_plain(comp.weight)}"
                     f" = <b>{_e(_plain(score.score))}</b>")
    lines.append(f"合計：{' + '.join(_short(c.score) for c in r.components)} = <b>{_e(_plain(r.total))}</b>")
    basis = "、".join(f"{g}: {_plain(m)}以上" for g, m in rule.grade_thresholds)
    lines.append(f"評価：<b>{_e(r.grade)}</b>　<span class=\"muted\">（基準 {_e(basis)}）</span>")
    problems = recheck(r, rule, e.values, evidence_owner)
    verdict = "一致（別の手順で計算し直しても同じ結果）" if not problems else "不一致：" + "／".join(problems)
    lines.append(f'検算：<span class="tag {"s-ok" if not problems else "s-stop"}">{_e(verdict)}</span>')
    for note in r.notes:
        lines.append(f'<span class="tag s-warn">要確認</span> {_e(note)}')
    return out + ['<div class="calc">' + "".join(f"<div>{line}</div>" for line in lines) + "</div></section>"]


def _rules(rules: RuleBook) -> list[str]:
    out = ["<h2>採点ルール</h2>"]
    labels = {Policy.SCORE_ZERO: "0点", Policy.EXCLUDE: "計算から除外"}
    for subject in rules.subjects():
        rule = rules.get(subject)
        comps = "".join(f"<tr><td>{_e(c.name)}</td><td class=\"num\">{_plain(c.weight)}</td><td>"
                        + "、".join(f"{_e(i)}（{_plain(rule.max_scores[i])}点）" for i in c.items) + "</td></tr>"
                        for c in rule.components)
        markers = "、".join(f"「{_e(k)}」＝{KIND_LABEL[v]}" for k, v in rule.markers.items()) or "なし"
        policies = "、".join(f"{KIND_LABEL[k]}＝{labels[p]}" for k, p in rule.value_policies.items()) or "定めなし"
        basis = "、".join(f"{g}: {_plain(m)}点以上" for g, m in rule.grade_thresholds)
        out.append(f'<section class="card"><h3>{_e(subject)}</h3><div class="muted">根拠: {_e(rule.rule_ref)}</div>'
                   f'<div class="table-wrap"><table><tr><th>評価項目</th><th>配点</th><th>項目（満点）</th></tr>{comps}</table></div>'
                   f"<div>評価基準：{_e(basis)}</div><div>記号の意味：{markers}</div>"
                   f"<div>数値以外の扱い：{_e(policies)}（ここに無い扱いはすべて停止して人に確認します）</div></section>")
    return out
