#!/usr/bin/env python3
"""
YAML -> Beamer .tex generator for Information Literacy lectures.

Usage:
  # 個別YAMLから生成
  python generate_tex.py lecture_01.yaml --compile --slide

  # 全週YAMLから一括生成（前期・後期 全28週）
  python generate_tex.py "info_literacy_all_weeks_v3 (1).yaml" --all --compile --slide

  # 特定の週だけ生成（前期3週目）
  python generate_tex.py "info_literacy_all_weeks_v3 (1).yaml" --all --week 3 --compile --slide
"""

import argparse
import glob
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

# Shared templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# OneDrive output directory
ONEDRIVE_DIR = Path.home() / "OneDrive - 独立行政法人 国立高等専門学校機構" / "情報リテラシー" / "2026"


# ---------------------------------------------------------------------------
# TeX escape
# ---------------------------------------------------------------------------
def escape_latex(text: str) -> str:
    if not text:
        return ""
    if any(c in text for c in ["\\", "$", "{", "}"]):
        return text
    for ch, repl in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")]:
        text = text.replace(ch, repl)
    return text


# ---------------------------------------------------------------------------
# Slide generators
# ---------------------------------------------------------------------------
def gen_title(data, slide):
    items = "\n".join(f"      \\item {escape_latex(s)}" for s in slide.get("flow", []))
    return rf"""
\begin{{frame}}{{\CourseName\quad 第\LectureNum 回「\LectureTitle 」}}
  {{\small \TermName\quad \TeacherName\quad ／\quad 教科書 \TextPages}}

  \vfill

  \begin{{block}}{{今日の流れ}}
    \begin{{enumerate}}
{items}
    \end{{enumerate}}
  \end{{block}}
\end{{frame}}
"""


def gen_terms(slide):
    title = slide.get("title", "用語と定義")
    items = "\n".join(
        f"    \\item[\\kw{{{escape_latex(t['term'])}}}]\n      {escape_latex(t['desc'])}"
        for t in slide.get("items", [])
    )
    return rf"""
\begin{{frame}}{{{escape_latex(title)}}}
  \begin{{description}}[labelwidth=6em]
{items}
  \end{{description}}
\end{{frame}}
"""


def gen_points(slide):
    title = slide.get("title", "重要ポイント")
    items = "\n".join(f"      \\item {escape_latex(s)}" for s in slide.get("items", []))
    out = rf"""
\begin{{frame}}{{{escape_latex(title)}}}
  \begin{{block}}{{ポイント}}
    \begin{{itemize}}
{items}
    \end{{itemize}}
  \end{{block}}"""
    supplement = slide.get("supplement")
    if supplement:
        sup = "\n".join(f"      \\item {escape_latex(s)}" for s in supplement)
        out += rf"""

  \vfill

  \begin{{exampleblock}}{{補足}}
    \begin{{itemize}}
{sup}
    \end{{itemize}}
  \end{{exampleblock}}"""
    out += "\n\\end{frame}\n"
    return out


def gen_code(slide):
    title = slide.get("title", "プログラム例")
    lang = slide.get("language", "Python")
    label = slide.get("label", f"{lang} の例")
    code = slide.get("code", "").rstrip()
    return rf"""
\begin{{frame}}[fragile]{{{escape_latex(title)}}}
  \begin{{exampleblock}}{{{escape_latex(label)}}}
\begin{{lstlisting}}[language={lang}]
{code}
\end{{lstlisting}}
  \end{{exampleblock}}
\end{{frame}}
"""


def gen_practice(slide):
    title = slide.get("title", "実習")
    desc = slide.get("desc", "実際にコンピュータで操作してください。")
    items = "\n".join(f"      \\item {escape_latex(s)}" for s in slide.get("steps", []))
    return rf"""
\begin{{frame}}{{{escape_latex(title)}}}
  {{\small {escape_latex(desc)}}}

  \vfill

  \begin{{block}}{{手順}}
    \begin{{enumerate}}
{items}
    \end{{enumerate}}
  \end{{block}}
\end{{frame}}
"""


def gen_notice(slide):
    title = slide.get("title", "補足・よくある間違い")
    items = "\n".join(f"      \\item {escape_latex(s)}" for s in slide.get("items", []))
    out = rf"""
\begin{{frame}}{{{escape_latex(title)}}}
  \begin{{noticebox}}[注意]
    \begin{{itemize}}
{items}
    \end{{itemize}}
  \end{{noticebox}}"""
    supplement = slide.get("supplement")
    if supplement:
        sup = "\n".join(f"    {escape_latex(s)}" for s in supplement)
        out += rf"""

  \vfill

  \begin{{exampleblock}}{{補足}}
{sup}
  \end{{exampleblock}}"""
    out += "\n\\end{frame}\n"
    return out


def gen_exercise(slide):
    title = slide.get("title", "演習")
    basic = "\n".join(f"      \\item {escape_latex(s)}" for s in slide.get("basic", []))
    out = rf"""
\begin{{frame}}{{{escape_latex(title)}}}
  {{\small 各自で取り組んでください。}}

  \vfill

  \begin{{block}}{{基本問題}}
    \begin{{itemize}}
{basic}
    \end{{itemize}}
  \end{{block}}"""
    advanced = slide.get("advanced")
    if advanced:
        adv = "\n".join(f"      \\item {escape_latex(s)}" for s in advanced)
        out += rf"""

  \vfill

  \begin{{exampleblock}}{{応用問題（余裕がある人）}}
    \begin{{itemize}}
{adv}
    \end{{itemize}}
  \end{{exampleblock}}"""
    out += "\n\\end{frame}\n"
    return out


def gen_assignment(data, slide):
    task = escape_latex(slide.get("task", "Teamsで提出してください。"))
    return rf"""
\begin{{frame}}{{課題・次回予告}}
  \begin{{importantbox}}[課題（次回までに提出）]
    {task}
  \end{{importantbox}}

  \vfill

  \begin{{block}}{{次回}}
    「\NextTopic 」（教科書 \NextPages ）
  \end{{block}}

  \vfill

  {{\small
  質問があれば授業後またはTeamsで受け付けます。}}
\end{{frame}}
"""


def gen_table(slide):
    title = slide.get("title", "表")
    headers = slide.get("headers", [])
    rows = slide.get("rows", [])
    col_spec = "l" * len(headers)
    header_line = " & ".join(escape_latex(h) for h in headers)
    row_lines = "\n".join(
        "    " + " & ".join(escape_latex(c) for c in row) + r" \\"
        for row in rows
    )
    return rf"""
\begin{{frame}}{{{escape_latex(title)}}}
  \centering
  \begin{{tabular}}{{{col_spec}}}
    \toprule
    {header_line} \\
    \midrule
{row_lines}
    \bottomrule
  \end{{tabular}}
\end{{frame}}
"""


def gen_twocol(slide):
    title = slide.get("title", "比較")
    left = slide.get("left", {})
    right = slide.get("right", {})

    def col_block(d, style="block"):
        label = escape_latex(d.get("label", ""))
        items = "\n".join(f"          \\item {escape_latex(s)}" for s in d.get("items", []))
        return rf"""      \begin{{{style}}}{{{label}}}
        \small
        \begin{{itemize}}
{items}
        \end{{itemize}}
      \end{{{style}}}"""

    return rf"""
\begin{{frame}}{{{escape_latex(title)}}}
  \begin{{columns}}[T]
    \begin{{column}}{{0.48\textwidth}}
{col_block(left, "block")}
    \end{{column}}
    \begin{{column}}{{0.48\textwidth}}
{col_block(right, "exampleblock")}
    \end{{column}}
  \end{{columns}}
\end{{frame}}
"""


def gen_free(slide):
    title = slide.get("title", "")
    fragile = "[fragile]" if slide.get("fragile") else ""
    latex = slide.get("latex", "")
    return rf"""
\begin{{frame}}{fragile}{{{escape_latex(title)}}}
{latex}
\end{{frame}}
"""


def gen_summary(items):
    lines = "\n".join(f"      \\item {escape_latex(s)}" for s in items)
    return rf"""
\begin{{frame}}{{まとめ}}
  \begin{{block}}{{今日のまとめ}}
    \begin{{itemize}}
{lines}
    \end{{itemize}}
  \end{{block}}

  \vfill

  {{\small 質問があれば授業後またはTeamsで受け付けます。}}
\end{{frame}}
"""


GENERATORS = {
    "title": lambda d, s: gen_title(d, s),
    "terms": lambda d, s: gen_terms(s),
    "points": lambda d, s: gen_points(s),
    "code": lambda d, s: gen_code(s),
    "practice": lambda d, s: gen_practice(s),
    "notice": lambda d, s: gen_notice(s),
    "exercise": lambda d, s: gen_exercise(s),
    "assignment": lambda d, s: gen_assignment(d, s),
    "table": lambda d, s: gen_table(s),
    "twocol": lambda d, s: gen_twocol(s),
    "free": lambda d, s: gen_free(s),
}


# ---------------------------------------------------------------------------
# Generate .tex content
# ---------------------------------------------------------------------------
def _parse_num(num):
    """numを (is_second, n) に分解。後期なら is_second=True。"""
    s = str(num)
    if s.startswith("後期"):
        return True, int(s[2:])
    if s.startswith("後"):
        return True, int(s[1:])
    return False, int(s)


def format_num(num) -> str:
    """numをゼロ埋め表示用文字列に変換。例: 1 -> '01', '後期3' -> '03'"""
    _, n = _parse_num(num)
    return f"{n:02d}"


def generate_tex(data: dict) -> str:
    num = data["num"]
    num_display = format_num(num)
    title = data["title"]
    textbook = data.get("textbook", "-")
    next_topic = data.get("next_topic", "")
    next_pages = data.get("next_pages", "-")

    header = rf"""% !TEX program = lualatex
% Auto-generated from YAML (v3) — {num_display}: {title}

\documentclass[aspectratio=43,professionalfonts,handout]{{beamer}}
\usepackage{{beamer_template}}

\newcommand{{\LectureNum}}{{{num_display}}}
\newcommand{{\LectureTitle}}{{{title}}}
\newcommand{{\CourseName}}{{情報リテラシー}}
\newcommand{{\TextPages}}{{{textbook}}}
\newcommand{{\NextTopic}}{{{next_topic}}}
\newcommand{{\NextPages}}{{{next_pages}}}

\begin{{document}}
"""

    body_parts = []
    for i, slide in enumerate(data.get("slides", []), 1):
        stype = slide.get("type", "free")
        gen = GENERATORS.get(stype)
        if gen:
            body_parts.append(f"% --- Slide {i}: {stype} ---")
            body_parts.append(gen(data, slide))

    summary = data.get("summary")
    if summary:
        body_parts.append("% --- まとめ ---")
        body_parts.append(gen_summary(summary))

    footer = r"\end{document}" + "\n"
    return header + "\n".join(body_parts) + "\n" + footer


# ---------------------------------------------------------------------------
# All-weeks YAML helpers
# ---------------------------------------------------------------------------
def load_all_weeks(yaml_path: Path) -> list:
    """全週YAMLから全週データのリストを返す。前期・後期を統合。"""
    weeks = []
    with open(yaml_path, encoding="utf-8") as f:
        for doc in yaml.safe_load_all(f):
            if isinstance(doc, list):
                weeks.extend(w for w in doc if w)
            elif isinstance(doc, dict):
                weeks.append(doc)
    return weeks


def num_to_stem(num) -> str:
    """YAML の num フィールドからファイル名幹を生成。
    例: 1 -> lecture_01, "後期3" -> lecture_second_03
    """
    is_second, n = _parse_num(num)
    if is_second:
        return f"lecture_second_{n:02d}"
    return f"lecture_{n:02d}"


# ---------------------------------------------------------------------------
# Compile .tex -> PDF
# ---------------------------------------------------------------------------
def compile_tex(tex_path: Path, output_dir: Path, slide_mode=False):
    """Compile .tex using a temp directory with templates from workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Copy .tex and templates
        shutil.copy(tex_path, tmp)
        for sty in TEMPLATES_DIR.glob("*.sty"):
            shutil.copy(sty, tmp)

        stem = tex_path.stem
        tex_name = tex_path.name

        if slide_mode:
            jobname = f"{stem}_slide"
            cmd = [
                "lualatex", "-interaction=nonstopmode",
                f"-jobname={jobname}",
                rf"\def\slidemode{{1}}\input{{{tex_name}}}"
            ]
        else:
            jobname = f"{stem}_handout"
            cmd = [
                "lualatex", "-interaction=nonstopmode",
                f"-jobname={jobname}",
                tex_name
            ]

        # Run twice for page numbers
        for _ in range(2):
            result = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)

        pdf_path = tmp / f"{jobname}.pdf"
        if pdf_path.exists():
            dest = output_dir / pdf_path.name
            shutil.copy(pdf_path, dest)
            print(f"  PDF: {dest}")

            # Also copy to OneDrive if it exists
            if ONEDRIVE_DIR.exists():
                onedrive_dest = ONEDRIVE_DIR / pdf_path.name
                shutil.copy(pdf_path, onedrive_dest)
                print(f"  -> OneDrive: {onedrive_dest.name}")

            return True
        else:
            print(f"  ERROR: Compile failed for {tex_name}")
            # Show last few lines of log
            log = tmp / f"{jobname}.log"
            if log.exists():
                lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in lines[-10:]:
                    if "Error" in line or "!" in line:
                        print(f"    {line}")
            return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="YAML -> Beamer .tex generator")
    parser.add_argument("files", nargs="+", help="YAML files to process")
    parser.add_argument("--compile", action="store_true", help="Compile to PDF")
    parser.add_argument("--slide", action="store_true", help="Also generate slide version")
    parser.add_argument("--outdir", type=str, default=None, help="Output directory")
    parser.add_argument("--all", action="store_true", help="全週YAMLから全週を一括生成")
    parser.add_argument("--week", type=str, default=None, help="特定週のみ生成（例: 3 または 後3）")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    out_dir = Path(args.outdir) if args.outdir else script_dir

    # Expand globs on Windows
    yaml_files = []
    for pattern in args.files:
        expanded = glob.glob(pattern)
        yaml_files.extend(expanded if expanded else [pattern])

    for yaml_file in yaml_files:
        yaml_path = Path(yaml_file)
        if not yaml_path.exists():
            print(f"SKIP: {yaml_path} not found")
            continue

        if args.all:
            # 全週YAMLから個別 lecture_XX.tex を生成
            weeks = load_all_weeks(yaml_path)
            for data in weeks:
                num = str(data.get("num", ""))
                if args.week and num_to_stem(num) != num_to_stem(args.week):
                    continue
                stem = num_to_stem(num)
                tex_content = generate_tex(data)
                tex_path = out_dir / f"{stem}.tex"
                with open(tex_path, "w", encoding="utf-8") as f:
                    f.write(tex_content)
                print(f"Generated: {tex_path.name}")
                if args.compile:
                    print(f"  Compiling handout...")
                    compile_tex(tex_path, out_dir)
                    if args.slide:
                        print(f"  Compiling slide...")
                        compile_tex(tex_path, out_dir, slide_mode=True)
        else:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            tex_content = generate_tex(data)
            tex_path = out_dir / yaml_path.with_suffix(".tex").name

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)
            print(f"Generated: {tex_path.name}")

            if args.compile:
                print(f"Compiling handout...")
                compile_tex(tex_path, out_dir)
                if args.slide:
                    print(f"Compiling slide...")
                    compile_tex(tex_path, out_dir, slide_mode=True)

    # Also copy .tex to OneDrive
    if ONEDRIVE_DIR.exists():
        for yaml_file in yaml_files:
            tex_name = Path(yaml_file).with_suffix(".tex").name
            src = out_dir / tex_name
            if src.exists():
                shutil.copy(src, ONEDRIVE_DIR / tex_name)


if __name__ == "__main__":
    main()
