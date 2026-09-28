取得日: 2026-09-28

# Gemini for Education ／ Gemini in Classroom ／ 年齢・アカウント・データ保護

## 事実（公式ページより）

### Gemini for Education
| 項目 | 内容 |
|---|---|
| 正式名称 | Gemini for Education |
| 提供者 | Google for Education |
| 概要 | 教育向けに設計された生成 AI。LearnLM を取り込んだ Gemini モデルを使用（米国ページ記載: Gemini 2.5 Pro）【曖昧】モデル名は更新が速い |
| 費用 | Google Workspace for Education の**全エディションで無料**（Fundamentals 含む）。上位アドオン Google AI Pro for Education: 米国 月15ドル（年契約）/24ドル（月契約）、日本ページ ¥1,695/月（年契約、1ユーザー） |
| 言語・地域 | 40以上の言語、230以上の国と地域（日本語ページ記載） |
| 主な機能 | 指導案作成、個別化教材、テスト・ルーブリック作成、Deep Research（引用付き）、Gemini Canvas、音声解説（Audio Overviews）、Gemini Live |
| 日本の事例 | 近畿大学附属広島高等学校の教員の声が日本語ページに掲載 |

### データ保護（学校アカウント）
- 「データは人間によるレビューの対象とならず、AI モデルのトレーニングにも使用されない」（日本語 Gemini for Education ページ）
- Workspace for Education 規約上の **Core Service**（コアサービス）扱い。COPPA、FERPA 等のコンプライアンスをサポート（米国の法令）
- Gemini アプリのヘルプ: 学校アカウントのチャットとアップロードファイルは人間のレビュー対象外、生成 AI モデル改善に使われない
- 会話履歴はデフォルトで18か月保存。管理者が3/18/36か月または無効に変更可
- 学校アカウントではモバイルアプリの一部機能が使えない: Google アシスタント連携機能、チャットの削除、公開チャットリンク作成
- 利用上限の例: 基本の Education プランで Pro モデル「4時間あたり最大25プロンプト」【曖昧】上限は頻繁に変わる
- 管理者は Vault で会話を検索・保持管理できる

### 年齢・アカウント要件
- Gemini アプリと Gemini Notebook は **Workspace for Education では全年齢が利用可能**（管理者クイックスタートガイド）
- 18歳未満には別の体験: より厳しいコンテンツポリシー、AI リテラシー資料つきのオンボーディング（ConnectSafely、Family Online Safety Institute 推奨）、事実回答の自動ダブルチェック
- 「Google Workspace with Gemini」アドオンおよび Google AI Pro for Education は **18歳未満は利用不可**
- 一部機能は18歳以上のみ
- 年齢別アクセス設定（管理コンソール）: 初等中等教育機関は18歳以上指定のないユーザーが自動的に制限対象。**高等教育機関は18歳未満指定のないユーザーに追加制限なし**（18歳未満の学生は管理者が指定する必要あり）
- 18歳未満は Search Labs 不可。個別設定のない追加サービスは自動的に「制限」
- 管理コンソール: 生成 AI → Gemini アプリ → サービスのステータスで ON/OFF、組織部門・グループ単位で設定可、反映に最大24時間。Android では「検索とアシスタント」サービスの有効化が必要

### Gemini in Classroom
| 項目 | 内容 |
|---|---|
| 対象エディション | Workspace for Education Fundamentals / Standard / Plus |
| 費用 | 全エディションで無料（2025年6月30日発表） |
| 日本語 | Google Japan ブログ「Gemini in Classroom: 日本語でも提供を開始」で日本語提供を告知。管理ヘルプでは「Gemini がサポートされる全ての Classroom 対応言語で提供」 |
| 年齢 | 現行の管理ヘルプ: 全年齢で利用可、年齢別アクセス設定に従う。デフォルト ON（過去に18歳未満を OFF にしていた場合はその設定を維持）。**日本語ブログ（公開時点）では「18歳以上のユーザーが利用できます」** 【曖昧】時期により条件が変わっている。最新の管理ヘルプを優先 |
| 前提 | 学生が Classroom で「生徒」ロールであること。Gemini アプリか Gemini Notebook のどちらかが ON であること（両方 OFF だと Gemini タブは非表示） |
| 教員向け機能 | 指導案の概要、テスト生成、解説作成、語彙リストなど「30以上の新機能」（2025年6月） |
| 学生向け機能 | 学習サポート、テスト、フラッシュカード、学習ガイド |

### 関連発表（2025年6月30日 ISTE）
- Gems（カスタム AI）を教員間で共有
- Gemini Canvas でクイズ生成（当初18歳以上）
- Common Sense Media Privacy Seal 取得
- NotebookLM の18歳未満対応を予告

## まとめ（筆者による整理・提案）

- **専門学校は通常「高等教育」扱い**になるため、管理者が明示的に18歳未満を指定しない限り制限はかからない。ただし1年生に17歳がいる可能性があるので、学校の Workspace 管理者と年齢設定を確認すること。
- **学校アカウント（Workspace for Education）で使うのが最重要**。個人の Gmail アカウントでは教育向けデータ保護（人間レビューなし・学習不使用）が適用されない。授業では必ず学校アカウントでログインさせる。
- スマホでは Gemini アプリに学校アカウントを追加して使う。チャット削除ができない点、履歴が管理者に保持される点を学生に説明しておく（ビジネス情報リテラシーの題材にもなる）。
- 学校が Workspace for Education を導入していない場合、個人アカウント（13歳以上／国の最低年齢）での利用となり、利用規約・データ扱いが異なる。授業開始前に確認必須。

### 授業への対応（ビジネス情報リテラシー 2〜3回分）
1. 「同じ Gemini でもアカウントでデータの扱いが違う」— 学校アカウントと個人アカウントの比較
2. 会話履歴・管理者の閲覧・保持期間 — 職場の業務アカウントと同じ構造であることを学ぶ
3. Gemini in Classroom の学習ガイド・フラッシュカードで自習する方法

## 出典
- https://edu.google.com/intl/ALL_us/ai/gemini-for-education/
- https://edu.google.com/intl/ALL_jp/ai/gemini-for-education/
- https://support.google.com/gemini/answer/14620100?hl=en&co=DASHER._Family%3DEducation
- https://knowledge.workspace.google.com/admin/gemini/turn-the-gemini-app-on-or-off?hl=en&co=DASHER._Family=Education （support.google.com/a/answer/14571493 からの 301 リダイレクト先）
- https://knowledge.workspace.google.com/admin/getting-started/editions/manage-access-to-gemini-in-classroom?hl=en （support.google.com/a/answer/16291887 からのリダイレクト先）
- https://knowledge.workspace.google.com/admin/getting-started/editions/control-access-to-google-services-by-age?hl=en （support.google.com/a/answer/10651918 からのリダイレクト先）
- https://knowledge.workspace.google.com/admin/getting-started/editions/quickstart-guide-to-gemini-and-gemini-notebook-for-education
- https://blog.google/products-and-platforms/products/education/gemini-iste-2025/
- https://blog.google/intl/ja-jp/company-news/outreach-initiatives/gemini-in-classroom/
- 取得失敗: https://support.google.com/edu/classroom/answer/15252543 （404）
