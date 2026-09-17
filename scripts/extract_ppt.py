#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把性格色彩 PPT 的每一页内容原样摘录成 Markdown（docs/PPT全量内容.md）。

与 colors.json 的区别：
  - colors.json 只装"能按四色拆开"的内容，给程序渲染用
  - 本脚本产出的文档是**逐页全录**，包括那些没法按色拆的页
    （总纲、组织搭配图、婚恋关系、子女教育等），保证 PPT 31 页一字不漏

用法：
    pip install python-pptx
    python3 scripts/extract_ppt.py <PPT 路径>
"""
import argparse
import sys
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

# PPT 里用于区分四种性格的填充色
COLOR_OF_FILL = {
    "FF0000": "红",
    "0099FF": "蓝",
    "FFCC00": "黄",
    "339966": "绿",
    "FFFF66": "黄",
    "00FF99": "绿",
    "00CCFF": "蓝",
}


def fill_of(shape):
    try:
        if shape.fill.type == 1:  # solid
            return str(shape.fill.fore_color.rgb)
    except Exception:
        pass
    return None


def walk(shapes, depth=0, out=None):
    """递归遍历形状，组合图形也会展开。"""
    if out is None:
        out = []
    for sh in shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            out.append(("group", depth, sh.name, None, None))
            walk(sh.shapes, depth + 1, out)
            continue
        if getattr(sh, "has_table", False) and sh.has_table:
            rows = []
            for row in sh.table.rows:
                rows.append([c.text.strip().replace("\n", " / ") for c in row.cells])
            out.append(("table", depth, sh.name, rows, fill_of(sh)))
            continue
        if sh.has_text_frame:
            t = sh.text_frame.text.strip()
            if t:
                out.append(("text", depth, sh.name, t.replace("\n", " / "), fill_of(sh)))
    return out


def render_table(rows):
    """表格渲染成 Markdown，空表头列用占位。"""
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    lines = []
    header = rows[0] + [""] * (width - len(rows[0]))
    lines.append("| " + " | ".join(h if h else " " for h in header) + " |")
    lines.append("|" + "|".join(["------"] * width) + "|")
    for r in rows[1:]:
        r = r + [""] * (width - len(r))
        lines.append("| " + " | ".join(c for c in r) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="摘录 PPT 全部内容到 Markdown")
    ap.add_argument("ppt", help="PPTX 文件路径")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    ppt = Path(args.ppt).expanduser()
    if not ppt.exists():
        sys.exit(f"找不到文件：{ppt}")
    out_path = Path(args.output).expanduser() if args.output else Path(__file__).resolve().parent.parent / "docs" / "PPT全量内容.md"

    prs = Presentation(ppt)
    parts = [
        "# PPT 全量内容摘录",
        "",
        f"源文件：`{ppt.name}`（共 {len(prs.slides)} 页）",
        "",
        "本文件由 `scripts/extract_ppt.py` 自动生成，逐页原样摘录，不做改写、不做筛选。",
        "",
        "- 缩进表示该文字位于组合图形内部",
        "- 标注「块底色」的，是 PPT 里用来区分四种性格的填充色",
        "  对应关系：`FF0000` 红 · `0099FF` 蓝 · `FFCC00` 黄 · `339966` 绿",
        "",
        "---",
        "",
    ]

    for i, slide in enumerate(prs.slides, 1):
        items = walk(slide.shapes, 0)
        if not items:
            continue
        parts.append(f"## 第 {i} 页")
        parts.append("")
        for kind, depth, name, payload, fill in items:
            indent = "  " * depth
            if kind == "group":
                continue  # 组合本身不输出，只输出内部内容
            tag = ""
            if fill and fill in COLOR_OF_FILL:
                tag = f"　`块底色 {fill} → {COLOR_OF_FILL[fill]}色`"
            elif fill:
                tag = f"　`块底色 {fill}`"
            if kind == "table":
                parts.append(indent + tag.strip())
                parts.append("")
                parts.append(render_table(payload))
            else:
                parts.append(indent + "- " + payload + tag)
        parts.append("")
        parts.append("---")
        parts.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"已生成 {out_path}（{len(prs.slides)} 页，{out_path.stat().st_size / 1024:.1f} KB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
