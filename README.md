# duty - 毎日の雑務管理ツール

毎日のタスク管理 + AQUA中古車お得アラートシステム

## 機能

- **毎日のタスク確認**: `python main.py check` で今日やることを一覧表示
- **中古車自動チェック**: 毎日カーセンサーを自動スキャン
- **お得度判定**: 年式・走行距離・価格で市場相場と比較しスコアリング
- **ドラレコなし補正**: ドラレコ未装備車は実質価格に自動上乗せ (デフォルト1.5万円)
- **アラート通知**: LINE Notify / メール / コンソール出力
- **見学提案**: お得な車が見つかると見学予約を促すメッセージを表示

## 検索条件 (car_alert/config.py)

| 条件 | 設定値 |
|------|--------|
| 車種 | トヨタ AQUA |
| 最大価格 | 110万円 |
| 走行距離 | 6万km以下 |
| 年式 | 2014年以降 |
| エリア | 関西 (滋賀・京都・大阪・兵庫・奈良・和歌山) |
| 修復歴 | なし |
| 必須装備 | バックモニター・衝突軽減ブレーキ・Bluetooth |
| ドラレコなし | 実質価格に+1.5万円 |

## セットアップ

```bash
pip install -r requirements.txt
cp .env.example .env
# .env を編集して通知設定を入れる (任意)
```

## 使い方

```bash
# 今日のタスク確認 (中古車チェック含む)
python main.py check

# 中古車チェックのみ
python main.py cars

# 保存済みお得車両を表示
python main.py cars --show

# 全条件合致車両をスコア順に表示
python main.py cars --all

# 毎朝8時に自動チェック (常駐モード)
python main.py schedule
```

## 通知設定

`.env` ファイルを作成して以下を設定:

```env
# LINE Notify トークン (https://notify-bot.line.me/ で取得)
LINE_NOTIFY_TOKEN=xxxx

# メール通知 (Gmail等)
SMTP_USER=your@gmail.com
SMTP_PASS=your_app_password
ALERT_EMAIL=notify@example.com

# ドラレコ費用 (デフォルト: 15000円)
DASHCAM_COST=15000
```

## 自動化 (cron設定例)

```cron
# 毎朝7時に実行
0 7 * * * cd /path/to/duty && python main.py cars >> data/cron.log 2>&1
```

## お得度スコア

- **1.2以上**: 超お得！即見学検討
- **1.0以上**: お得 - 見学の価値あり
- **1.0未満**: 通常価格帯

スコアは `市場基準価格 x 0.88 / 実質価格 x 走行距離係数` で計算
