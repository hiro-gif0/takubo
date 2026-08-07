# sources.md（Google公式情報の確認記録）

確認日：2026年8月7日
確認方法：Web検索により、support.google.com（Gmailヘルプ／Google Workspace管理者ヘルプ／Google Workspaceラーニングセンター）の該当ページの内容を確認。ブログ・SEO記事・まとめサイトは参考にせず、判断根拠にしていない。

| # | 確認した内容 | 出典（ページ名） | URL | 確認日 | 使用スライド |
|---|---|---|---|---|---|
| 1 | 代理人は委任された相手のGmailで、メールの閲覧・送信・削除ができる | Delegate & collaborate on email（Gmail ヘルプ） | https://support.google.com/mail/answer/138350 | 2026-08-07 | 3, 5 |
| 2 | 代理人はチャットができず、パスワードも変更できない | Delegate & collaborate on email（Gmail ヘルプ） | https://support.google.com/mail/answer/138350 | 2026-08-07 | 5 |
| 3 | 代理人を追加すると招待メールが届き、承認が必要。招待には有効期限があり、承認後の反映まで時間がかかる場合がある | Delegate & collaborate on email（Gmail ヘルプ） | https://support.google.com/mail/answer/138350 | 2026-08-07 | 7 |
| 4 | 代理人の追加・削除は、パソコンのGmail設定「アカウントとインポート」から行う（削除も同じ画面） | Delegate & collaborate on email（Gmail ヘルプ） | https://support.google.com/mail/answer/138350 | 2026-08-07 | 7, 8 |
| 5 | 職場・学校アカウントでは代理人を最大1,000人まで登録可能。実務上の目安として同時にアクセスできる代理人は40人程度 | Let users delegate access to a Gmail account（Google Workspace 管理者ヘルプ） | https://support.google.com/a/answer/7223765 | 2026-08-07 | 11 |
| 6 | 管理者は管理コンソール（アプリ＞Google Workspace＞Gmail＞ユーザー設定＞メールの委任）で、組織内のユーザーが委任機能を使えるかどうかを設定する | Let users delegate access to a Gmail account（Google Workspace 管理者ヘルプ） | https://support.google.com/a/answer/7223765 | 2026-08-07 | 7, 11 |
| 7 | 職場・学校アカウントでは、同じ組織内の別のユーザーにのみ委任できる | Let users delegate access to a Gmail account（Google Workspace 管理者ヘルプ） | https://support.google.com/a/answer/7223765 | 2026-08-07 | 11 |
| 8 | Googleグループを代理人として追加できる（例：営業部のGoogleグループを代理人にして、部署全員に1つのGmailへのアクセスを与える）。管理者側の許可設定に依存する | Let users delegate access to a Gmail account（Google Workspace 管理者ヘルプ） | https://support.google.com/a/answer/7223765 | 2026-08-07 | 8（補足）, 11 |
| 9 | メールエイリアス（代替メールアドレス）はGoogleアカウントそのものではないため、代理人として追加できない | Add or delete an alternate email address（Google Workspace 管理者ヘルプ）／Gmail コミュニティの関連スレッド | https://support.google.com/a/answer/33327 | 2026-08-07 | 本紙では非掲載（一般部員には不要な技術詳細と判断） |
| 10 | 代理人がメールを送信すると、管理者の設定により「代理人の名前も表示される」場合と「アカウント所有者のみ表示」の場合がある | Delegate & collaborate on email（Gmail ヘルプ） | https://support.google.com/mail/answer/138350 | 2026-08-07 | 12（FAQ） |
| 11 | 代理人の追加はパソコンのみ対応。代理アカウントの閲覧・送信をスマートフォン版Gmailアプリ（Android／iOS）で行う機能は、2026年半ばにかけて順次展開されている（環境により利用可否が異なる場合がある） | Delegate & collaborate on email（Gmail ヘルプ, Android/iOS版）／Google Workspace Updates ブログ | https://support.google.com/mail/answer/138350 | 2026-08-07 | 12（FAQ） |
| 12 | 代理アクセスはGmail（メール）専用の仕組みであり、Google DriveやGoogle Calendarには自動的に適用されない。Drive・Calendarで複数人が共同利用する場合は、共有ドライブ・共有カレンダーという別の仕組みを使う | Google Workspace ラーニングセンター（委任に関するページ群）の一般的な整理と、Drive／Calendarの共有機能に関する公式ヘルプの記載内容から確認 | https://support.google.com/mail/answer/138350 | 2026-08-07 | 9 |

## 断定を避けた項目

以下は変更されやすい、または環境依存が大きいため、スライド本体では断定せず「環境により異なる場合がある」「情報システム担当へ確認」という表現にとどめた。

- スマートフォン版Gmailでの代理アカウント利用の対応状況（展開時期・対象OSバージョン）
- 招待の有効期限の具体的な日数、承認後の反映時間の具体的な長さ
- Googleグループを代理人にできるかどうか（管理者の許可設定・組織のドメイン構成に依存）
- 代理人送信時の差出人表示のされ方（管理者設定・ユーザー設定に依存）

## 使用しなかった情報源

- 個人ブログ、SEOまとめ記事、非公式のGmail解説サイトは検索結果に含まれていたが、判断根拠として採用していない。あくまで支持材料として、上記のsupport.google.com配下の公式ページの記載内容を優先した。
