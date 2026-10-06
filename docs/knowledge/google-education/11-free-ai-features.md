取得日: 2026-09-28

# 無料プランで使える便利機能（Gemini アプリ・ChatGPT・Notion・Canva）

前提は、成人の学生が**個人アカウント・無料プラン・スマホ**で使う授業。根拠は公式ページだけで、各行に直リンクを付けた。公式ページで確認できなかった点には【曖昧】を付け、記憶や推測では埋めていない。

## 根拠の取り方と限界

- Gemini: gemini.google と support.google.com/gemini の本文を直接読んだ。
- ChatGPT: help.openai.com・openai.com・chatgpt.com は、この環境から本文を取得すると **HTTP 403** になった。そのため ChatGPT の行は、help.openai.com に絞った検索結果に出た**公式ヘルプの抜粋**だけを根拠にしている。検索エンジンが古い版の抜粋を返している可能性もあるので、授業の前には各リンクを開き、今の記載を確かめる。数値には「（抜粋）」と付けた。
- Notion: notion.com の本文を直接読んだ。
- Canva: canva.com もこの環境からは 403 だった。canva.com に絞った検索結果に出た公式ヘルプの抜粋だけを根拠にしている（ChatGPT と同じ扱い）。
- 無料枠は各社が予告なく変えることがある。Gemini のヘルプにも「プランをご利用のユーザーよりも先に、制限が適用されることがあります」と書かれている。[Gemini 上限](https://support.google.com/gemini/answer/16275805?hl=ja)

## 1. Gemini アプリ（無料・個人アカウント）

共通条件: 無料プランは「標準の上限」で、有料プランの上限は Plus が2倍、Pro が4倍。コンテキストウィンドウは無料が **32,000 トークン**（Plus は 128,000、Pro と Ultra は 100 万）。[Gemini 上限](https://support.google.com/gemini/answer/16275805?hl=ja)
無料で使えるモデルは「3.6 Flash」と「3.1 Pro（アクセスは変動）」。[プラン比較](https://gemini.google/subscriptions/)

| 機能名 | 何ができるか | 無料での上限・条件 | スマホアプリ | 授業での使い道（ビジネスの場面） | 罠 |
|---|---|---|---|---|---|
| [画像生成・編集](https://support.google.com/gemini/answer/14286560?hl=ja&co=GENIE.Platform%3DAndroid) | 文章から画像を作る。アップロードした画像の編集や、複数の画像の合成もできる | 無料で使えるのは Nano Banana 2（Pro は有料プランだけ）。1日の上限はあるが、数値は書かれていない。**生成と編集は18歳以上**。無料では「画像の再生成（Nano Banana Pro）」は使えない。[上限表](https://support.google.com/gemini/answer/16275805?hl=ja) | ○（Android のヘルプに手順がある） | 広告バナー案や SNS 投稿画像のラフを作る | 作った画像には見えない **SynthID** が必ず残る。見える透かしを消せるのは、少なくともインド・韓国・ベトナムでは AI Ultra だけ。日本では【曖昧】。[透かし](https://support.google.com/gemini/answer/17405358?hl=ja&co=GENIE.Platform%3DAndroid) 第三者の権利を侵害しない、という注意書きがある |
| [Deep Research](https://support.google.com/gemini/answer/15719111?hl=ja&co=GENIE.Platform%3DAndroid) | 多数のソースを調べてレポートにする。調査プランを編集できる。Google ドキュメントへの書き出しや音声解説にも対応 | 無料でも使える（上限表でチェックあり）が、「需要が高い期間には利用できないことがあります」。**18歳以上**。1本に通常5〜10分かかる。[上限表](https://support.google.com/gemini/answer/16275805?hl=ja) | ○ | 競合調査や市場概況のたたき台を作る | 既定では Google 検索がソースになるので、出典を1本ずつ開いて確かめる。空く時間を待てない授業では使えないことがある |
| [Canvas](https://support.google.com/gemini/answer/16047321?hl=ja&co=GENIE.Platform%3DAndroid) | ドキュメント、アプリ、スライド、コードを作って編集する。音声解説・クイズ・インフォグラフィックへの変換や、Google ドキュメントへの書き出しもできる | 無料（上限表でチェックあり）。作成機能の多くは18歳以上 | △: 使えるが、**文字の書式を編集できるのはパソコンのウェブ版だけ**。共有された Canvas はモバイルアプリで開けない | 企画書の下書き、提案スライドの骨子づくり | 共有リンクを受け取った人がスマホだけだと開けない |
| Gem の利用（[Android](https://support.google.com/gemini/answer/15146780?hl=ja&co=GENIE.Platform%3DAndroid) / [iPhone](https://support.google.com/gemini/answer/15146780?hl=ja&co=GENIE.Platform%3DiOS)） | 指示を決めておいたカスタム AI を呼び出す | 無料（上限表でチェックあり）。13歳以上 | 使うのは○。**作成・編集・削除はウェブアプリだけ** | 教員がウェブで作った「添削役 Gem」を学生がスマホで使う | Gemini Live では Gem を使えない。学生がスマホだけで Gem を作る課題は出せない |
| [ファイル・画像の読み込み](https://support.google.com/gemini/answer/14903178?hl=ja) | PDF や画像などを読み込んで質問する | 1回のプロンプトで最大10ファイル。動画は1ファイル2GBまで、それ以外は100MBまで。動画は合計5分まで、音声は合計10分まで（有料プランで拡張）。コンテキストは32,000トークン | ○（ヘルプに Android・iPhone のタブがある） | 配布資料や求人票を読ませて要約させる | 32,000トークンを超える長い資料は、全体を読めない可能性がある【曖昧: 超えたときの挙動は書かれていない】 |
| [音声会話（Gemini Live）](https://support.google.com/gemini/answer/15274899?hl=ja&co=GENIE.Platform%3DiOS) | 声で自然に会話する | 無料プランに含まれる。[プラン比較](https://gemini.google/subscriptions/) | ○（**ウェブアプリでは使えない**） | 面接練習、商品説明のロールプレイ | Gem を使えないので、役を設定して練習させたいなら毎回口頭で指示する。録音する前に相手の同意を取る |
| カメラで見せる・画面共有（[Live](https://support.google.com/gemini/answer/15274899?hl=ja&co=GENIE.Platform%3DAndroid)） | Live の最中にカメラや画面を見せて相談する | 無料で使えるかは明記がない【曖昧】。画面共有には Live の通知をオンにする必要がある | ○（スマホ前提） | 店頭 POP や売り場を撮って改善案を聞く | ミュートにしてもカメラと画面共有は続く。「アクティビティを保存」がオンなら、映像も履歴に保存される |
| [Google 検索との連携（回答を再確認）](https://support.google.com/gemini/answer/14143489?hl=ja&co=GENIE.Platform%3DAndroid) | 回答の記述を Google 検索と照らし合わせ、緑やオレンジで色分けする | 無料での条件は明記がない【曖昧】 | ○ | ファクトチェックの手順を身につける | ヘルプ自身が「ダブルチェック機能に誤りが生じる可能性」があると書いている。緑でも正しいとは限らない |
| [YouTube・マップ等のアプリ連携](https://support.google.com/gemini/answer/13695044?hl=ja&co=GENIE.Platform%3DAndroid) | 検索・マップ・フライト・ホテル・YouTube の公開情報を使う。Gmail などとの連携も | **「アクティビティを保存」がオフだと使えない**。[YouTube](https://support.google.com/gemini/answer/16622858?hl=ja&co=GENIE.Platform%3DAndroid) も同じ条件。無料かどうかの明記はない【曖昧】 | ○ | 店舗の商圏を調べる、解説動画を探して要点を聞く | 履歴を残したくない学生が保存をオフにすると使えなくなる。YouTube の再生履歴や再生リストの操作には対応していない |
| Gemini Notebook との関係（[ノートブック](https://support.google.com/gemini/answer/16972047?hl=ja)） | Gemini アプリのノートブックが Gemini Notebook（旧 NotebookLM。2026年7月16日に改称。[blog](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/)）と自動で同期する | 個人アカウントだけ（仕事用・学校用は不可）。ソースは「Google AI プランに基づいて最大600個」。無料ユーザーへの提供は「予定」と書かれた時期があり、現状は【曖昧】。[blog](https://blog.google/innovation-and-ai/products/gemini-app/notebooks-gemini-notebooklm/) | ウェブとモバイル | 授業資料を1つのノートブックにまとめる | 無料の Gemini Notebook の上限は [06](06-notebooklm-gemini-notebook.md) を参照（音声解説は1日3回など） |
| 動画生成 | 動画を作る | **無料では使えない**。[上限表](https://support.google.com/gemini/answer/16275805?hl=ja) | - | - | 学生が無料アカウントで動画を作る課題は組めない |

## 2. ChatGPT（無料・個人アカウント）

年齢: 13歳以上。18歳未満は保護者の許可が必要。[利用規約](https://openai.com/policies/row-terms-of-use/)
国によっては無料プランに広告が表示されることがある（抜粋）。[Free FAQ](https://help.openai.com/en/articles/9275245-chatgpt-free-tier-faq)

| 機能名 | 何ができるか | 無料での上限・条件 | スマホアプリ | 授業での使い道 | 罠 |
|---|---|---|---|---|---|
| [無料で使えるモデル](https://help.openai.com/en/articles/9275245-chatgpt-free-tier-faq) | 日常の文章チャット | 既定は **GPT-5.6 Luna** で、テキストチャットは無制限（不正利用防止の制限あり）。難しい質問には「Think」ボタンを使う（抜粋）。GPT-5.5 は「5時間に10メッセージ、超えると mini 版」と書かれた版もあり、現行かどうかは【曖昧】。[モデル](https://help.openai.com/en/articles/11909943-gpt-5-in-chatgpt) | ○（Think はモバイルアプリで提供され、ウェブへは順次）（抜粋） | 文案づくり、壁打ち | モデルは予告なく切り替わる。同じ指示でも時期によって質が変わる |
| [検索](https://help.openai.com/en/articles/9237897-chatgpt-search) | ウェブを検索して出典付きで答える | 無料で使える。ログアウト中でも使える（抜粋） | ○（iOS・Android では地図が出ることもある）（抜粋） | 最新ニュースや価格の確認 | 出典リンクの中身と回答が一致しているかは自分で確かめる |
| [画像生成](https://help.openai.com/en/articles/6696591-what-are-the-rate-limits-for-image-generation) | 文章から画像を作る | 無料でも使えるが、別の上限がある。回数は【曖昧】（明記を確認できなかった） | 【曖昧】 | 広告ラフ | 上限に達したら通知が出る。班の全員が同時に作ると足りなくなる可能性がある |
| [ファイル読み込み](https://help.openai.com/en/articles/8555545-file-uploads-faq) | PDF・表・画像を読む | 無料は**1日3ファイル**（抜粋）。1ファイル512MBまで、文書は200万トークンまで、画像は20MBまで。ライブラリの容量は500MB | 【曖昧】 | 資料の要約 | 1日3ファイルしか使えないので、1コマで何度も試すと枠が尽きる |
| [音声モード](https://help.openai.com/en/articles/20001274-chatgpt-voice) | 声で会話する | 無料で使える。テキストとは別の上限があり、1日の時間が決まっている。「1日2時間」という記載はフィリピン語版の抜粋でしか確認できず【曖昧】 | ○（アプリのヘッドホンアイコンから） | 英語面接の練習 | 上限に達すると機能が落ちる、と書かれている |
| [Canvas](https://help.openai.com/en/articles/9930697) | 文章やコードを横のパネルで共同編集する | 無料・有料とも使える（抜粋） | 【曖昧】（「モバイルは今後」と書かれた古い抜粋しか見つからない） | 企画書の推敲 | スマホで開けるかどうかは授業の前に実機で確かめる |
| [GPTs の利用](https://help.openai.com/en/articles/8554397-creating-a-gpt) | 他の人が作ったカスタム GPT を使う | 共有された既存の GPT は使える。**個人アカウントは Free・Go・Plus・Pro のどれも、新しい GPT を作ることも公開することもできない**（抜粋）。OpenAI はカスタム GPT の廃止を予定している | 【曖昧】 | 教員が用意した GPT を使わせる案は**不可に近い**（教員も個人アカウントなら作れない） | [廃止 FAQ](https://help.openai.com/en/articles/20001519) の日程しだいで、授業期間中に使えなくなる恐れがある |
| [プロジェクト](https://help.openai.com/en/articles/10169521-projects-in-chatgpt) | チャットとファイルを案件ごとにまとめる | ログインしたユーザーが使える。ただし「プランによる」。無料で入れられるファイル数は【曖昧】 | 【曖昧】 | 科目ごとにチャットを整理する | ファイルの1日3件の上限はプロジェクトの中でも共通 |
| [メモリ](https://help.openai.com/en/articles/8590148-memory-faq) | 好みや前提を覚えさせる | 無料は「保存したメモリ」だけ（抜粋）。改善版を Free と Go に順次展開中 | ○ | 自分の学科や目標を覚えさせる | 覚えた内容が以後の回答を変える。課題の比較をするときはオフにしておく |
| [データ分析](https://help.openai.com/en/articles/8437071-data-analysis-with-chatgpt) | CSV や表を読み、Python で集計してグラフにする | 無料でも使えるが、有料より上限が厳しい（抜粋）。回数は【曖昧】 | 【曖昧】 | 売上 CSV から傾向をつかむ | 集計に使ったコードが見えるので、集計の条件を必ず確かめる |
| [Deep research](https://help.openai.com/en/articles/10500283-deep-research-in-chatgpt) | 長い調査レポートを作る | 無料で使えるか、何回までかを確認できなかった【曖昧】 | 【曖昧】 | - | 無料で使える前提の課題は組まない |

## 3. Notion（無料プラン）

| 機能名 | 何ができるか | 無料での上限・条件 | スマホアプリ | 授業での使い道 | 罠 |
|---|---|---|---|---|---|
| [無料プランの上限](https://www.notion.com/pricing) | ページとデータベースで情報を整理する | 個人ならブロック数は無制限、2人以上だと制限がある。アップロードは**1ファイル5MBまで**。ゲストは10人まで。ページ履歴は7日。グラフは1つ。基本的なフォーム | - | 班の企画ノート | 2人以上のワークスペースにするとブロック数の制限がかかる。1人1ワークスペースにしてゲストで招く運用が無難 |
| [Notion AI](https://www.notion.com/help/complimentary-ai-responses) | 文章の生成・編集、自動入力、質問への回答 | 無料プランは「お試しの回数」だけ。**回数は書かれていない【曖昧】**。回数はワークスペースで共有し、「Try again」も1回と数える。使い切ると有料プランへの変更が必要 | ○（ホーム画面のウィジェットから AI チャット・カメラ・音声を使える）[mobile](https://www.notion.com/help/notion-for-mobile) | 議事録の要約を1回だけ試す | 授業で何度も使うと、すぐに枠がなくなる |
| [ページの公開](https://www.notion.com/help/public-pages-and-web-publishing) | ページを notion.site で公開する | 無料でも公開できる。URL の変更、独自ドメイン、Google Analytics は使えない | 【曖昧】（明記なし） | ポートフォリオの公開 | **公開したページのメタデータに、編集した人の名前・写真・メールアドレスが含まれる**。サブページも一緒に公開される。検索エンジンへの掲載は設定でオンにする |
| [ゲスト招待](https://www.notion.com/help/add-members-admins-guests-and-groups) | ページ単位で外部の人をメールアドレスで招く | ゲストは10人まで（[料金](https://www.notion.com/pricing)） | 【曖昧】 | 教員をゲストに招いて提出物を見てもらう | ゲストに付けた権限（閲覧・コメント・編集）を確認する |
| データベース（[料金](https://www.notion.com/pricing)） | サブタスク、依存関係、独自プロパティ | 無料でも使える。グラフは1つまで | ビューの切り替えは○。[mobile](https://www.notion.com/help/notion-for-mobile) | 顧客リストや課題管理 | - |
| [スマホアプリ](https://www.notion.com/help/notion-for-mobile) | 閲覧、編集、コメント、@メンション、画像の挿入 | - | ○ | - | **段組み（カラム）は1列に崩れて表示される**。設定の多くはデスクトップ版にしかない |

## 4. Canva（無料版）

| 機能名 | 何ができるか | 無料での上限・条件 | スマホアプリ | 授業での使い道 | 罠 |
|---|---|---|---|---|---|
| [サイズ変更（Magic Resize／Magic Switch）](https://www.canva.com/help/resize/) | 1つのデザインを別のサイズにまとめて変換する | **無料版では使えない**（Pro・Teams・Education などだけ）（抜粋） | - | - | 「インスタ用とチラシ用を同時に作る」課題は、無料版では手作業になる |
| [ブランドキット](https://www.canva.com/help/color-palettes/) | ブランドの色などを登録する | 無料版はカラーパレット1つ、**3色まで**（抜粋） | 【曖昧】 | 架空ブランドの3色を決める | フォントのアップロードは無料版ではできない（[pricing](https://www.canva.com/pricing/) の抜粋） |
| [AI 画像生成（Dream Lab／Magic Media）](https://www.canva.com/help/ai-access/) | 文章から画像や動画を作る | 無料版にも毎月の AI 利用枠がある。**回数は書かれていない【曖昧】**。上限に達すると、生成と生成の間に短い待ち時間が入る（抜粋） | 【曖昧】 | 広告ビジュアルのラフ | 「使える回数」を前提に授業を組めない |
| [有料素材の見分け方](https://www.canva.com/help/premium-elements/) | - | サムネイルの右下に**王冠マーク**があるものが有料。無料版では透かし（格子状の模様）が入り、外すにはデザインごとにライセンスを買う（抜粋） | ○（同じ表示と思われるが明記なし【曖昧】） | 著作権・ライセンス教育の教材 | 透かしに気づかないまま提出する。同じ素材でも、別のデザインで使うときは再購入が必要 |
| [アップロード容量](https://www.canva.com/help/manage-uploads/) | 自分の素材を置く | 5GB（抜粋） | - | - | - |
| スマホアプリ（[resize ヘルプ](https://www.canva.com/help/resize/)） | デザインの編集 | 無料で使える（抜粋）。スマホでできない操作の一覧は見つからなかった【曖昧】 | ○ | - | - |

## まとめ: 学生（成人・個人・スマホ・無料）で使えるか

| 使える | 危うい |
|---|---|
| Gemini: Live での会話・カメラ、ファイル読み込み（10件・32Kトークン）、Gem の利用、Deep Research（混雑時は除く）、画像生成 | Gemini: Gem の作成（ウェブのみ）、Canvas の書式編集や共有物を開くこと（ウェブのみ）、動画生成（無料は不可）、アプリ連携（「アクティビティを保存」がオンでないと不可）、ノートブック（無料への提供は【曖昧】） |
| ChatGPT: 文章チャット（Luna）、検索、音声 | ChatGPT: ファイル（1日3件）、画像生成・データ分析・Deep research（回数不明）、Canvas・プロジェクトのスマホ対応（【曖昧】）、GPTs（個人では作れず、廃止予定） |
| Notion: 閲覧・編集・データベースのビュー、ページの公開 | Notion: AI（お試しの回数だけ）、5MB の壁、公開ページからのメールアドレス露出、段組みの崩れ |
| Canva: 無料素材での編集、3色のブランドキット | Canva: サイズ一括変換（無料は不可）、王冠素材の透かし、AI の回数不明 |

## 再現性: 同じ課題を Gemini と ChatGPT にやらせたときの違い

1. 動いているモデルも上限も各社が随時変えるので、同じ指示でも実施した日やアカウントによって出力が変わる。授業では、使ったモデル名と日時を提出物に書かせる。
2. 調べ物の出典が違う。Gemini は既定で Google 検索を使い、ChatGPT は ChatGPT search を使う。出典が違えば結論も数値もずれうる。
3. 手元の文脈が違う。ChatGPT のメモリや、Gemini の「アクティビティを保存」とアプリ連携の設定によって、同じ指示でも個人ごとに回答が変わる。比較するときはメモリをオフにし、設定をそろえる。
4. 無料枠が尽きたときの振る舞いが違う。Gemini は混雑時に機能そのものが使えなくなり、ChatGPT は軽いモデルに落ちたりファイル枠が尽きたりする。班ごとに条件がばらつきやすい。
5. 読み込める量が違う。Gemini の無料版は32,000トークン、ChatGPT は1ファイル200万トークン（抜粋）。同じ長さの資料でも、読めた範囲が違う可能性がある。
