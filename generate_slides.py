#!/usr/bin/env python3
"""YAML → Beamer LaTeX スライド生成スクリプト"""

import yaml
import os
import re

YAML_FILE = "info_literacy_all_weeks_v3 (1).yaml"
OUTPUT_DIR = "."

def escape_latex(text):
    """LaTeX特殊文字のエスケープ（最低限）"""
    if not isinstance(text, str):
        text = str(text)
    # & はテーブル以外でエスケープ、% と # はエスケープ
    text = text.replace('%', '\\%')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    # ⚠️ などの絵文字はそのまま（LuaLaTeXで対応可能）
    return text

def escape_latex_keep_amp(text):
    """テーブルセル用（&はエスケープしない）"""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace('%', '\\%')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    return text

def get_file_info(num_str):
    """num文字列からファイル名とLectureNum、学期情報を返す"""
    if num_str.startswith("後期"):
        n = int(num_str.replace("後期", ""))
        filename = f"lecture_second_{n:02d}.tex"
        lecture_num = str(n)
        semester = "second"
    else:
        n = int(num_str)
        filename = f"lecture_{n:02d}.tex"
        lecture_num = f"{n:02d}"
        semester = "first"
    return filename, lecture_num, semester

def render_title_slide(slide, meta):
    """タイトルスライド"""
    lines = []
    lines.append(r"\begin{frame}{\CourseName\quad 第\LectureNum 回「\LectureTitle 」}")
    lines.append(r"  {\small \TermName\quad \TeacherName\quad ／\quad 教科書 \TextPages}")
    lines.append("")
    lines.append(r"  \vfill")
    lines.append("")
    lines.append(r"  \begin{block}{今日の流れ}")
    lines.append(r"    \begin{enumerate}")
    for item in slide.get("flow", []):
        lines.append(f"      \\item {escape_latex(item)}")
    lines.append(r"    \end{enumerate}")
    lines.append(r"  \end{block}")
    lines.append(r"\end{frame}")
    return lines

def render_terms_slide(slide):
    """用語スライド"""
    title = escape_latex(slide.get("title", "用語"))
    lines = []
    lines.append(f"\\begin{{frame}}{{{title}}}")
    lines.append(r"  \begin{description}[labelwidth=6em]")
    for item in slide.get("items", []):
        term = escape_latex(item["term"])
        desc = escape_latex(item["desc"])
        lines.append(f"    \\item[\\kw{{{term}}}]")
        lines.append(f"      {desc}")
    lines.append(r"  \end{description}")
    lines.append(r"\end{frame}")
    return lines

def render_points_slide(slide):
    """ポイントスライド"""
    title = escape_latex(slide.get("title", "ポイント"))
    lines = []
    lines.append(f"\\begin{{frame}}{{{title}}}")
    lines.append(r"  \begin{block}{ポイント}")
    lines.append(r"    \begin{itemize}")
    for item in slide.get("items", []):
        lines.append(f"      \\item {escape_latex(item)}")
    lines.append(r"    \end{itemize}")
    lines.append(r"  \end{block}")
    # supplement があれば exampleblock で追加
    supplement = slide.get("supplement", [])
    if supplement:
        lines.append("")
        lines.append(r"  \vfill")
        lines.append("")
        lines.append(r"  \begin{exampleblock}{補足}")
        lines.append(r"    \begin{itemize}")
        for item in supplement:
            lines.append(f"      \\item {escape_latex(item)}")
        lines.append(r"    \end{itemize}")
        lines.append(r"  \end{exampleblock}")
    lines.append(r"\end{frame}")
    return lines

def render_twocol_slide(slide):
    """2カラムスライド"""
    title = escape_latex(slide.get("title", "比較"))
    left = slide.get("left", {})
    right = slide.get("right", {})
    left_label = escape_latex(left.get("label", "左"))
    right_label = escape_latex(right.get("label", "右"))
    lines = []
    lines.append(f"\\begin{{frame}}{{{title}}}")
    lines.append(r"  \begin{columns}[T]")
    lines.append(r"    \begin{column}{0.48\textwidth}")
    lines.append(f"      \\begin{{block}}{{{left_label}}}")
    lines.append(r"        \small")
    lines.append(r"        \begin{itemize}")
    for item in left.get("items", []):
        lines.append(f"          \\item {escape_latex(item)}")
    lines.append(r"        \end{itemize}")
    lines.append(r"      \end{block}")
    lines.append(r"    \end{column}")
    lines.append(r"    \begin{column}{0.48\textwidth}")
    lines.append(f"      \\begin{{exampleblock}}{{{right_label}}}")
    lines.append(r"        \small")
    lines.append(r"        \begin{itemize}")
    for item in right.get("items", []):
        lines.append(f"          \\item {escape_latex(item)}")
    lines.append(r"        \end{itemize}")
    lines.append(r"      \end{exampleblock}")
    lines.append(r"    \end{column}")
    lines.append(r"  \end{columns}")
    lines.append(r"\end{frame}")
    return lines

def render_table_slide(slide):
    """テーブルスライド"""
    title = escape_latex(slide.get("title", "表"))
    headers = slide.get("headers", [])
    rows = slide.get("rows", [])
    ncols = len(headers)
    col_spec = "l" * ncols
    lines = []
    lines.append(f"\\begin{{frame}}{{{title}}}")
    lines.append(r"  \centering")
    lines.append(r"  \small")
    lines.append(f"  \\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"    \toprule")
    header_str = " & ".join(escape_latex_keep_amp(h) for h in headers) + r" \\"
    lines.append(f"    {header_str}")
    lines.append(r"    \midrule")
    for row in rows:
        row_str = " & ".join(escape_latex_keep_amp(str(c)) for c in row) + r" \\"
        lines.append(f"    {row_str}")
    lines.append(r"    \bottomrule")
    lines.append(r"  \end{tabular}")
    lines.append(r"\end{frame}")
    return lines

def render_practice_slide(slide):
    """実習スライド"""
    title = escape_latex(slide.get("title", "実習"))
    desc = slide.get("desc", "")
    steps = slide.get("steps", [])
    lines = []
    lines.append(f"\\begin{{frame}}{{{title}}}")
    if desc:
        lines.append(f"  {{\\small {escape_latex(desc)}}}")
        lines.append("")
        lines.append(r"  \vfill")
        lines.append("")
    lines.append(r"  \begin{block}{手順}")
    lines.append(r"    \begin{enumerate}")
    for step in steps:
        lines.append(f"      \\item {escape_latex(step)}")
    lines.append(r"    \end{enumerate}")
    lines.append(r"  \end{block}")
    lines.append(r"\end{frame}")
    return lines

def render_notice_slide(slide):
    """注意スライド"""
    title = escape_latex(slide.get("title", "注意"))
    lines = []
    lines.append(f"\\begin{{frame}}{{{title}}}")
    lines.append(f"  \\begin{{noticebox}}[{title}]")
    lines.append(r"    \begin{itemize}")
    for item in slide.get("items", []):
        lines.append(f"      \\item {escape_latex(item)}")
    lines.append(r"    \end{itemize}")
    lines.append(r"  \end{noticebox}")
    lines.append(r"\end{frame}")
    return lines

def render_exercise_slide(slide):
    """演習スライド"""
    title = escape_latex(slide.get("title", "演習"))
    basic = slide.get("basic", [])
    advanced = slide.get("advanced", [])
    lines = []
    lines.append(f"\\begin{{frame}}{{{title}}}")
    lines.append(r"  {\small 各自で取り組んでください。}")
    lines.append("")
    lines.append(r"  \vfill")
    lines.append("")
    if basic:
        lines.append(r"  \begin{block}{基本問題}")
        lines.append(r"    \begin{itemize}")
        for item in basic:
            lines.append(f"      \\item {escape_latex(item)}")
        lines.append(r"    \end{itemize}")
        lines.append(r"  \end{block}")
    if advanced:
        lines.append("")
        lines.append(r"  \vfill")
        lines.append("")
        lines.append(r"  \begin{exampleblock}{応用問題（余裕がある人）}")
        lines.append(r"    \begin{itemize}")
        for item in advanced:
            lines.append(f"      \\item {escape_latex(item)}")
        lines.append(r"    \end{itemize}")
        lines.append(r"  \end{exampleblock}")
    lines.append(r"\end{frame}")
    return lines

def render_assignment_slide(slide, meta):
    """課題・次回予告スライド"""
    task = escape_latex(slide.get("task", ""))
    lines = []
    lines.append(r"\begin{frame}{課題・次回予告}")
    lines.append(r"  \begin{importantbox}[課題]")
    lines.append(f"    {task}")
    lines.append(r"  \end{importantbox}")
    lines.append("")
    lines.append(r"  \vfill")
    lines.append("")
    lines.append(r"  \begin{block}{次回}")
    lines.append(r"    「\NextTopic 」（教科書 \NextPages ）")
    lines.append(r"  \end{block}")
    lines.append("")
    lines.append(r"  \vfill")
    lines.append("")
    lines.append(r"  {\small")
    lines.append(r"  質問があれば授業後またはTeamsで受け付けます。}")
    lines.append(r"\end{frame}")
    return lines

RENDERERS = {
    "title": lambda s, m: render_title_slide(s, m),
    "terms": lambda s, m: render_terms_slide(s),
    "points": lambda s, m: render_points_slide(s),
    "twocol": lambda s, m: render_twocol_slide(s),
    "table": lambda s, m: render_table_slide(s),
    "practice": lambda s, m: render_practice_slide(s),
    "notice": lambda s, m: render_notice_slide(s),
    "exercise": lambda s, m: render_exercise_slide(s),
    "assignment": lambda s, m: render_assignment_slide(s, m),
}

def generate_tex(week, output_dir):
    """1週分の.texファイルを生成"""
    num_str = str(week["num"])
    filename, lecture_num, semester = get_file_info(num_str)
    filepath = os.path.join(output_dir, filename)

    title = week.get("title", "")
    textbook = week.get("textbook", "-")
    next_topic = week.get("next_topic", "")
    next_pages = week.get("next_pages", "-")

    # TextPages: "-" はそのまま、"pp.X-Y" もそのまま
    text_pages = textbook if textbook != "-" else "対応なし"
    next_pages_val = next_pages if next_pages != "-" else "対応なし"

    meta = {
        "lecture_num": lecture_num,
        "title": title,
        "text_pages": text_pages,
        "next_topic": next_topic,
        "next_pages": next_pages_val,
        "semester": semester,
    }

    lines = []
    lines.append("% !TEX program = lualatex")
    lines.append(f"% Auto-generated from YAML (v3) — {num_str}: {title}")
    lines.append("")
    lines.append(r"\documentclass[aspectratio=43,professionalfonts,handout]{beamer}")
    lines.append(r"\usepackage{beamer_template}")
    lines.append("")
    lines.append(f"\\newcommand{{\\LectureNum}}{{{lecture_num}}}")
    lines.append(f"\\newcommand{{\\LectureTitle}}{{{escape_latex(title)}}}")
    lines.append(r"\newcommand{\CourseName}{情報リテラシー}")
    lines.append(f"\\newcommand{{\\TextPages}}{{{escape_latex(text_pages)}}}")
    lines.append(f"\\newcommand{{\\NextTopic}}{{{escape_latex(next_topic)}}}")
    lines.append(f"\\newcommand{{\\NextPages}}{{{escape_latex(next_pages_val)}}}")
    lines.append("")
    lines.append(r"\begin{document}")

    slides = week.get("slides", [])
    for i, slide in enumerate(slides):
        stype = slide.get("type", "")
        renderer = RENDERERS.get(stype)
        if renderer is None:
            lines.append(f"% --- Unknown slide type: {stype} ---")
            continue
        lines.append(f"% --- Slide {i+1}: {stype} ---")
        lines.append("")
        slide_lines = renderer(slide, meta)
        lines.extend(slide_lines)
        lines.append("")

    lines.append(r"\end{document}")
    lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filename

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, YAML_FILE)
    output_dir = os.path.join(script_dir, OUTPUT_DIR)

    with open(yaml_path, "r", encoding="utf-8") as f:
        docs = list(yaml.safe_load_all(f))

    # 複数ドキュメントの場合、各ドキュメントがリストなので結合
    data = []
    for doc in docs:
        if isinstance(doc, list):
            data.extend(doc)
        elif isinstance(doc, dict):
            data.append(doc)

    if not data:
        print("Error: No data found in YAML")
        return

    generated = []
    for week in data:
        filename = generate_tex(week, output_dir)
        generated.append(filename)
        print(f"  Generated: {filename}")

    print(f"\nTotal: {len(generated)} files generated.")

if __name__ == "__main__":
    main()
