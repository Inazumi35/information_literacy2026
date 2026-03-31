# 講義スライドYAML生成プロンプト

以下の仕様に従って、指定された授業テーマのYAMLファイルを生成してください。
出力はYAMLコードブロック1つだけにしてください。

---

## YAML仕様

### メタデータ（必須）

```yaml
num: "8"                          # 回数
title: "メインタイトル"            # 授業タイトル
subtitle: "サブタイトル"           # 任意
textbook: "-"                     # 教科書ページ（なければ"-"）
next_topic: "次回のテーマ"         # 次回予告
next_pages: "-"                   # 次回の教科書ページ
```

### スライドタイプ一覧

slides配列に以下のtypeを並べます。通常の構成：title → terms/points/twocol/table → exercise → assignment

#### title（タイトルスライド）
```yaml
- type: title
  flow: ["トピック1", "トピック2", "トピック3"]
```

#### terms（用語定義）
```yaml
- type: terms
  title: "基本用語"
  items:
    - term: "用語名"
      desc: "説明文"
```

#### points（箇条書きポイント）
```yaml
- type: points
  title: "重要ポイント"
  items: ["項目1", "項目2"]
  supplement: ["補足1"]           # 任意
```

#### table（表）
```yaml
- type: table
  title: "比較表"
  headers: ["列1", "列2", "列3"]
  rows:
    - ["値1", "値2", "値3"]
```

#### twocol（2列比較）
```yaml
- type: twocol
  title: "比較"
  left:
    label: "左タイトル"
    items: ["項目1", "項目2"]
  right:
    label: "右タイトル"
    items: ["項目1", "項目2"]
```

#### notice（注意事項）
```yaml
- type: notice
  title: "注意"
  items: ["注意1", "注意2"]
  supplement: ["補足"]            # 任意
```

#### code（コード例、fragile）
```yaml
- type: code
  title: "コード例"
  language: "Python"
  label: "ラベル"
  code: |
    print("hello")
```

#### practice（実習手順）
```yaml
- type: practice
  title: "実習"
  desc: "説明文"
  steps: ["手順1", "手順2"]
```

#### exercise（演習問題）
```yaml
- type: exercise
  title: "演習"
  basic: ["基本問題1", "基本問題2"]
  advanced: ["応用問題1"]         # 任意
```

#### assignment（課題・次回予告、最後に置く）
```yaml
- type: assignment
  task: "課題の内容"
```

---

## 出力例

```yaml
num: "8"
title: "データサイエンス・AI（1）"
subtitle: "導入"
textbook: "-"
next_topic: "データサイエンス・AI（2）：活用事例"
next_pages: "-"

slides:
  - type: title
    flow:
      - "データサイエンスとは"
      - "AIの歴史と現在"
      - "データ駆動型社会"

  - type: terms
    title: "基本用語"
    items:
      - term: "データサイエンス"
        desc: "データから有益な知見を引き出す学問分野。統計学・情報学・専門知識の融合"
      - term: "AI（人工知能）"
        desc: "人間の知的活動をコンピュータで再現する技術の総称"
      - term: "ビッグデータ"
        desc: "従来の手法では処理困難な大量・多種・高速なデータ"
      - term: "Society 5.0"
        desc: "サイバー空間とフィジカル空間を融合した超スマート社会"

  - type: points
    title: "AIの歴史"
    items:
      - "第1次ブーム（1950-60年代）：探索・推論。迷路やパズルを解く"
      - "第2次ブーム（1980年代）：エキスパートシステム。専門家の知識をルール化"
      - "第3次ブーム（2010年代〜）：機械学習・深層学習。データから自動で学習"
      - "現在：生成AI（ChatGPT、Claude等）の登場で社会が大きく変化"

  - type: twocol
    title: "データサイエンスの3要素"
    left:
      label: "必要なスキル"
      items:
        - "統計学・数学"
        - "プログラミング"
        - "対象分野の専門知識"
    right:
      label: "活用分野"
      items:
        - "医療（画像診断）"
        - "交通（自動運転）"
        - "マーケティング（購買予測）"
        - "製造（品質管理）"

  - type: points
    title: "データ活用のプロセス"
    items:
      - "1. 課題設定：何を知りたいか明確にする"
      - "2. データ収集：必要なデータを集める"
      - "3. データ前処理：欠損値や異常値の処理"
      - "4. 分析・モデリング：統計分析やAIモデルの構築"
      - "5. 評価・活用：結果を解釈し意思決定に活かす"

  - type: exercise
    title: "演習"
    basic:
      - "データサイエンスの3つの要素を説明せよ"
      - "AIの3つのブームをそれぞれ説明せよ"
    advanced:
      - "身近なAI活用の例を3つ挙げ、どのようなデータを使っているか考えてみよう"

  - type: assignment
    task: "データサイエンスとAIの基本概念を復習してください。"
```

---

## ルール
- スライドは5〜8枚程度（title + 内容3〜5枚 + exercise + assignment）
- 高専1年生向け。専門用語には必ず説明をつける
- 各itemは1行に収まる簡潔な文にする
- LaTeX特殊文字（& % # _）はそのまま書いてOK（自動エスケープされる）
- \や$や{}を含むLaTeX数式を書きたい場合はそのまま書く（エスケープしない）
