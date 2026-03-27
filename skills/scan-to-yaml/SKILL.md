---
name: scan-to-yaml
description: >
  情報リテラシー教科書スキャン→YAML更新スキル。
  「スキャンから更新」「教科書に合わせて」「週Xを抽出して」「スキャン画像を読んで」
  などのキーワードが出たら必ずこのスキルを参照する。
  スキャン画像の読み取り→テキスト抽出→YAML加筆修正→PDF再生成の手順を定める。
version: 1.0.0
---

# 情報リテラシー スキャン→YAML更新スキル

## 作業フォルダ

```
C:\Users\inazumi\workspace\情報リテラシー\
```

## 主要ファイル

| ファイル | 役割 |
|---|---|
| `scan/` | 教科書スキャン画像（JPG）を格納 |
| `scan/textbook_extract.md` | 抽出済みテキストの記録 |
| `info_literacy_all_weeks_v3 (1).yaml` | 全28週スライドのYAML（編集対象） |
| `generate_tex.py` | YAML → Beamer tex 生成スクリプト |

## スキャン画像の命名規則

| バッチ | ページ範囲 | 内容 |
|---|---|---|
| `Scan2026-03-27_080109_001〜022.jpg` | pp.4〜25 | Theory 01〜11（前期分） |
| `Scan2026-03-27_082700.jpg〜019.jpg` | pp.34〜53程度 | Theory 12以降（週12〜14対応） |

## ページ向きのパターン
- 奇数ページ（001, 003, 005...）→ **正置き**
- 偶数ページ（002, 004, 006...）→ **上下逆**（内容は読み取り可能）

## 教科書とYAML週の対応表

| 週 | textbook フィールド | Theory | 対応スキャン |
|---|---|---|---|
| 前期3 | pp.2-5 | 01-02 | 080109_001〜004 |
| 前期4 | pp.6-11 | 03-05 | 080109_005〜010 |
| 前期5 | pp.12-15 | 06-07 | 080109_011〜014 |
| 前期10 | pp.16-19 | 08-09 | 080109_015〜018 |
| 前期11 | pp.20-23 | 10-11 | 080109_019〜022 |
| 前期12 | pp.34-35 | 13 | 082700.jpg〜001 |
| 前期13 | pp.36-43 | 14-17 | 082700_002〜009 |
| 前期14 | pp.44-47 | 18-19 | 082700_010〜013 |
| 後期1〜7 | pp.70-121 | 27〜48 | 未スキャン |
| 後期9〜10 | pp.122-129 | 49〜52 | 未スキャン |

## 実行手順

### STEP 1：スキャン画像の読み取り

対象週のページ範囲に対応するスキャン画像を Read ツールで順番に読む。
上下逆の画像も内容は読み取れる。

```
対象週の textbook フィールドを確認
→ 上の対応表からスキャンファイル名を特定
→ Read ツールで各画像を読み取りテキスト抽出
```

### STEP 2：現在のYAMLと比較

```yaml
# YAMLの該当週のslidesを読み取り、教科書と比較する
# 確認ポイント：
# - 用語の名称が教科書と一致しているか
# - 教科書にある内容が抜けていないか
# - 教科書にない用語が含まれていないか（削除候補）
# - 表の列・行が教科書と一致しているか
```

### STEP 3：YAMLを修正

Edit ツールで `info_literacy_all_weeks_v3 (1).yaml` を編集：
- 用語・説明文を教科書の表現に合わせる
- 教科書の表をそのまま反映する
- 教科書にない用語は削除
- summaryを修正した内容に合わせて書き直す

### STEP 4：PDF再生成

```bash
cd ~/workspace/情報リテラシー
python generate_tex.py "info_literacy_all_weeks_v3 (1).yaml" --all --skip-week 1 --compile --slide
```

⚠️ **必ず `--skip-week 1` を付けること**。lecture_01.tex は手動編集済みのため上書き禁止。
⚠️ `--week` オプション単体は使わず、必ず `--all` を付けること（複数ドキュメントYAML対応）

### STEP 4.5：lecture_01.tex の手動フレームを確認・復元

`--all` で再生成すると `lecture_01.tex` が YAML から上書きされ、手動追加フレームが消える。
ビルド後に必ず以下を確認し、消えていたら復元すること。

```bash
grep -c "includegraphics" lecture_01.tex
# → 6 であれば OK（6未満なら消えている）
```

消えていた場合は `lecture_01.tex` の演習フレームの後・課題フレームの前に以下を追加する：

```latex
% --- 演習1：リンク集 ---
\begin{frame}{演習1：リンク集}
  \begin{figure}
    \begin{subfigure}{0.3\linewidth}
      \includegraphics[width=\linewidth]{images/syllabus.png}
      \caption{Webシラバス}
    \end{subfigure}
    \hfill
    \begin{subfigure}{0.3\linewidth}
      \includegraphics[width=\linewidth]{images/syusseki.png}
      \caption{出席管理システム}
    \end{subfigure}
    \hfill
    \begin{subfigure}{0.3\linewidth}
      \includegraphics[width=\linewidth]{images/LAN.png}
      \caption{無線LANの申請}
    \end{subfigure}
  \end{figure}
\end{frame}

% --- 演習2：リンク集 ---
\begin{frame}{演習2：リンク集}
  \begin{figure}
    \begin{subfigure}{0.3\linewidth}
      \includegraphics[width=\linewidth]{images/gmail.png}
      \caption{Gmail多要素認証設定}
    \end{subfigure}
    \hfill
    \begin{subfigure}{0.3\linewidth}
      \includegraphics[width=\linewidth]{images/webclass.png}
      \caption{WebClass}
    \end{subfigure}
    \hfill
    \begin{subfigure}{0.3\linewidth}
      \includegraphics[width=\linewidth]{images/pw.png}
      \caption{統一アカウントパスワード変更}
    \end{subfigure}
  \end{figure}
\end{frame}

% --- まとめ ---
\begin{frame}{まとめ}
  \begin{block}{今日のまとめ}
    \begin{itemize}
      \item 学内ネットワーク・各種アカウントの役割を理解した
      \item WebClass・Gmail・出席管理システムにログインできた
      \item パスワード管理・情報セキュリティの基本を確認した
    \end{itemize}
  \end{block}
  \vfill
  {\small 質問があれば授業後またはTeamsで受け付けます。}
\end{frame}
```

復元後に再コンパイル：
```bash
lualatex -interaction=nonstopmode lecture_01.tex
lualatex -interaction=nonstopmode lecture_01.tex
# スライド版
sed 's/handout,//' lecture_01.tex > _tmp.tex && lualatex -interaction=nonstopmode -jobname=lecture_01_slide _tmp.tex && lualatex -interaction=nonstopmode -jobname=lecture_01_slide _tmp.tex && rm _tmp.tex
```

### STEP 5：git push

```bash
cd ~/workspace/情報リテラシー
git add "info_literacy_all_weeks_v3 (1).yaml" lecture_*_slide.pdf lecture_*_handout.pdf lecture_*.tex
git commit -m "週XX：教科書スキャンに基づきYAML修正・PDF再生成"
git push origin main
```

## 修正方針（原則）

1. **goalsは変更しない**（シラバスの文言を使用）
2. **教科書にない用語は削除**（教科書対応週のみ）
3. **教科書の表は列構成も含めてそのまま反映**
4. **summaryは修正後の内容を反映して書き直す**
5. **教科書なし（textbook: "-"）の週は対象外**

## 抽出済みテキスト

既に抽出済みの内容は `scan/textbook_extract.md` を参照。
新たに読み取った内容は同ファイルに追記する。

## カメラ撮影画像への対応

スキャンが読み取りにくい場合はカメラ撮影画像を使用。
同じ `scan/` フォルダに配置し、ファイル名で区別する。
手順はスキャン画像と同じ。
