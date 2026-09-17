#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 data/*.json 打包成 web/assets/data.js。

为什么要这一步：
  - data/ 下的 JSON 是唯一可编辑的数据源（改解析只动 JSON，不动代码）
  - 但浏览器以 file:// 打开页面时 fetch('xxx.json') 会被 CORS 拦住
  - 所以把 JSON 内联成一个普通 <script> 能加载的 JS 文件，页面既能双击直开，
    也能挂到 GitHub Pages / 个人网站上跑，两条路都不需要构建工具

用法：
    python3 scripts/build.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT = ROOT / "web" / "assets" / "data.js"


def main():
    colors = json.loads((DATA_DIR / "colors.json").read_text(encoding="utf-8"))
    questions = json.loads((DATA_DIR / "questions.json").read_text(encoding="utf-8"))

    bundle = {"colors": colors, "questions": questions}
    payload = json.dumps(bundle, ensure_ascii=False, indent=2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "/* 自动生成，请勿手改。改数据请编辑 data/*.json 后运行 python3 scripts/build.py */\n"
        "window.FPA_DATA = " + payload + ";\n",
        encoding="utf-8",
    )

    # 校验：题库与色彩键位是否闭合
    keys = {c["key"]: c["id"] for c in colors["colors"].values()}
    assert set(keys) == {"A", "B", "C", "D"}, f"色彩键位异常：{keys}"
    for q in questions:
        for k in ("A", "B", "C", "D"):
            assert q["options"].get(k), f"第 {q['id']} 题缺选项 {k}"

    print(f"题库 {len(questions)} 题，色彩 {len(colors['colors'])} 种")
    print(f"已生成 {OUT}（{OUT.stat().st_size / 1024:.1f} KB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
