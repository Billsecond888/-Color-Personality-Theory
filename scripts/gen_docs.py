#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 data/colors.json 渲染成人能直接读的 Markdown（docs/四色解析.md）。

为什么要有这一步：colors.json 是给程序读的，人打开是一坨 JSON。
生成一份 Markdown 放仓库里，在 GitHub 上点开就能看到 PPT 的全部内容。

用法：
    python3 scripts/gen_docs.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "四色解析.md"


def bullets(items):
    return "\n".join("- " + i for i in items) if items else "- （无）"


def block(color):
    tc = color.get("teamContribution", {})
    tw = color.get("teamwork", {})
    f = color.get("figure", {})
    L = []
    L.append(f"## {color['name']}（选项 {color['key']}）")
    L.append("")
    L.append(f"> {color['motto']}")
    L.append("")
    L.append("| 项目 | 内容 |")
    L.append("|------|------|")
    L.append(f"| 最大的长处 | {color['maxStrength']} |")
    L.append(f"| 最大的短处 | {color['maxWeakness']} |")
    L.append(f"| 基本动机 | {' · '.join(color.get('basicMotivation', []))} |")
    L.append(f"| 对外界的需求 | {' · '.join(color.get('needsFromOutside', []))} |")
    L.append("")
    L.append("### 优势")
    L.append("")
    L.append(bullets(color.get("strengths", [])))
    L.append("")
    L.append("### 优势过当")
    L.append("")
    L.append(bullets(color.get("overuses", [])))
    L.append("")
    L.append("### 典型人物")
    L.append("")
    L.append(f"**{f.get('name', '')}** —— {f.get('desc', '')}")
    L.append("")
    L.append("### 对团队的贡献")
    L.append("")
    L.append("**发挥优势时**")
    L.append("")
    L.append(bullets(tc.get("whenStrength", [])))
    L.append("")
    L.append("**优势过当时**")
    L.append("")
    L.append(bullets(tc.get("whenOveruse", [])))
    L.append("")
    L.append("**运用优势得当时**")
    L.append("")
    L.append(bullets(tc.get("whenApplied", [])))
    L.append("")
    L.append("### 团队合作")
    L.append("")
    L.append(f"- 优势：{tw.get('strength', '')}")
    L.append(f"- 过当：{tw.get('overuse', '')}")
    L.append("")
    L.append("### 协作方式")
    L.append("")
    L.append(f"**怎么沟通**\n\n{bullets(color.get('howToCommunicate', []))}\n")
    L.append(f"**TA 是你的上司**\n\n{bullets(color.get('howToInfluenceBoss', []))}\n")
    L.append(f"**TA 是你的部属**\n\n{bullets(color.get('howToLeadSubordinate', []))}\n")
    L.append(f"**适合的方向**\n\n{bullets(color.get('careerDirection', []))}\n")
    L.append("### 领导风格")
    L.append("")
    L.append(bullets(color.get("leadershipStyle", [])))
    L.append("")
    L.append("### 客户视角")
    L.append("")
    L.append(f"**作为客户**\n\n{bullets(color.get('asCustomer', []))}\n")
    L.append(f"**客户抱怨时需要**\n\n{bullets(color.get('whenComplaining', []))}\n")
    L.append(f"**培训中的表现**\n\n{bullets(color.get('inTraining', []))}\n")
    return "\n".join(L)


def main():
    data = json.loads((ROOT / "data" / "colors.json").read_text(encoding="utf-8"))
    colors = data["colors"]
    order = data["order"]

    parts = [
        "# 四色完整解析",
        "",
        "本文件由 `scripts/gen_docs.py` 从 `data/colors.json` 自动生成，内容逐条照录",
        "《性格分析之性格色彩 - 2026 Leader Offsite》PPT（31 页），未做校正。",
        "",
        "**不要手改本文件**——改内容请改 `data/colors.json` 后重新生成。",
        "",
        "四色与选项对应：A 红 · B 蓝 · C 黄 · D 绿",
        "",
        "---",
        "",
    ]
    for cid in order:
        parts.append(block(colors[cid]))
        parts.append("")
        parts.append("---")
        parts.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"已生成 {OUT}（{OUT.stat().st_size / 1024:.1f} KB，{len(order)} 种色彩）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
