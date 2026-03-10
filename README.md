# 情報リテラシー（2026年度）

## 概要
- **対象**: 1年生（全学科共通）
- **教科書**: 情報Ⅰ Step Forward!（東京書籍）
- **構成**: 前期14回 ＋ 後期14回（計28回）

## ファイル構成
```
情報リテラシー/
├── info_literacy_all_weeks_v3 (1).yaml  # 授業トピック定義（前期・後期）
├── generate_slides.py                   # スライド生成スクリプト
├── generate_tex.py                      # TeXファイル生成スクリプト
├── claude_prompt.md                     # Claude Code用プロンプト
├── lecture_01.tex ~ lecture_14.tex      # 前期TeXファイル
├── lecture_01.pdf ~ lecture_14.pdf      # 前期スライド
├── lecture_01_handout.pdf ~ ...         # 前期ハンドアウト
├── lecture_second_01.tex ~ ...          # 後期TeXファイル
├── lecture_second_01.pdf ~ ...          # 後期スライド
└── lecture_second_01_handout.pdf ~ ...  # 後期ハンドアウト
```

## 使い方
1. `info_literacy_all_weeks_v3 (1).yaml` を編集して授業内容を更新する
2. `generate_tex.py` を実行してTeXファイルを生成する
3. TeXファイルをコンパイルしてPDFを作成する
