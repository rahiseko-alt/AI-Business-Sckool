# 提出用シラバス（3科目）の中身

作成日: 2026-09-29。状態: 下書き（利用者の確認待ち）。

- `marketing.json`・`ai.json`・`literacy.json`: 提出先シートの欄ごとの中身（正）
- `build.py`: JSON から、提出先シートと同じ枠の `syllabus.xlsx`（3タブ）を作る。`python3 build.py docs/drafts/syllabus-sheets`
- Google ドライブに、提出先シートと同じセル位置で値だけを入れたスプレッドシートを3つ作った（Google Sheets 連携が無いため、元のシートには直接書けない。利用者が貼り付ける）
  - マーケティング: https://docs.google.com/spreadsheets/d/14iQHZbjYjZ87Fg6IJHh-gYYpejOzQrxxTug22tYWoL8/edit
  - AI演習（実践）: https://docs.google.com/spreadsheets/d/1XAUhBMlb6LGm1FrIsFYDBoyGUlcF6LYTIXULJRRIt_0/edit
  - ビジネス情報リテラシー: https://docs.google.com/spreadsheets/d/1YA7NeopKQxjdN-WbtaKcw9OBNw1BZysIEgIKHvhP_Bs/edit
- 未確定: 単位数（学校確認中）、リテラシーの後期の科目名（資料では「ビジネスIT」に変わる記載あり）
- 2026-09-29: 3科目とも要点だけに短くした版に差し替え、旧版はゴミ箱へ（利用者承認）
- 2026-09-29: Google Sheets 連携を追加（利用者）。提出先シート（https://docs.google.com/spreadsheets/d/18dGvAfyAc1UMdphg27CtaJdfbTYxWkjIEuxaNhSPhzw/edit ）の「シラバス」タブを複製して「マーケティング」タブを作り、marketing.json を書き込んだ（欄とのバランス確認用。元の「シラバス」タブは変更なし）。文章欄は1行1マスの5行なので、5行を超える評価基準は2項目ずつ1マスにまとめた

- 2026-09-29: 同じ提出先シートに「AI演習（実践）」「ビジネス情報リテラシー」タブを作り、ai.json・literacy.json（マーケティングと同じ書き方）を書き込んだ
