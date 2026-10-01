# 成績統合システム

複数の資料から学生ごとの採点情報を集め、科目ごとの採点ルールで計算し、1つの成績資料にまとめます。
目指すのは「間違えないAI」ではなく「間違いを確定できないシステム」です。
迷う箇所があれば必ず止まって質問し、推測で埋めることはしません。

## 現在の状態

- 環境構築のみ完了（保存の土台・工程の進行役・停止と回答の記録・監査ログ）
- 資料の読込・名寄せ・採点計算などの中身は未実装
- 実装を始めるには、実際の資料（または個人情報を伏せた見本）を `data/input/` に置いてください。
  `data/` の中身は Git に入りません

## 成績資料（出力）

Excel 1ファイルに、成績表・検算・完全性・根拠・採点ルール・確認事項をまとめて出力します。
「検算」シートの小計・合計・評価は Excel 自身の計算式で、システムの値と並べて一致・不一致を表示します。
見本（架空データ）: `docs/sample/成績資料_サンプル.xlsx`（`python3 -m grading.sample <出力先>` で作り直せます）

## 構成

| 場所 | 役割 |
| --- | --- |
| `src/grading/pipeline/` | LOAD → … → EXPORT の進行役。未解決の BLOCKED があれば ASK_USER で止まる |
| `src/grading/store/schema.sql` | 13 の表。元資料・根拠・回答・監査ログはデータベース側で書き換えを拒否 |
| `src/grading/issues/` `decisions/` | 停止理由と回答の記録。同じ問題は二度聞かない |
| `src/grading/audit/` | 全処理の監査ログ |
| `src/grading/{importing,classification,extraction,normalization,identity,rules,calculation,validation,export}/` | 各工程（未実装） |
| `docs/adr/0001-*.md` | 守るべき原則 |

```bash
pip install -e '.[dev]'   # クラウドの会話では開始時に自動実行
python3 -m pytest
```

## 進め方

- 会話の最初に、前回の続きと次の一手が自動で報告されます
- `s` で現状報告、`f` で終了前の片づけ、`/next-step` で次に打つものを案内します
- 会話をまたぐ記録は `docs/agents/handover.md` に残ります
