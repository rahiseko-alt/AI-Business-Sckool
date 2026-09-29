取得日: 2026-09-29

# 基本教材の目次を、2026年9月時点の最新情報に置き換えた版

利用者の指示（2026-09-29）: 基本教材『Geminiビジネス活用ガイド』は本文が古く意味をなさないので、**目次の節ごとに最新の類似内容を調べて使う**。本文は使わない。
目次そのものは `12-gemini-business-guide-base-textbook.md`。この文書は、節ごとの「いまの名前・できること・無料で使えるか・スマホで使えるか・出典」を、サブエージェント5体が Google 公式ヘルプ・公式ブログ・公式リリースノートで調べた結果（報道だけのものは【曖昧】）。

## 要点（授業の前提: 学生は全員成人、無料の個人 Google アカウント、スマホだけ）

- **NotebookLM は2026年7月16日に「Gemini Notebook」に改名**。無料で使え、専用のスマホアプリがある（第5章は全部使える）
- **Gem は終了し「スキル」に移行**（個人アカウントは2026年11月）。公式ヘルプではスキルは「Google AI の契約なしで使える」。条件は18歳以上・「アクティビティを保存」オン。報道の「スキル作成は有料のみ」は公式と食い違う【曖昧】→ 学生は全員成人なので、公式どおりなら使える
- **動画（旧 Veo3、いまは Gemini Omni）は有料のみ**。使わない
- **第4章（Gmail・スプレッドシート等の画面の中の Gemini）は個人の無料アカウントではほぼ使えない**。代わりに、Gemini アプリの「連携アプリ（Google Workspace）」で Gmail・ドライブ・ドキュメント・カレンダー・Keep・ToDo を Gemini アプリ側から扱える（無料。「アクティビティを保存」オンが条件）
- **ディープリサーチ・Canvas の一部・画像の編集・スキルは18歳以上**（学生は全員成人なので問題なし）
- **スケジュールされたアクション**は、無料で使えるかが公式ページどうしで食い違う（わからない）
- 無料の上限は2026年5月17日から「5時間ごとに回復＋週の上限」。一度に読める量は無料32kトークン
- モデルの番号（3.6 Flash など）は数週間ごとに変わる。授業では「Flash（速い）と Pro（深い）」と教え、番号は書かない
- 学生向けに Google AI Plus 1年無料（2026年12月31日まで受付）があるが、日本の専門学校生が対象かはわからない【曖昧】


---

# 調査結果: 第1章

担当した第2章1〜5を、2026年9月29日時点の Google 公式ヘルプ（日本語版・Android 表示）と公式リリースノートで調べました。報道記事は出典に使っていません。

**大きな変化が3つあります。**
- 第2章5「動画（Veo3）」は Veo の名前がヘルプから消え、「Gemini Omni」に変わっています。しかも無料アカウントでは使えません。
- 回数制限は「1日○回」から「使った量で決まる上限」に変わりました（2026年5月17日から）。上限は5時間ごとに戻り、別に週ごとの上限があります。無料の上限は「標準」で、Google AI Plus は2倍、Pro は4倍です。
- ディープリサーチと、Canvas の一部の機能は18歳以上限定です。18歳未満の学生がいると、その学生は使えません。

| 節 | いまの名前 | できること（授業で使う操作） | 無料 | スマホ | 出典 |
|---|---|---|---|---|---|
| 2-1 基本操作とインターフェース | Gemini アプリ（アプリ版と gemini.google.com） | ・新しいチャットを作る／入力欄で質問する／ファイルや画像を付ける<br>・送ったプロンプトを直すと回答が作り直される。ほかの回答案も見られる<br>・メニューの「最近」で履歴を見る。チャットの長押しで「固定・名前を変更・削除」。「新しいチャットに分岐」もある（ヘルプに書いてあるのは Android アプリ）<br>・チャットからドキュメント・スプレッドシート・PDF を作れる | ○（履歴・固定・名前の変更は「アクティビティの保存」がオンのときだけ） | ○（アプリはチャットの長押し、ブラウザは「その他」メニュー） | https://support.google.com/gemini/answer/13275745?hl=ja ／ https://support.google.com/gemini/answer/13666746?hl=ja |
| 2-2 選べるAIモデル | 入力欄のモデル名をタップして選ぶ。**Flash-Lite（速い）／Flash（バランス）／Pro（難しい数学やコード向け）**。深く考えさせる度合いは「標準思考」と「拡張思考」から選べる。Deep Think は Ultra 限定 | ・入力欄のモデル名をタップ →「Flash」と「Pro」で同じ質問をして、速さと中身を比べる<br>・高いモデルや拡張思考ほど上限に早く届くことを体験する<br>・ヘルプ上のモデル名は「Gemini 3 Flash／3 Pro」。リリースノートには 2026年7月21日「Gemini 3.6 Flash を全ユーザーに提供」とある。いま画面に何番の版が出るかは**わからない**<br>・API 料金の項目：API 料金ページ（2026年9月24日更新）の見出しには 3.8 Flash などがあり、無料枠のあるモデルもある。ただ、スマホだけの授業では使わない | ○（3つとも無料で選べる。ただし上限は「標準」で、読み込める量は32,000トークン。Plus は128,000、Pro と Ultra は100万） | ○ | https://support.google.com/gemini/answer/16275805?hl=ja ／ https://gemini.google/release-notes/ ／ https://ai.google.dev/gemini-api/docs/pricing |
| 2-3 ディープリサーチ | Deep Research（名前は変わっていない） | ・アプリで「＋（ファイルを追加）」→「Deep Research」→ 質問を入れる → 出てきたリサーチプランを確かめ（「プランを編集」もできる）→「リサーチを開始」<br>・5〜10分でレポートができ、終わるとスマホに通知が来る<br>・できたレポートは、音声解説にする・図にする（「作成」）・Google ドキュメントに出す、ができる | ○（「高速モード」のみ。1日に作れる数に上限あり。「思考モード」は Pro と Ultra のみ）。**18歳以上限定**。無料だと混雑時に使えないことがある | ○（アプリもブラウザも使える。調べ先の「ソース」選びはアプリでは順次公開中） | https://support.google.com/gemini/answer/15719111?hl=ja&co=GENIE.Platform%3DAndroid |
| 2-4 Canvas | Canvas（名前は変わっていない。スライド生成もここに入った） | ・「＋」→「Canvas」→ プロンプトを入れる（例：「〜のスライドを作成して」「〜のクイズを作成して」）<br>・文書やアプリを作り、プロンプトで直す。変更は自動保存される<br>・「共有とエクスポート」で共有リンクを作る、Google ドキュメントに出す<br>・文書から音声解説、クイズ、インフォグラフィック、ウェブページを作れる（**18歳以上限定**） | ○（全プランで使える） | ○（ただし文字のスタイルや書式を変えられるのはパソコンのブラウザだけ。人から共有された Canvas はアプリでは開けず、ブラウザで開く） | https://support.google.com/gemini/answer/16047321?hl=ja&co=GENIE.Platform%3DAndroid ／ https://support.google.com/gemini/answer/16275805?hl=ja |
| 2-5 動画（Veo3） | **「動画」機能。いまのモデルは Gemini Omni**（動画のヘルプに Veo の名前は出てこない） | ・メニュー →「動画」→ プロンプトを入れる。画像は最大5枚、動画は1本を材料にでき、会話を続けながら何度も直せる。縦横比も選べる<br>・できた動画は「共有」から端末に保存するか YouTube に出す | ×（Google AI の有料プランが必要。**Google AI Plus 以上**）。**18歳未満は使えない** | ○（有料プランならアプリでもブラウザでも使える） | https://support.google.com/gemini/answer/16126339?hl=ja&co=GENIE.Platform%3DAndroid ／ https://support.google.com/gemini/answer/16275805?hl=ja |

**わからないこと**
- 無料アカウントで、ディープリサーチが1日に何回使えるか。どの公式ページにも数字がありません。
- いまのアプリ画面で、Flash と Pro の後ろに何番の版（3.6 など）が表示されるか。
- リリースノート（2026年8月19日）に「対象の学生に Google AI Plus を1年無料」とあります。日本が対象か、専門学校生が対象か、年齢などの条件は何かは、確かめられていません。これが使えれば第2章5も授業で扱えるかもしれません。
- API 料金の具体的な金額。料金ページを自動で要約した数字しか見ておらず、元の表とは突き合わせていません。

**授業で使える／使えない（節ごと）**
- 2-1 基本操作とインターフェース：使える
- 2-2 選べるAIモデル：使える
- 2-3 ディープリサーチ：条件付き（18歳以上なら）
- 2-4 Canvas：使える
- 2-5 動画：使えない

ファイルはどこにも書いていません。

---

# 調査結果: 第2章 1〜5

## 第1章 1〜7：2026年9月29日時点の最新情報

先に結論です。ご指摘のとおり、本文はほぼ使えません。2年間で名前が変わったもの（NotebookLM → **Gemini Notebook**）、モデルの世代が何回も進んだもの（Gemini 3.6 Flash / 3.1 Pro）、無料版では使えないもの（Workspace アプリの中の Gemini、Genie）がそれぞれあります。

| 節 | いまの名前 | できること（授業で使う操作） | 無料 | スマホ | 出典 |
|---|---|---|---|---|---|
| 1 モデルの進化 | Gemini アプリの無料版は **Gemini 3.6 Flash**（2026年7月21日から。モデル一覧で「3.6 Flash」を選ぶ）。上位の **3.1 Pro** も回数を制限して使える。開発者向けには 3.7 Flash（8月）と 3.8 Flash（9月）が報道されているが、アプリで選べるかは**わからない**【曖昧】 | モデル一覧で Flash と Pro を切り替える。同じ質問を両方に出して、速さと答えの深さを比べる | 使える。3.6 Flash は利用できる。3.1 Pro は「アクセス（制限あり）」。具体的な回数は公式に書かれていない | 使える（アプリとブラウザ） | https://gemini.google/release-notes/ ／ https://gemini.google/jp/subscriptions/ ／ https://support.google.com/gemini/answer/16275805 ／ 3.7・3.8 は報道のみ【曖昧】: https://9to5google.com/2026/08/13/gemini-3-7-flash-launch/ |
| 2 Workspace への導入 | **Gemini in Gmail / ドキュメント / Vids など**（アプリの中のサイドパネル） | Gmail やドキュメントの画面の中で、要約や下書きを Gemini に頼む | 無料では**使えない**（公式の比較表で、無料の列にこの機能が無い）。Gmail と Vids は **Google AI Plus**（¥725/月と表示。キャンペーン価格かは**わからない**）から。ドキュメントは **Google AI Pro**（¥2,900/月）から。18歳以上が条件 | 無料では対象外。有料版でスマホから使えるかの詳細は**わからない** | https://gemini.google/jp/subscriptions/ |
| 3 大容量データ処理 | 「ロング コンテキスト」（一度に読み込める量） | PDF などをまとめて渡して要約させる。1回に10ファイルまで。動画は1本2GBまで、動画以外は1ファイル100MBまで | 無料版は **32k トークン**（Pro は 100万）。動画は合計5分まで、音声は合計10分まで（Pro はそれぞれ1時間、3時間） | 使える（アプリからファイル添付） | https://support.google.com/gemini/answer/16275805 ／ https://support.google.com/gemini/answer/14903178 |
| 4 マルチモーダル（コラム: Genie 3） | **Gemini Live**（カメラ共有・画面共有）。Genie 3 は **Project Genie** として提供 | Live でカメラを向け、写したものについて声で質問する。画面を共有して、表示中の内容を相談する | Live は使える。Project Genie は **Google AI Ultra**（¥14,500/月から）だけで、無料では使えない | Live は Android と iPhone のアプリで使える（ウェブ版では使えない）。Genie をスマホで使えるかは**わからない** | https://support.google.com/gemini/answer/15274899 ／ https://gemini.google/jp/subscriptions/ ／ Genie の時期: https://9to5google.com/2026/01/29/google-project-genie/【曖昧】 |
| 5 Workspace アプリ連携 | **アプリ連携**（Gemini アプリから Gmail、ドライブ、ドキュメント、カレンダー、Keep、ToDo リストにつなぐ） | 「@」でサービスを選んで、「ドライブの○○を5行で要約して」「Keep に保存して」のように頼む。「アクティビティの保存」をオンにしておく必要がある | 使える（無料版の機能一覧に Connected Apps が入っている） | 使える。ただし Live 中に使えるサービスは一部だけ | https://support.google.com/gemini/answer/15229592?hl=ja ／ https://support.google.com/gemini/answer/16275805 |
| 6 NotebookLM | **Gemini Notebook**（2026年7月16日に NotebookLM から改名。URL は notebooklm.google のまま） | 授業資料をソースとして登録し、その資料だけを根拠にチャットで質問する。音声解説、クイズ、フラッシュカード、マインドマップを作る | 使える（Standard）。ノートブック100件、1冊あたりソース50件、チャット50回/日、音声解説3件/日、クイズ10件/日、Deep Research 10件/月。Google アカウントの年齢確認が必要 | 専用のモバイルアプリがある（「初期バージョン」で一部機能のみ）。ブラウザでも使える | https://workspaceupdates.googleblog.com/2026/07/notebooklm-now-gemini-notebook.html ／ https://support.google.com/notebooklm/answer/16213268?hl=ja ／ https://support.google.com/notebooklm/answer/16269187?hl=ja |
| 7 Gemma | **Gemma 4**（2026年4月2日公開。いまも最新か、Gemma 5 が出ていないかは報道でしか確認できていない【曖昧】）。スマホ用の小型版は E2B と E4B | 「Google AI Edge Gallery」アプリにモデルを入れ、ネットにつながずに端末の中だけで会話や要約をさせる | 使える（無料のオープンモデル） | 使える（Android と iOS）。ダウンロード容量や必要な端末性能は**わからない** | https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/ ／ https://play.google.com/store/apps/details?id=com.google.ai.edge.gallery |

補足:
- Gemini アプリには2026年8月19日に「学生ハブ」と、スマホで使える「学習ノートブック」が加わりました。日本の料金ページには「学生: Plus プランを1年間無料（まもなく終了）」という表示があります。専門学校生が対象に入るかは**わからない**です。出典: https://gemini.google/release-notes/
- 公式ページの注記に、無料版の上限は「2026年5月17日から変更」とあります。回数は今後も変わる前提で扱ってください。
- モデルの番号は数週間おきに変わります。教材には番号を書かず、「Flash（速い）と Pro（深い）」という分け方で教えるほうが安全です。

## 授業で使える／使えない（節ごとに1語）
1. 使える
2. 使えない
3. 使える
4. 使える（Genie のコラムは使えない）
5. 使える
6. 使える
7. 使える

---

# 調査結果: 第2章 6〜10

## 第2章 6〜10の最新状況（2026年9月29日に確認）

| 節 | いまの名前 | できること（授業での操作） | 無料 | スマホ | 出典 |
|---|---|---|---|---|---|
| 6 画像生成 | Nano Banana 2（Lite 版あり）。高画質版は Nano Banana Pro | アプリのメニューから「画像」を開き、テンプレートを選ぶか指示文を入れて生成する。編集はライブラリで画像を選び、「チャット」で直したい点を指示する | 使える。Nano Banana 2 は1日の上限あり（回数は公式に書かれていない＝わからない）。Nano Banana Pro での作り直しは有料の Google AI Plus 以上 | 使える（Android の手順が公式ヘルプにある） | https://support.google.com/gemini/answer/14286560 ／ https://support.google.com/gemini/answer/16275805 |
| 7 学習モード | ガイド付き学習（Guided Learning） | 入力欄の「ファイルを追加」から「ガイド付き学習」を選び、学びたいことを送る。段階を追った解説と確認の問題が返ってくる | 使える（プラン表で「Guided Learning（クイズ・フラッシュカード）」が無料で使える印）。英語・米国・18歳以上に限られるのは OpenStax 教材の連携だけ | 使える（ただしモバイルアプリへは「順次提供中」） | https://support.google.com/gemini/answer/16448384?hl=ja ／ https://blog.google/products-and-platforms/products/education/guided-learning/ |
| 8 Gem | Gem は終了し、スキル（skills）へ移行する。個人アカウントは2026年11月、学校アカウントは2027年6月（公式）。既存の Gem は自動でスキルに変わる | スキルは入力欄に「/」と打って呼び出し、1つのチャットで複数を組み合わせられる。作成はメニュー→設定→スキル | Gem は今は無料。スキルも公式ヘルプに「Google AI の契約なしで使える」とある。ただし18歳以上で、個人アカウントかつ「アクティビティを保存」をオンにする必要がある。報道の「スキル作成は有料のみ」【曖昧】は公式と合わない。「10月中旬から Gem の新規作成・編集ができなくなる」は報道のみ【曖昧】 | スキルはスマホで使える。ファイルを添えたスキル作成は Mac アプリとブラウザ版だけ | https://support.google.com/gemini/answer/18560919 ／ https://support.google.com/gemini/answer/17094296 ／ 報道【曖昧】 https://9to5google.com/2026/09/27/gemini-gems-skills/ |
| 9 Workspace 連携 | 「連携アプリ（Connected Apps）」の中の Google Workspace アプリ。旧称の「拡張機能」は使われていない。Gmail・Photos・YouTube などとつなぐ「Personal Intelligence」は別の機能で、米国の Pro/Ultra 向け | アプリのメニュー→プロフィール→連携アプリで Workspace をオンにする。そのうえで「Gmail の〇〇を要約して」「ドライブの PDF を探して」のように指示する。対象は Gmail・ドキュメント・ドライブ・カレンダー・ToDo リスト（Tasks）・Keep | 使える（プラン表で無料に印あり）。「アクティビティを保存」をオン、Gmail の「他の Google サービスのスマート機能」をオンにする必要がある。年齢条件は書かれていない＝わからない | 使える（Android の手順が公式ヘルプにある） | https://support.google.com/gemini/answer/15229592 ／ https://support.google.com/gemini/answer/13695044 ／ https://support.google.com/gemini/answer/16275805 |
| 10 スケジュールされたタスク | 「スケジュールされたアクション（Scheduled actions）」。これとは別に、有料の Gemini Spark に「スケジュール」機能がある | チャットで「毎朝7時に天気とニュースをまとめて」のように頼むと予約できる。同時に有効にできるのは10件まで | 公式どうしで食い違う＝わからない。プラン表は「契約なしは使えない」、機能の説明ページは「Google AI プランなしの場合は数時間前に準備」と書いている。Spark のスケジュールは Pro/Ultra 限定で18歳以上 | スケジュールされたアクションはアプリで作れる。Spark の「スケジュール」画面はブラウザ版だけ | https://support.google.com/gemini/answer/16316416 ／ https://support.google.com/gemini/answer/16275805 ／ https://support.google.com/gemini/answer/17094710 |

## 授業で使える／使えない（1語）

- 6 画像生成：使える
- 7 学習モード：使える
- 8 Gem：使えない（11月に終了するので、後継のスキルとして教えるなら条件付きで可。18歳以上が条件）
- 9 Workspace 連携：使える
- 10 スケジュールされたタスク：使えない（無料で使えるか公式どうしで食い違うため、確かめられていない）

## 補足

- 画像の編集は18歳以上、生成は13歳以上。スキルも18歳以上。
- 9 と 10 は「アクティビティを保存」をオンにするのが前提。学生にこの設定を求めてよいかは、授業の方針として判断が必要。

---

# 調査結果: 第3章

# 第3章 1〜5：無料のGeminiアプリ（スマホ）で授業に使えるか（2026年9月29日に調査）

目次にある節の中身は今も使えます。ただし、2年前の本文にある操作手順と機能名は古くなっています。調べたのは Google の公式ヘルプ（support.google.com）、公式ブログ（blog.google）、公式リリースノート（gemini.google）です。ファイルは作っていません。

**全体に関わる点**
- **無料アカウントの上限：** 無料アカウントは「standard limits（標準の上限）」です。2026年5月17日から、上限が5時間ごとに回復し、週単位の上限がある方式に変わりました。一度に扱える量（コンテキスト長）は、無料が32k、AI Plus が128k、AI Pro と AI Ultra が100万トークンです。
- **モデル：** 無料でも Gemini 3 系のモデルが使えます。7月21日に全ユーザー向けに Gemini 3.6 Flash が出ています。
- **学生向け特典：** 2026年8月から、条件を満たす大学生は米国外なら Google AI Plus が1年間無料です。受付は2026年12月31日まで、学生確認は SheerID です。日本の専門学校生が対象かどうかは公式では確かめられませんでした（わからない）。
- **年齢の制限：** Deep Research と、Canvas の一部の機能は、公式ヘルプに「18歳以上」と書かれています。18歳未満の学生がいるクラスでは使えない可能性があります。

| 節 | いまの名前 | できること（授業での操作） | 無料 | スマホ | 出典 |
|---|---|---|---|---|---|
| 1. アイデア出し | Gemini アプリ（通常のチャット）、Gems、Canvas | チャットで案を出させてから、「表にして」「3案に絞って」と頼んで絞り込む。Gems では役割（例：企画担当）を決めた自分専用のGeminiを作れる。Canvas では、出した案をそのまま文書やスライドにできる。 | 使える（標準の上限あり。Gems と Canvas も無料で使える） | 使える（アプリ） | [上限と料金プラン](https://support.google.com/gemini/answer/16275805?hl=en) / [Canvas](https://support.google.com/gemini/answer/16047321?hl=en&co=GENIE.Platform%3DAndroid) |
| 2. 情報収集・リサーチ | Deep Research（Gemini アプリ内の機能） | 「＋（Add）」から Deep Research を選んで質問を入れる。まず調査計画が出て、5〜10分ほどで出典つきのレポートができる。Googleドキュメントへの書き出しと、音声での解説（Audio Overview）の作成ができる。 | 使える（1日の回数などに上限あり。有料の AI Pro / Ultra は上限が高く、レポートの質も上がる）。**18歳以上が条件** | 使える（Android / iOS アプリ） | [Deep Research](https://support.google.com/gemini/answer/15719111?hl=en&co=GENIE.Platform%3DAndroid) / [上限と料金プラン](https://support.google.com/gemini/answer/16275805?hl=en) |
| 3. 文章作成（要件・具体例・出力フォーマット、リバース・ナレッジ） | Gemini アプリ（チャット）、Canvas | 条件、例、出力の形をプロンプトに書いて文章を作る。Canvas では下書きを横に表示したまま「ここを丁寧語に」と部分的に直せる。Googleドキュメントへの書き出しと、共有リンクの作成ができる。「リバース・ナレッジ」という機能は公式には無い（わからない） | 使える | 使える（アプリ）。ただし共有リンクはブラウザ（gemini.google.com）でしか開けず、アプリでは開けない | [Canvas](https://support.google.com/gemini/answer/16047321?hl=en&co=GENIE.Platform%3DAndroid) |
| 4. 外国語関連業務 | Gemini アプリのチャット（翻訳、添削）、Gemini Live（音声で会話）、Google 翻訳アプリ（Gemini を使った翻訳と会話練習） | チャットでメール文の翻訳や添削をする。Gemini Live で声で会話練習をする（カメラ映像や画面の共有もできる）。Google 翻訳アプリは Gemini で自然な訳ができ、会話練習の機能もある。ヘッドホンで聞くリアルタイム通訳はベータ版 | チャットは使える。Gemini Live が有料かどうかは公式ヘルプに書かれていない（わからない）。翻訳アプリの新機能に料金の記載は無い | チャットと Live はアプリで使える。リアルタイム通訳（ベータ）は2025年12月時点で Android（米国・メキシコ・インド）のみ。**日本で使えるかはわからない**。Gemini Live が日本語に対応しているかも、公式ヘルプからは確かめられなかった | [Gemini Live](https://support.google.com/gemini/answer/15274899?hl=en&co=GENIE.Platform%3DAndroid) / [公式ブログ（翻訳）](https://blog.google/products-and-platforms/products/search/gemini-capabilities-translation-upgrades/) |
| 5. ITツール活用・プログラミング（関数・マクロ・Apps Script・バイブコーディング） | ① Gemini アプリのチャットと Canvas（コード生成、アプリ試作、プレビュー）② ファイルのアップロードと分析（表からグラフを作る）③ Gemini in Google Sheets（スプレッドシートの画面の中で使う Gemini） | ① 「売上を合計する関数を作って」と頼み、出てきた式をスプレッドシートにコピーする。Canvas では言葉で頼むだけで Webアプリを作れて、プレビューと動作確認ができる（バイブコーディング）。② CSV や XLSX を最大10件アップロードしてグラフを作らせる。③ 関数の自動作成や =AI() 関数は、スプレッドシートの画面の中で動く | ①② は使える。③ は**有料プランか Google Workspace が必要**。個人向けの AI Plus で使えるかはわからない。Canvas で作るアプリに AI 機能を組み込むのは**18歳以上** | ①② はアプリで使える。③ は Android と PC の案内のみ。スマホで Apps Script やマクロを編集できるかは公式で確かめられなかった（わからない） | [Canvas](https://support.google.com/gemini/answer/16047321?hl=en&co=GENIE.Platform%3DAndroid) / [ファイルのアップロード](https://support.google.com/gemini/answer/14903178?hl=en&co=GENIE.Platform%3DAndroid) / [Sheets の Gemini](https://support.google.com/docs/answer/14356410?hl=en) |

**確かめられなかったこと**
- **Gemini アプリ内のコード実行：** 無料ユーザー向けのコード実行について、公式の説明は見つかりませんでした（わからない）。公式にあるのは、グラフ作成と、有料プラン向け機能 Gemini Spark のリモート実行だけです。
- **学生特典の日本での対象：** 日本が対象に含まれるという話は報道だけで、公式では確かめられていません【曖昧】（[公式ブログ](https://blog.google/innovation-and-ai/products/gemini-app/student-offer-google-ai/)）。

## 結論（節ごとに1語）
1. アイデア出し：**使える**
2. 情報収集・リサーチ：**条件付き**（18歳以上のみ）
3. 文章作成：**使える**
4. 外国語関連業務：**使える**（チャットでの翻訳と添削。リアルタイム通訳は日本で使えるかわからない）
5. ITツール活用・プログラミング：**一部使える**（関数づくりとバイブコーディングはアプリで使える。スプレッドシート内の Gemini と Apps Script はスマホの無料アカウントでは使えない）

---

# 調査結果: 第4章〜第6章

## 第4章〜第6章：最新情報の調査（2026-09-29 時点）

**先に結論です。** 目次にある機能はほぼすべてまだありますが、名前と使える条件が変わっています。
- **名前の変更：** NotebookLM は **2026年7月16日から「Gemini Notebook」** に変わりました（アプリは別のまま残り、機能の変更はありません）。Workspace Labs は **2026年3月10日から「Google Workspace Experiments」** に変わりました。
- **第4章：** Gmail の AI スレッド要約だけは全世界で無料、日本語にも対応しています。それ以外（ドキュメント・スプレッドシート・スライド・ドライブ・Meet）の Gemini は、個人アカウントだと **Google AI Pro か Ultra**（一部は **AI Plus** でも可）が必要です。Chat には個人向けの Gemini 機能がありません。
- **第5章：** 無料で使えます。スマホアプリもあります。

### 第4章 Gemini in Google Workspace

| 節 | いまの名前 | できること（授業での操作） | 無料 | スマホ | 出典 |
|---|---|---|---|---|---|
| 4-1 Gemini in Workspace とは | 公式ヘルプでは「Google Workspace with Gemini」。個人向けは Google AI Plus / Pro / Ultra の特典 | 各アプリの画面内にある Gemini ボタンやサイドパネルで、要約・作成・分析ができる | 個人アカウントでは、ほとんどの機能が有料プラン必須 | 一部だけ（アプリごとに違う） | https://support.google.com/mail/answer/13952129?hl=en&co=DASHER._Family%3DPersonal |
| 4-1 無料の代わり①（Gemini アプリ） | Gemini アプリの「Google Workspace」連携（接続アプリ） | Gemini アプリから Gmail・ドキュメント・ドライブの中身を要約・検索できる。Keep・ToDo・カレンダーの追加や取得もできる | 無料かどうかは公式ヘルプに書かれていない（わからない）。「アクティビティを保持」と Gmail のスマート機能をオンにする必要がある | Gemini アプリで使えるが、ヘルプにスマホ対応の明記はない | https://support.google.com/gemini/answer/15229592?hl=en |
| 4-1 無料の代わり②（旧 Workspace Labs） | Google Workspace Experiments（2026年3月10日に改名） | 申し込むと、試験中の機能を先に使える：Gmail・ドキュメント・スプレッドシート・スライドのサイドパネル、ドライブの「Ask Gemini」、Meet の「Take notes for me」など。日本語と日本に対応 | 18歳以上で、自分で管理する個人アカウントが条件。料金は公式に書かれていない（わからない）。品質・提供状況は変わることがある | わからない | https://support.google.com/docs/answer/13447104?hl=en ・ https://support.google.com/docs/answer/13607340?hl=en |
| 4-2 主要な5つの活用パターン | Google の公式な区分ではなく、本の著者の分け方 | わからない（本文なし） | ― | ― | ― |
| 4-3 サイドパネルでの Gem 活用 | 「Gems in the side panel」 | Gemini アプリで作った Gem を、Gmail・ドキュメント・スプレッドシート・スライド・ドライブのサイドパネルから呼び出せる | 2025年7月の公式発表では、サイドパネルを使える **Workspace 顧客** 向け。個人の有料プランで使えるかはわからない。Gem を作ること自体は Gemini アプリで無料 | サイドパネルはパソコンのブラウザ（ウェブ）の機能 | https://workspaceupdates.googleblog.com/2025/07/gems-in-the-side-panel-of-google-workspace-apps.html |
| 4-4 Gmail × Gemini | AI Overview（スレッド要約）／Help me write／Suggested Replies／Proofread／AI Inbox／Gmail Live | 長いメールの上に要約カードが出る。指示文からメールの下書きを作れる | **スレッド要約は無料・全世界・日本語対応。** Help me write と Suggested Replies の無料提供は米国のみ。ほかは AI Plus / Pro / Ultra。※ヘルプのページ同士で記述が食い違う（下の注を参照） | ウェブ・iOS・Android（機能ごとに違う） | https://support.google.com/mail/answer/16831098?hl=en |
| 4-5 スプレッドシート × Gemini | Gemini in Sheets サイドパネル／AI function／Fill with Gemini | 指示文から表を作る。データの分析や分類をさせる | AI Pro / Ultra。Experiments に AI function とサイドパネルあり | わからない | 上の personal プラン表 ・ https://blog.google/products-and-platforms/products/workspace/gemini-workspace-updates-march-2026/ |
| 4-6 ドキュメント × Gemini | Gemini in Docs サイドパネル／Help me write／Help me create | 文書の要約・下書き・書き直し。「Match writing style」で文体をそろえる | AI Pro / Ultra。Experiments にもあり | わからない | 同上 |
| 4-7 ドライブ × Gemini | Ask Gemini in Drive／AI Overviews in Drive／PDF の要約カード | 複数のファイルをまたいで質問に答える | AI Pro / Ultra。Experiments にもあり | わからない | 同上 |
| 4-8 スライド × Gemini | Gemini in Slides サイドパネル（スライド生成・画像生成） | 指示文から編集できるスライドや画像を作る | AI Pro / Ultra。Experiments にサイドパネルあり | わからない | 同上 |
| 4-9 Google Chat × Gemini | 個人向けの機能はなし | ― | 個人アカウントでは提供なし | ― | https://support.google.com/mail/answer/13952129?hl=en&co=DASHER._Family%3DPersonal |
| 4-10 Google Meet × Gemini | Take notes for me（「Take notes with Gemini」）／翻訳字幕／Ask Gemini in Meet | 会議メモを自動で作り、ドキュメントとしてドライブに保存する。日本語対応 | AI Pro / Ultra。Experiments にもあり | Android・iOS の Meet アプリで使える | https://support.google.com/meet/answer/14754931?hl=en&co=GENIE.Platform%3DAndroid |

**注（Gmail の食い違い）：** プラン別の表（13952129）では、Help me write とスレッド要約は「AI Plus / Pro / Ultra」とされています。一方、Gmail の機能ヘルプ（16831098）では「スレッド要約は Global で無料」とされています。日本の学生の無料アカウントで実際に要約カードが出るかは、**実機で確かめる必要があります。**

### 第5章 NotebookLM（現在の名前は Gemini Notebook）

| 節 | いまの名前 | できること（授業での操作） | 無料 | スマホ | 出典 |
|---|---|---|---|---|---|
| 5-1 NotebookLM とは（操作・チャット・メモ・Studio・関連情報の追加） | **Gemini Notebook**（2026年7月16日に改名。アプリは別のまま、機能の変更なし） | PDF・ウェブ・YouTube・音声を資料として追加し、資料に基づいてチャットする。Studio で音声解説・動画解説・フラッシュカード・クイズ・インフォグラフィック・スライド・マインドマップを作る。Fast research / Deep Research で資料を探して追加する | 無料（Standard）：ノートブック100個、資料は1冊50件、チャット50回/日、音声解説3回/日、動画解説3回/日、レポート・フラッシュカード・クイズ・マインドマップ各10回/日、Deep Research 10回/月。有料は Plus / Pro / Ultra。個人アカウントは年齢確認が必要で、18歳未満は一部の機能が制限される | 専用アプリあり（Android 10以上、iOS）。音声解説はオフライン再生できる | https://workspaceupdates.googleblog.com/2026/07/notebooklm-now-gemini-notebook.html ・ https://support.google.com/notebooklm/answer/16213268?hl=en ・ https://support.google.com/gemininotebook/answer/16296687 |
| 5-2 共有機能 | 共有／公開ノートブック（「リンクを知っている全員」）／チャットだけ見せるリンク | 「共有」から相手を指定するか、公開リンクを出す。「Copy link to chat view」でチャット画面だけを見せる（ただし資料が完全に隠れるわけではない） | 個人アカウントは最大50人まで。Google グループには共有できない。公開共有は個人アカウントだけの機能 | わからない | https://support.google.com/gemininotebook/answer/16206563?hl=en ・ https://support.google.com/gemininotebook/answer/16322204?hl=en |
| 5-3 3大活用シーン（個人学習・音声学習・チーム共有） | ― | 授業資料から、クイズ・フラッシュカード・音声解説を作る | 無料枠でできる | できる（アプリ） | 5-1と同じ |
| 5-4 他の AI ツールとの連携 | **Gemini アプリの「ノートブック」**（Notebooks in Gemini Apps） | Gemini アプリにノートブックを作ると、Gemini Notebook と自動で同期する。チャットと資料をまとめて扱える。スマホで何か共有するとき「Gemini Notebook」を選ぶと資料として追加できる | 2026年4月に有料ユーザーから始まり、無料ユーザーにも広がった【曖昧：無料化は報道のみ。公式ヘルプに無料か有料かの記載なし】。一部の機能は「アクティビティを保持」をオンにする必要あり | ウェブと Gemini モバイルアプリの両方で使える | https://support.google.com/gemini/answer/16972047?hl=en&co=GENIE.Platform%3DAndroid ・ https://9to5google.com/2026/04/17/gemini-notebooks-free/【曖昧】 |

### 第6章 組織での AI 導入

| 節 | いまの名前 | できること | 無料 | スマホ | 出典 |
|---|---|---|---|---|---|
| 6-1 なぜ組織で AI 活用が求められるか | 製品の機能ではない（考え方の節） | 本文がないため中身はわからない | ― | ― | ― |
| 6-2 社内導入の2つのサイクル | 同上 | 同上 | ― | ― | ― |
| 6-3 社内展開を成功させる8つのポイント | 関係する製品：Google Workspace（Business / Enterprise プラン） | 報道によると、2025年1月から Business Standard 以上に Gemini が追加料金なしで含まれ、Business Starter は機能が限られる | 組織向けの有料契約が前提。学生の個人アカウントでは体験できない | ― | https://workspace.google.com/pricing（Gemini の中身は報道のみ【曖昧】） |

### 節ごとの結論（授業で使えるか）

- 4-1：使えない
- 4-2：使えない
- 4-3：使えない
- 4-4：一部だけ使える（スレッド要約のみ、実機で要確認）
- 4-5：使えない
- 4-6：使えない
- 4-7：使えない
- 4-8：使えない
- 4-9：使えない
- 4-10：使えない
- 5-1：使える
- 5-2：使える
- 5-3：使える
- 5-4：使える
- 6-1：使える（考え方の講義として）
- 6-2：使える（考え方の講義として）
- 6-3：使えない（実際に触る体験はできない。講義として話すだけなら可能）

4-5〜4-10 は、18歳以上の学生なら Workspace Experiments に申し込めば使える可能性があります。ただし料金とスマホ対応が確かめられていないので、「使えない」としました。第4章の代わりに授業でできることは次の2つです。
- **Gemini アプリの Workspace 連携：** Gmail やドライブの要約をスマホで扱う（無料かどうかはヘルプで未確認）。
- **Gem：** Gemini アプリで作る（無料）。
