# 成績統合システム

複数の資料から学生ごとの採点情報を集め、科目ごとの採点ルールで計算し、1つの成績資料にまとめます。
目指すのは「間違えないAI」ではなく「間違いを確定できないシステム」です。
迷う箇所があれば必ず止まって質問し、推測で埋めることはしません。

## 現在の状態

- 環境構築のみ完了（保存の土台・工程の進行役・停止と回答の記録・監査ログ）
- 資料の読込・名寄せ・採点計算などの中身は未実装
- 実装を始めるには、実際の資料（または個人情報を伏せた見本）を `data/input/` に置いてください。
  `data/` の中身は Git に入りません

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

---

以下は、このリポジトリが元にした開発フローのテンプレートの説明です。

## 開発フロー（テンプレート由来）
Claude Code で開発を進めるための**テンプレート**です。ここから複製して、新しいプロジェクトを始めます。
製品のコードは入っていません。入っているのは「進め方の仕組み」だけです。

## 複製したら最初にすること

会話を開いて、そのまま話しかけてください。何も打たなくても、AI が
「前回の続き・いまの状態・最初の一手」を報告します。

そのうえで、次の1つだけ打てば始まります。

```
/grill-with-docs
```

AI が質問を重ねて、作りたいものの曖昧な部分を潰します。答えるだけで構いません。
決まった用語は `CONTEXT.md` に、重要な判断の理由は `docs/adr/` に書き残されるので、
次の会話にも引き継がれます。

その後、この `README.md` の冒頭をプロジェクトの説明に書き換えてください。

## 覚えるのはこの3つだけ

| 打つもの | 何が起きるか |
| --- | --- |
| `s` | 前回の続き・いまの状態・最初の一手を報告します（開始時は自動でも出ます） |
| `f` | 環境を破棄しても大丈夫な状態まで片づけ、終了して良いかを報告します |
| `/next-step` | いまどこにいて、次に何を打てばいいかを1つだけ提示します |

コマンドを覚える必要はありません。「〇〇を作りたい」と伝えるだけでも、実装前に自動で案内が入ります。

## 入っているもの

- `.claude/skills/` に [mattpocock/skills](https://github.com/mattpocock/skills) を 12 個インストール
  （`npx skills add mattpocock/skills`、`skills-lock.json` でバージョン固定）
  - ユーザー起動（このうち案内で使うもの）: `grill-with-docs` / `to-spec` / `to-tickets` / `implement` / `improve-codebase-architecture` / `setup-matt-pocock-skills`
  - モデル起動: `grilling` / `domain-modeling` / `codebase-design` / `tdd` / `code-review`
- `.claude/skills/s/`, `.claude/skills/f/`, `.claude/skills/next-step/`: この置き場所独自の案内役と儀式
- `.claude/settings.json`: 会話開始時に `docs/agents/flow-map.md` を読み込む仕組み
- `docs/agents/flow-map.md`: 進め方と、説明の書き方のルール
- `docs/agents/handover.md`: 会話をまたぐ引き継ぎメモ。区切りごとに自動で追記されます
- `AGENTS.md`: 開発フローの全体像
- `docs/agents/issue-tracker.md`: 作業指示書の置き場所は GitHub Issues
- `docs/agents/domain.md`: 用語集は `CONTEXT.md`、判断の記録は `docs/adr/`

## フロー全体

- 新規開発・機能追加: `/grill-with-docs` → 必要に応じて `/to-spec` → `/to-tickets` → `/implement`
- 設計改善: `/improve-codebase-architecture` → 候補を選択 → `/grill-with-docs` または `/codebase-design` → 以下同じ

`/implement` は `/tdd` で RED → GREEN を繰り返し、最後に `/code-review` を実行します。
詳細は [AGENTS.md](./AGENTS.md) の「Development flow」を参照してください。

## スキルの更新

```bash
npx skills update
```

スキル本体は本家のまま使う方針のため、ローカルで書き換えないでください。
