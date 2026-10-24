# Mynavi TechTus面接準備：質問集と対話練習の始め方

まずはQ01の自己紹介を、日本語で60秒程度話すか、そのまま文章にしてください。回答をもとに、内容の確認、添削、英語での練習を進めます。

- [ChatGPTへ渡す引継ぎファイル](claude_21-13-33_chatgpt_handoff.md)：この1ファイルで背景、経歴、90通りの出題、添削方法を引き継げます。
- [回答メモ](claude_21-13-33_answer_notes.md)：必要なときに下書きと練習結果を残せます。

作成・調査日：2026-10-15。質問の文言は、以下の資料に載る質問・評価領域を、今回の事情と職務経歴に合わせて組み直したものです。

## 今回、優先して準備すること

準備の中心は12テーマです。対話用には追加6テーマも含め、主質問54通りと深掘り36通りを用意しました。90個の回答を別々に暗記する必要はありません。同じ経験を、違う聞かれ方でも説明できるように練習します。

今回の日本人・役割未定の面談について、実際に出た過去問や評価表は確認できませんでした。必須・追加は準備の優先順位です。出題の確率や確定情報を表すものではありません。

| 分かっていること | 未確認のこと |
|---|---|
| エージェントの紹介を受け、会社側が宇野さんの経歴に関心を持った | 職種、役職、具体的な担当、採用枠・予算 |
| 現地エンジニアとは英語。社長とは日本語で話せる | 出席者、時間配分、技術テスト・コーディングの有無 |
| 条件と働き方が合えば検討する段階 | 報酬、現地での勤務条件、入社・赴任時期 |
| 準備が進んだら日程を連絡する方針 | 面接日は未確定。「来週以降」はLINE上の調整方針 |

一般的なカジュアル面談では、転職理由、転職をどの程度具体的に考えているか、今後の関心も話題になります。今回は英語での技術的な質疑も予告されているため、相互理解と技術説明の両方を準備します。「カジュアルなので技術評価はない」とは判断しません。[dodaのカジュアル面談解説](https://doda.jp/engineer/guide/it/032.html)

## 企業研究から質問へつなげた点

1. 公式日本語サイトはWeb・モバイル・業務システム開発と、APOによる日本側との意思疎通を説明しています。開発経験と要求の認識合わせを話す材料になります。[公式サイト](https://mynavitechtus.com/jp/)
2. 英語のFull-stack Engineerの公開求人には、保守性、設計、リスク・トレードオフの説明が記載されています。非同期処理や段階的なコード改善の説明を準備する根拠にしました。この求人には「Vietnamese nationality」とあり、宇野さん向けの求人ではありません。[公開求人](https://mynavitechtus.com/careers-at-mynavi-techtus-vietnam/full-stack-engineer/)
3. ベトナム語のAPO Leaderの公開求人には、要求整理、技術説明、調整、育成が記載されています。技術とコミュニケーションのどちらを任されるか、確認する価値があります。今回APOとして採用されるという意味ではありません。[APO Leader](https://mynavitechtus.com/vi/jobs/apo-leader/)
4. 公式日本語サイトは、生成AIの活用と人によるレビュー・テストを掲げています。AI利用を聞かれた場合の検証方法も、対話用の質問に含めました。[開発体制の説明](https://mynavitechtus.com/jp/)

ここから、「技術経験に加え、日本側と現地チームの間でどう働きたいかを聞かれる可能性がある」と推定しました。具体的な役割と本人の希望を照合するための推定であり、募集要件の断定ではありません。

## 回答に使う経歴と、混同しない点

主に、本人指定の[職務経歴書PDF](C:/Users/ukowu/Downloads/【レバテック】職務経歴書_宇野.pdf)と、[ラクス応募資料の索引](C:/Users/ukowu/Desktop/travel/jobs/rakus/DOCUMENT_INDEX.md)、そこから参照される事実メモ・面接相談メモを使いました。PDFは2026年7月29日現在の内容です。直近の状態は、回答作成時に更新します。

| 使える題材 | 回答で区別すること |
|---|---|
| IoT／RFIDのWeb開発。Java、Python。画面、サーバー、機器連携 | 入社は2022年4月、Web開発は2022年10月から。Javaの使用期間とWeb開発全体の期間は別 |
| 自動検品の非同期制御、タグ発行の状態管理と責務分割 | 異なる機能・時期の話を一つの改善として混ぜない。約300行の分離を約3,000行全体の刷新としない |
| 保全部品管理のフローチャートとPM経由の仕様確認 | 要件定義全体・直接の顧客交渉全体を担当したとはしない |
| 新人1名への約3か月・3サイクル・約25回のレビュー | 正式な管理職、複数人の組織管理、教育方法をすべて独力で考案した実績へ広げない |
| イタリア子会社の技術者との約2週間の英語での確認 | 日常的な大規模交渉の経験や、現在の英語の流暢さを証明したものとはしない |

追加で注意したいのは次の点です。

- テストのカバレッジ80％は、問題が起きやすい一部のメソッド群についての記録です。システム全体の達成率にはしません。テスト標準化の試行も、継続運用が定着した実績にはしません。[事実メモ・P0-5](C:/Users/ukowu/Desktop/travel/jobs/rakus/persoal_information/company_pc_interview_notes.md)
- RFID案件のシステムテストと本番リリースは別担当です。旧IoT案件では本人のリリース経験があります。案件ごとに工程を説明します。
- 2026年9月のリリース予定は、7月時点の予定です。完了・延期・現在の担当を確認するまで、リリース済みとは書きません。
- Spring Boot、React、Jenkins構築、クラウド全体設計などを、現在の確定した実務経験に足しません。古い別用途のAI草稿は根拠に採用していません。
- ラクス向け資料には、キャリア目標が本人の本意と合うかへの違和感と、弱みが未確定との記録があります。今回の役割や志望理由は、本人の言葉で確認します。[面接相談メモ](C:/Users/ukowu/Desktop/travel/jobs/rakus/meeting/面接回答たたき台_エージェント相談.md)

## 自己紹介の作成指示

職務経験を中心に、名前、経歴の概要、強みを示す事例、今回の面談につながる一言を短くまとめます。日本語の自己紹介は約1分を目安にする解説があり、今回はそこを練習の出発点にします。[dodaの自己紹介解説](https://doda.jp/guide/mensetsu/interview/001.html)

1. 名前と現在の会社・仕事内容を述べる。
2. 主な技術と自分の担当範囲を述べる。
3. 深掘りしてほしい工夫を1つ述べる。
4. 今回の面談で話したいことを短く添える。

初稿では、次の空欄だけ埋めれば十分です。

> 宇野拓磨と申します。現在、村田製作所で［どのような利用者のための、どのようなシステム］を開発しています。主に［技術と担当範囲］を担当しています。最近は［工夫と結果を1つ］に取り組みました。今回は［関心のある仕事、または確認したい役割］についてお話を伺えればと思っています。

英語は同じ内容を短い文にします。45〜60秒は今回の練習目標で、会社からの指定ではありません。

> My name is Takuma Uno. I work at Murata Manufacturing, developing [type of system]. My main responsibilities are [your responsibilities], using [technologies]. One example of my work is [one concrete example]. I would like to learn more about [the role or work you want to discuss].

趣味は海外に関心を持った理由として話せます。職務中心の自己紹介では必要な経歴を先に置き、海外勤務の理由を聞かれたときに詳しく話す構成です。本人にない「社会貢献の使命」や「会社への強い憧れ」は加えません。

## まず準備する12テーマ

各テーマでは、最初に短く答え、深掘りされたら具体例を足します。事例は「状況・課題→自分の行動→結果・学び」で整理できます。STARもこの整理に使えます。[AmazonのSTAR解説](https://amazon.jobs/content/en/how-we-hire/interview-loop)

### Q01 自己紹介・職歴の要約

**質問**：現在の仕事を中心に、簡単に自己紹介してください。

> Could you briefly introduce yourself, focusing on your current work?

- 用意する材料：村田製作所に2022年4月入社。2022年10月からIoT・RFIDのWeb開発。Java／Python、画面とサーバー側を担当。強みを示す事例は1つに絞る。
- 回答の組み立て：名前・現在の仕事→担当範囲→代表的な工夫1つ→今回話したいこと。日本語60秒、英語45〜60秒を練習目標にする。
- 深掘り例：Which part of that work did you personally own?
- 根拠：資料に掲載された質問テーマ。[J2](https://doda.jp/guide/mensetsu/interview/001.html)・[J1](https://doda.jp/engineer/guide/it/004.html)

### Q02 代表案件・構成・自分の担当

**質問**：代表的な開発案件を、構成と担当範囲が分かるように説明してください。

> Walk me through a representative project, including the architecture and your responsibilities.

- 用意する材料：RFID共通機能、顧客向け保全部品管理、旧IoT基盤は別案件。ひとつを選び、画面・サーバー・DB・機器の関係と自分の担当を説明する。
- 回答の組み立て：何をするシステムか→構成→自分の担当→制約→結果。チーム全体の仕事と本人の仕事を区別する。
- 深掘り例：How did data move between the user interface, the backend, and the devices?
- 根拠：資料の案件説明を職務経歴に具体化。[J1](https://doda.jp/engineer/guide/it/004.html)・[V3](https://itviec.com/blog/cau-hoi-phong-van-mobile-developer/)

### Q03 難しい技術課題・設計判断

**質問**：最も難しかった技術課題と、解決方法を教えてください。

> What was a difficult technical problem you worked on, and how did you approach it?

- 用意する材料：自動検品の非同期順序制御、タグ発行画面のViewState・状態別クラス・Strategy。約300行の分離は約3,000行の画面クラスの一部。別機能・別時期の話を混ぜない。
- 回答の組み立て：困っていた現象→選択肢→選んだ理由→本人の変更→確認できた結果。速度改善率やバグ削減率は作らない。
- 深掘り例：What alternative did you consider, and why did you not choose it?
- 根拠：設計・問題解決の質問を職務経歴に具体化。[E1](https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing)・[C2](https://mynavitechtus.com/careers-at-mynavi-techtus-vietnam/full-stack-engineer/)

### Q04 品質・テスト・不具合調査

**質問**：担当した機能の品質をどのように確認しましたか。

> How did you verify the quality of a feature you developed?

- 用意する材料：JUnit／JaCoCo、単体・結合テストの設計と実施。80％は限定した一部メソッド群。標準化の試行は継続定着した実績としない。
- 回答の組み立て：対象→重要な正常・異常系→実行方法→分かったこと。実際に行った方法と、今なら行う方法を分ける。
- 深掘り例：Which failure or boundary case was especially important to test?
- 根拠：テストの質問を経歴と公式の品質方針に具体化。[E1](https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing)・[V3](https://itviec.com/blog/cau-hoi-phong-van-mobile-developer/)・[C1](https://mynavitechtus.com/jp/)

### Q05 曖昧な要件・認識合わせ

**質問**：仕様に曖昧な点を見つけた経験を教えてください。

> Tell me about a time you found ambiguity in a specification.

- 用意する材料：保全部品管理で例外条件をフローチャート化。PMを窓口に確認し約3回の往復で修正。本人が要件定義全体や顧客交渉全体を主導したとはしない。
- 回答の組み立て：曖昧だった点→可視化したもの→誰にどう確認したか→変更点。
- 深掘り例：How did you communicate the exception without bypassing the agreed contact person?
- 根拠：要求整理の職務情報を経歴に具体化。[C3](https://mynavitechtus.com/vi/jobs/apo-leader/)・[J1](https://doda.jp/engineer/guide/it/004.html)

### Q06 英語での技術対話・海外協働

**質問**：英語で技術的なやりとりをした経験を教えてください。

> Tell me about a time you discussed technical work in English.

- 用意する材料：2026年2月頃、イタリア子会社の技術者と約2週間、英語で一対一の確認。更新影響、DBマイグレーション、スナップショット復旧を確認・実施し日本側へ共有。
- 回答の組み立て：相手と期間→技術的な主題→理解を確認した方法→実施・共有。現在の英語力を過去のスコアやAIの評価で決めない。
- 深掘り例：Could you give an example of a technical point you clarified?
- 根拠：協働の質問を本人の英語経験に具体化。[E2](https://www.atlassian.com/company/careers/resources/interviewing/engineering)・[C3](https://mynavitechtus.com/vi/jobs/apo-leader/)

### Q07 失敗・弱み・改善

**質問**：失敗した経験と、その後に変えたことを教えてください。

> Tell me about a mistake you made and what you changed afterward.

- 用意する材料：旧IoT基盤の初回リリース時の手戻りと、先輩の支援を受けた改善が候補。弱みは過去資料でも未確定で、勝手に選ばない。
- 回答の組み立て：自分の判断・不足→起きたこと→対処→その後に変えた行動。失敗と性格上の弱みは同じものと決めない。
- 深掘り例：What part of the outcome was within your control?
- 根拠：資料に掲載された失敗・行動事例のテーマ。[J1](https://doda.jp/engineer/guide/it/004.html)・[E4](https://amazon.jobs/content/en/how-we-hire/interview-loop)

### Q08 転職・海外・ベトナムの理由

**質問**：村田から海外への転職を検討している理由は何ですか。

> Why are you considering leaving Murata to work overseas?

- 用意する材料：昆虫採集、周辺国での魚突き、近隣国への移動のしやすさへの期待が出発点。待遇と働き方が合うなら検討。趣味を架空の職業使命へ置き換えない。
- 回答の組み立て：海外で暮らしたい理由→その中でベトナムを検討する理由→仕事として大切にしたい条件。なぜ今か・滞在期間は本人に確認。
- 深掘り例：Why is this the right time for you to consider a move?
- 根拠：海外就業資料と今回の事情から出題を推定。[E3](https://www.robertwalters.com.vn/insights/career-advice/blog/10-tips-for-starting-an-international-career.html)・[J3](https://doda.jp/engineer/guide/it/032.html)

### Q09 Mynavi TechTusへの関心

**質問**：今回、当社と話してみようと思った理由は何ですか。

> What made you interested in speaking with Mynavi TechTus?

- 用意する材料：エージェントから紹介され、会社側が経歴に関心を持った。公開情報のWeb・モバイル開発、保守性や品質への方針が経験と接続するかを本人が選ぶ。
- 回答の組み立て：紹介の経緯→公開情報で関心を持った事実1つ→自分の経験との接点→まだ確認したい点。志望度を実際より高くしない。
- 深掘り例：Which part connects most closely to your experience?
- 根拠：一般的な志望理由を企業の公式情報に具体化。[J1](https://doda.jp/engineer/guide/it/004.html)・[C1](https://mynavitechtus.com/jp/)・[C2](https://mynavitechtus.com/careers-at-mynavi-techtus-vietnam/full-stack-engineer/)

### Q10 未定の役割・貢献・今後の方向

**質問**：当社でどのような役割を担いたいですか。

> What kind of role would you like to take on here?

- 用意する材料：開発、設計改善、要求の整理、レビュー・教育は貢献候補。実装比率や調整業務への希望は未確認。正式なテックリード／PM／組織管理の経験は確認されていない。
- 回答の組み立て：いま任せられること→伸ばしたいこと→希望する担当範囲→避けたい比率や条件。過去のラクス向け目標を確定した本音として扱わない。
- 深掘り例：Which responsibilities are you ready to own now, and which would require support?
- 根拠：カジュアル面談・職務情報と役割未定の事情から推定。[J3](https://doda.jp/engineer/guide/it/032.html)・[E2](https://www.atlassian.com/company/careers/resources/interviewing/engineering)・[C3](https://mynavitechtus.com/vi/jobs/apo-leader/)

### Q11 未経験技術・学び方・入社後の適応

**質問**：未経験の技術を業務で使う必要があるとき、どう学びますか。

> How do you learn a technology you need for work but have not used before?

- 用意する材料：実務で使ったJava／Dropwizard／Hibernate、Python／Flask。Spring BootやReact、定着したGit／PR運用、クラウド設計主導の経験は確認されていない。
- 回答の組み立て：使った技術→未経験の範囲→過去に学んだ例→最初の立ち上がり方。未経験を隠して説明しない。
- 深掘り例：Can you describe a time you learned something unfamiliar for a real task?
- 根拠：学習・成長に関する資料を今回の経験差に具体化。[E2](https://www.atlassian.com/company/careers/resources/interviewing/engineering)・[C2](https://mynavitechtus.com/careers-at-mynavi-techtus-vietnam/full-stack-engineer/)

### Q12 待遇・入社時期・勤務条件

**質問**：希望する待遇を教えてください。

> What are your compensation expectations?

- 用意する材料：村田と同等の待遇かつ働き方が合えば検討。現年収、同等の定義、最低条件、退職予告期間、赴任可能日は未確認。面接日も未確定。
- 回答の組み立て：現状と希望を分ける。金額を出す前に、通貨・月額／年額・税込／手取り・賞与・住居等の比較条件をそろえる。未確定日を約束しない。
- 深掘り例：What would you include when comparing the offer with your current package?
- 根拠：海外就業・相互理解の資料と本人の条件から推定。[E3](https://www.robertwalters.com.vn/insights/career-advice/blog/10-tips-for-starting-an-international-career.html)・[J3](https://doda.jp/engineer/guide/it/032.html)

## 追加6テーマ

Q01〜Q12の練習後、役割や本番形式に合わせて増やします。英語の聞き方、別の聞き方、深掘りはすべて引継ぎファイルに入っています。

| ID | テーマ | 質問例 | 根拠 |
|---|---|---|---|
| Q13 | 育成・レビュー・リーダー経験 | 後輩に技術を教えた経験を教えてください。 | [C3](https://mynavitechtus.com/vi/jobs/apo-leader/)・[E2](https://www.atlassian.com/company/careers/resources/interviewing/engineering) |
| Q14 | 意見の違い・負荷・文化への配慮 | 技術的な意見が同僚と違ったとき、どう対応しましたか。 | [E2](https://www.atlassian.com/company/careers/resources/interviewing/engineering)・[C3](https://mynavitechtus.com/vi/jobs/apo-leader/) |
| Q15 | Java・OOP・コレクション・並行処理 | interfaceや多態性を、実際の設計でどう使いましたか。 | [V1](https://itviec.com/blog/cau-hoi-phong-van-java/) |
| Q16 | DB・Hibernate・データの整合性 | HibernateでDBにアクセスする処理を1つ説明してください。 | [V2](https://itviec.com/blog/cau-hoi-phong-van-backend/)・[E1](https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing) |
| Q17 | API・認証認可・通信失敗 | 実装したAPIの入力・出力と役割を説明してください。 | [V2](https://itviec.com/blog/cau-hoi-phong-van-backend/)・[C2](https://mynavitechtus.com/careers-at-mynavi-techtus-vietnam/full-stack-engineer/) |
| Q18 | 設計・実装の演習 | 小さなセンサーモニタリングシステムを設計するなら、何から確認しますか。 | [E1](https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing)・[C2](https://mynavitechtus.com/careers-at-mynavi-techtus-vietnam/full-stack-engineer/) |

Q18の実装演習は、本番での実施が予告されているものではありません。テストの有無が分かるまでは、経歴と希望する役割を英語で説明する練習を優先します。

## 自分から確認する5つの質問

待遇と働き方は、転職判断そのものに必要な情報です。「ホワイトですか」だけで終えず、具体的な担当と実態を聞きます。以下は、相互理解の資料と本人の条件から作成した確認項目です。[カジュアル面談の質問例](https://doda.jp/engineer/guide/it/032.html)・[海外就業で調べる条件](https://www.robertwalters.com.vn/insights/career-advice/blog/10-tips-for-starting-an-international-career.html)

| 優先 | 日本語 | 英語 |
|---|---|---|
| 1 | 今回、私の経歴のどの点に関心を持ち、どんな課題への貢献を期待されていますか。 | Which parts of my background interested you, and what problems would you hope I could help solve? |
| 2 | 想定する役割では、実装、設計・レビュー、顧客との調整の割合はどうなりますか。 | How would the role be divided among implementation, design and reviews, and client coordination? |
| 3 | 想定チームの直近の残業や休日対応は、通常時と繁忙期でどの程度ありますか。 | What have overtime and weekend work looked like recently for the team, both normally and during busy periods? |
| 4 | 想定する報酬と福利厚生の全体像を、役割と合わせて確認できますか。 | Could we discuss the total compensation and benefits package alongside the scope of the role? |
| 5 | 勤務地と入社後の立ち上がり方、海外から入社する場合の支援を教えてください。 | Could you explain the work location, onboarding process, and support for someone relocating from overseas? |

必要に応じて、直属の上司と技術判断の分担、日常の会議・文書の言語、有給取得の実態、住居・渡航・医療保険・就労手続きの支援を掘り下げます。報酬比較では通貨、月額／年額、税込／手取り、賞与、残業代等の前提を確認します。日本人の今回の役割に、公開求人の勤務時間や休暇がそのまま適用されるとは限りません。[公式APO求人の条件](https://mynavitechtus.com/vi/jobs/apo-leader/)

エージェントには事前に、「想定役割」「出席者と使用言語」「面接時間」「テストの有無」「報酬の想定範囲」を確認できると準備を絞れます。確認待ちでもQ01〜Q12の練習は進められます。

## 今日・明日の進め方

合計135分の練習枠を確保できる場合の配分案です。文章を完成させるより、短く答えて分からない点を見つけることに時間を使います。

| 日 | 練習枠 | やること |
|---|---:|---|
| 10月15日 | 20分 | Q01の日本語初稿と英語版を作り、声に出す |
| 10月15日 | 20分 | 代表案件・設計改善・仕様確認・英語協働の材料を短いメモにする |
| 10月15日 | 20分 | 海外勤務の理由、会社への関心、希望する役割、待遇の未確認点を整理する |
| 10月16日 | 25分 | 日本語でQ01〜Q12を練習する。長い箇所を短くする |
| 10月16日 | 25分 | 英語で技術経験を練習する。GPTに聞き方を変えてもらう |
| 10月16日 | 25分 | 日本語・英語を切り替える模擬面接と、逆質問を練習する |

時間が少ない場合は、Q01・Q02・Q03・Q06・Q08・Q10を先に扱います。Q09・Q12と逆質問は短い箇条書きでも用意します。回答しにくかったテーマを翌日の最初に回します。

### 英語で止まったときの表現

- “Could you rephrase the question?”：別の言い方で聞いてもらう。
- “Do you mean the technical design or my responsibilities?”：質問の対象を確かめる。
- “Let me take a moment to organize my thoughts.”：少し考える。
- “I haven't used that in production. My experience is with ...”：実務経験の範囲を伝える。
- “I don't remember the exact figure, but I can explain what I changed.”：数字を作らず、行ったことを説明する。

## ChatGPTへの渡し方

1. [引継ぎファイル](claude_21-13-33_chatgpt_handoff.md)を、対話するChatGPTに添付するか全文を貼る。
2. 「この指示で準備モードを開始してください」と送る。
3. 最初の質問に声で答える。

音声を使わず、文章で答えても進められます。引継ぎはローカルファイルの参照を前提にしていません。終了時には回答と未確認点の引継ぎメモを出すよう指定しています。

AI模擬面接の研究には、発話や自信の面で役立ったという参加者の報告があります。ただし対象20人の形成的・質的研究であり、今回の採用結果や合格率を裏付けるものではありません。AIの点数より、事実に合った回答を自分で説明できるかを確認します。[Gomezほかの研究](https://arxiv.org/abs/2506.16542)

## 調べた資料と質問の根拠

資料に出る評価テーマと本人の経験を対応させました。ベトナム語の記事は、ベトナムのIT人材向けに公開された質問領域の参考です。日本語面接との差や、国全体の採用慣行については判断していません。技術記事は出題される領域を調べるために使いました。

### 企業の公式情報

| ID・言語 | 資料 | 採用した内容 |
|---|---|---|
| C1・日本語 | [Mynavi TechTus公式・事業／開発体制](https://mynavitechtus.com/jp/) | Web・モバイル開発、APO、AI出力の人による確認 |
| C2・英語 | [Mynavi TechTus公式・Full-stack Engineer](https://mynavitechtus.com/careers-at-mynavi-techtus-vietnam/full-stack-engineer/) | 保守性、リスク・トレードオフの説明、開発工程。別枠の公開求人 |
| C3・ベトナム語 | [Mynavi TechTus公式・APO Leader](https://mynavitechtus.com/vi/jobs/apo-leader/) | 要求の整理、技術説明、育成、チームとの調整。別枠の公開求人 |

### 日本語の面接資料

| ID・言語 | 資料 | 採用した内容 |
|---|---|---|
| J1・日本語 | [doda・ITエンジニアの面接](https://doda.jp/engineer/guide/it/004.html) | 転職理由、志望理由、案件・失敗・技術選択の深掘り |
| J2・日本語 | [doda・面接の自己紹介](https://doda.jp/guide/mensetsu/interview/001.html) | 職務経験を中心とした簡潔な自己紹介 |
| J3・日本語 | [doda・カジュアル面談](https://doda.jp/engineer/guide/it/032.html) | 転職への考え、希望する仕事、相互理解 |

### 英語の採用・海外就業資料

| ID・言語 | 資料 | 採用した内容 |
|---|---|---|
| E1・英語 | [Microsoft・Technical interviewing](https://careers.microsoft.com/v2/global/en/hiring-tips/technical-interviewing) | 問題の分解、設計、実装、テスト、前提確認 |
| E2・英語 | [Atlassian・Engineering interview handbook](https://www.atlassian.com/company/careers/resources/interviewing/engineering) | 過去の案件、協働、技術課題、今後の関心 |
| E3・英語 | [Robert Walters Vietnam・International career](https://www.robertwalters.com.vn/insights/career-advice/blog/10-tips-for-starting-an-international-career.html) | 海外勤務の理由、生活との関係、仕事・生活条件の調査 |
| E4・英語 | [Amazon Jobs・Interview Loop](https://amazon.jobs/content/en/how-we-hire/interview-loop) | 行動事例をSTARで整理する方法 |

### ベトナム語のIT面接資料

| ID・言語 | 資料 | 採用した内容 |
|---|---|---|
| V1・ベトナム語 | [ITviec・Java面接質問](https://itviec.com/blog/cau-hoi-phong-van-java/) | OOP、Collections、例外、並行処理などの質問領域 |
| V2・ベトナム語 | [ITviec・Backend面接質問](https://itviec.com/blog/cau-hoi-phong-van-backend/) | API、DB、認証・認可などの質問領域 |
| V3・ベトナム語 | [ITviec・Mobile Developer面接質問](https://itviec.com/blog/cau-hoi-phong-van-mobile-developer/) | 本人の担当、技術課題、品質、実務経験、発話練習 |

### 対話練習に関する研究

| ID・言語 | 資料 | 採用した内容 |
|---|---|---|
| R1・英語・研究 | [Gomezほか・Virtual Interviewers, Real Results](https://arxiv.org/abs/2506.16542) | AI模擬面接の形成的・質的研究。対象20人 |

資料の更新日・公開対象はそれぞれ異なります。他社の面接手順や時間配分を、Mynavi TechTusの面接手順として扱わないでください。

次は、Q01の自己紹介を日本語で60秒程度話すか、文章のまま送ってください。

