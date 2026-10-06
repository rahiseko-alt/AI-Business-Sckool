# deck-spec.json（生成AIクイズ UI試作）

- 元ファイル名: deck-spec.json（フォルダ: 2026-09-07_生成AIクイズ_UI試作）
- Drive viewUrl: https://drive.google.com/file/d/1W33MWnb1awOeFFwQFMNvcKVUNqROr5Rz/view?usp=drivesdk
- 最終更新日: 2026-09-07
- 取得日: 2026-09-28
- 区分: teacher

スライド生成に使った仕様ファイル（JSON）。

## 主な項目

- title: 生成AIクイズ 第1問 UI改善試作（原文維持）
- scope: 今回のみ原文を変更せず、UIだけ調整。個人スキルは変更していない。
- design: canvas 720 x 405 pt／font Noto Sans JP／titlePt 20／bodyPt 22／answerAreaPt 16／rubyPt 8.5・7.5
- sourceText: 問題画面・解答画面の元テキスト（読み仮名は「説明(せつめい)」のような括弧付きで保持）
- baseLines: 各行の役割（title／statement／option）、y座標、文字サイズ、太字
- interaction: 問題から1回進めると同じ配置で下部に元の正解文を表示。第1問のみ、問題・解答の2画面。
- validation: exactOriginalTextReadbackMatch true／ルビ括弧とレイアウト空白のみ無視して比較／両状態を目視確認／skillChanged false
