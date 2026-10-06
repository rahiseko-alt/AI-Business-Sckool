#!/bin/sh
# クラウドの作業環境は毎回まっさらなので、会話開始時に成績システムの依存を入れる。
# 出力は会話に読み込まれるため、失敗したときだけ1行出す。
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
pip install -q -e '.[dev]' >/dev/null 2>&1 || echo "依存のインストールに失敗しました: pip install -e '.[dev]' を手動で実行してください"
exit 0
