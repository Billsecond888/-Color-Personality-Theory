#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把四色解析数据渲染成一份可翻页的网页 PPT（web/deck.html）。

基于 guizang-ppt-skill 的「风格 A · 电子杂志风」模板：
拷贝模板 → 补几个模板里缺失的 stat 类 → 用 colors.json 生成 slides → 替换占位符。

为什么用脚本生成而不是手写 deck.html：
  内容全在 data/colors.json，手写容易与数据不同步；脚本保证页面与数据永远一致，
  改解析后重跑一次即可。

用法：
    python3 scripts/gen_deck.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = Path.home() / ".workbuddy/skills/guizang-ppt-skill"
TEMPLATE = SKILL / "assets" / "template.html"
OUT = ROOT / "web" / "deck.html"

TITLE = "性格色彩 · 四色完整解析"

# 模板缺这几个 stat 子组件，补进 style（不发明新类名，沿用 layouts.md 的命名）
EXTRA_CSS = """
  /* ---- 补齐 layouts.md 用到但模板未定义的 stat 子组件 ---- */
  .stat-label{font-family:var(--mono);font-size:max(11px,.82vw);letter-spacing:.14em;
    text-transform:uppercase;opacity:.55;margin-bottom:.9vh}
  .stat-nb{font-family:var(--serif-en);font-size:max(30px,3.4vw);font-weight:500;
    line-height:1;letter-spacing:-.01em}
  .stat-unit{font-family:var(--sans-zh);font-size:max(13px,1.05vw);opacity:.6;
    letter-spacing:0}
  .stat-note{font-family:var(--sans-zh);font-size:max(12px,.95vw);opacity:.62;
    margin-top:.9vh;line-height:1.5}
  /* ---- 四色卡：左侧色条 + 色名 ---- */
  .cc{border-left:3px solid var(--cc,var(--ink));padding:1.6vh 1.4vw;background:var(--paper-tint)}
  .cc-name{font-family:var(--serif-zh);font-size:max(17px,1.5vw);font-weight:600;
    color:var(--cc,var(--ink));letter-spacing:.02em}
  .cc-motto{font-family:var(--sans-zh);font-size:max(12px,.95vw);opacity:.6;
    font-style:italic;margin-top:.5vh}
  .cc-line{font-family:var(--sans-zh);font-size:max(12.5px,1vw);line-height:1.75;
    margin-top:.7vh}
  .cc-line b{font-weight:500}
  .li{font-family:var(--sans-zh);font-size:max(12.5px,1vw);line-height:1.85;
    padding-left:1.1em;position:relative}
  .li:before{content:"";position:absolute;left:0;top:.72em;width:5px;height:5px;
    border-radius:50%;background:var(--cc,currentColor);opacity:.75}
  /* ---- 内容密集页用的紧凑卡：同页放 8 组信息时不溢出 ---- */
  .cc-tight{padding:1.1vh .95vw}
  .cc-tight .cc-name{font-size:max(13px,1.05vw)}
  .cc-tight .li{font-size:max(11px,.86vw);line-height:1.52}
  .cc-sep{margin-top:1.2vh;padding-top:1.1vh;
    border-top:1px solid rgba(var(--ink-rgb),.14)}
"""

FAVICON = ('<link rel="icon" href="data:image/svg+xml,'
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Ccircle cx='9' cy='9' r='6' fill='%23D4594A'/%3E"
           "%3Ccircle cx='23' cy='9' r='6' fill='%234A6FA5'/%3E"
           "%3Ccircle cx='9' cy='23' r='6' fill='%23C8922A'/%3E"
           "%3Ccircle cx='23' cy='23' r='6' fill='%233A8E6A'/%3E"
           '%3C/svg%3E">')


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def lis(items, cls="li"):
    if not items:
        return ""
    return "".join(f'<div class="{cls}">{esc(i)}</div>' for i in items)


def slide(theme, chrome_l, chrome_r, body, foot_l, foot_r, extra=""):
    cls, attrs = theme
    return f"""<section class="slide {cls}"{attrs}>
  <div class="chrome">
    <div>{chrome_l}</div>
    <div>{chrome_r}</div>
  </div>
  <div class="frame" style="padding-top:5vh">
{body}
  </div>
  <div class="foot">
    <div>{foot_l}</div>
    <div>{foot_r}</div>
  </div>
</section>
"""


def build(colors, order):
    cs = {k: colors[k] for k in order}
    S = []
    n = 0

    def add(s):
        nonlocal n
        n += 1
        S.append(s)

    # ---- 1 封面 ----
    add(slide(
        ("hero dark", ""),
        "Color Personality · 培训讲义", "Vol.01",
        f"""    <div class="frame" style="display:grid;gap:4vh;align-content:center;min-height:78vh">
      <div class="kicker" data-anim>四种性格色彩 · 完整解析</div>
      <h1 class="h-hero" data-anim>性格色彩</h1>
      <h2 class="h-sub" data-anim>红 蓝 黄 绿</h2>
      <p class="lead" style="max-width:58vw" data-anim>
        没有哪一种颜色更好，只有哪一种更像你。看清自己的长处与过当，
        也看懂别人为什么和你不一样。
      </p>
      <div class="meta-row" data-anim>
        <span>30 道题</span><span>·</span><span>4 种色彩</span><span>·</span><span>一套协作语言</span>
      </div>
    </div>""",
        "内容整理自性格色彩培训讲义", "— 2026 —"))

    # ---- 2 四色总览 ----
    cards = "".join(
        f'      <div class="cc" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">{esc(cs[k]["name"])}</div>\n'
        f'        <div class="cc-motto">{esc(cs[k]["motto"])}</div>\n'
        f'        <div class="cc-line">长处 <b>{esc(cs[k]["maxStrength"])}</b></div>\n'
        f'        <div class="cc-line">短处 <b>{esc(cs[k]["maxWeakness"])}</b></div>\n'
        f'        <div class="cc-line">动机 <b>{esc(" · ".join(cs[k]["basicMotivation"]))}</b></div>\n'
        f'      </div>' for k in order)
    add(slide(
        ("light", ""),
        "四色总览 · Overview", f"01 / {len(order) * 3 + 8}",
        f"""    <div class="kicker" data-anim>先认识四个主角</div>
    <h2 class="h-xl" data-anim>四种基本性格色彩</h2>
    <div class="grid-4" style="margin-top:5vh">
{cards}
    </div>""",
        "每种色彩都有长处与短处", "Overview"))

    # ---- 每色三页 ----
    for idx, k in enumerate(order):
        c = cs[k]
        col = c["color"]
        nm = c["name"]
        base = idx * 3 + 2

        # 幕封（红色不用幕封，第 3 页直接进）
        if idx > 0:
            theme = "hero light" if idx % 2 == 1 else "hero dark"
            add(slide(
                (theme, ""),
                f"色彩解析 · {nm}", f"Act {idx + 1} · {base} / {len(order) * 3 + 8}",
                f"""    <div class="frame" style="display:grid;gap:6vh;align-content:center;min-height:78vh">
      <div class="kicker" data-anim>Act {idx + 1}</div>
      <h1 class="h-hero" style="font-size:8.5vw;color:{col}" data-anim>{esc(nm)}</h1>
      <p class="lead" style="max-width:52vw" data-anim>{esc(c["motto"])}</p>
    </div>""",
                f"{nm}性格解析", f"Act {idx + 1}"))

        # 档案页
        t = "dark" if idx % 2 == 0 else "dark"
        add(slide(
            ("dark", ""),
            f"{nm} · 档案", f"{base + 1} / {len(order) * 3 + 8}",
            f"""    <div class="kicker" data-anim style="color:{col}">{esc(nm)}性格 · 核心档案</div>
    <h2 class="h-xl" data-anim>{esc(c["motto"])}</h2>
    <div class="grid-2-6-6" style="margin-top:5vh">
      <div class="cc" style="--cc:{col}" data-anim>
        <div class="cc-name">最大的长处</div>
        <div class="cc-line" style="font-size:max(16px,1.5vw)"><b>{esc(c["maxStrength"])}</b></div>
        <div class="cc-name" style="margin-top:2.5vh">最大的短处</div>
        <div class="cc-line" style="font-size:max(16px,1.5vw)"><b>{esc(c["maxWeakness"])}</b></div>
      </div>
      <div style="display:grid;gap:2.6vh;align-content:start" data-anim>
        <div class="cc" style="--cc:{col}">
          <div class="cc-name">基本动机</div>
          <div class="cc-line">{esc(" · ".join(c["basicMotivation"]))}</div>
        </div>
        <div class="cc" style="--cc:{col}">
          <div class="cc-name">对外界的需求</div>
          <div class="cc-line">{esc(" · ".join(c["needsFromOutside"]))}</div>
        </div>
      </div>
    </div>""",
            f"{nm} · 长处 / 短处 / 动机 / 需求", "Profile"))

        # 优势与过当
        add(slide(
            ("light", ""),
            f"{nm} · 优势与过当", f"{base + 2} / {len(order) * 3 + 8}",
            f"""    <div class="kicker" data-anim>优势用过头，就是过当</div>
    <h2 class="h-xl" data-anim>{esc(nm)}：优势 与 优势过当</h2>
    <div class="grid-2-6-6" style="margin-top:5vh">
      <div class="cc" style="--cc:{col}" data-anim>
        <div class="cc-name">优势</div>
        <div style="margin-top:1.5vh;display:grid;gap:.5vh">{lis(c["strengths"])}</div>
      </div>
      <div class="cc" style="--cc:{col}" data-anim>
        <div class="cc-name" style="opacity:.62">优势过当</div>
        <div style="margin-top:1.5vh;display:grid;gap:.5vh">{lis(c["overuses"])}</div>
      </div>
    </div>""",
            f"{nm} · 6 条优势 / 6 条过当", "Strengths"))

        # 典型人物 + 团队贡献
        tc = c["teamContribution"]
        add(slide(
            ("dark", ""),
            f"{nm} · 人与团队", f"{base + 3} / {len(order) * 3 + 8}",
            f"""    <div class="kicker" data-anim>典型人物</div>
    <h2 class="h-xl" data-anim style="color:{col}">{esc(c["figure"]["name"])}</h2>
    <p class="lead" style="max-width:66vw;margin-top:1.5vh" data-anim>{esc(c["figure"]["desc"])}</p>
    <div class="grid-3" style="margin-top:5vh">
      <div class="cc" style="--cc:{col}" data-anim>
        <div class="cc-name">发挥优势时</div>
        <div style="margin-top:1.2vh;display:grid;gap:.4vh">{lis(tc["whenStrength"])}</div>
      </div>
      <div class="cc" style="--cc:{col}" data-anim>
        <div class="cc-name" style="opacity:.62">优势过当时</div>
        <div style="margin-top:1.2vh;display:grid;gap:.4vh">{lis(tc["whenOveruse"])}</div>
      </div>
      <div class="cc" style="--cc:{col}" data-anim>
        <div class="cc-name">运用优势得当时</div>
        <div style="margin-top:1.2vh;display:grid;gap:.4vh">{lis(tc["whenApplied"])}</div>
      </div>
    </div>""",
            f"{nm} · 典型人物与团队贡献", "Team"))

    total = len(order) * 3 + 10
    tail = len(order) * 3 + 2

    # ---- 四色对比 ----
    rows = "".join(
        f'      <div class="cc" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">{esc(cs[k]["name"])}</div>\n'
        f'        <div class="cc-line" style="margin-top:1vh">{esc(cs[k]["teamwork"]["strength"])}</div>\n'
        f'        <div class="cc-line" style="opacity:.65;margin-top:1.2vh">过当：{esc(cs[k]["teamwork"]["overuse"])}</div>\n'
        f'      </div>' for k in order)
    add(slide(
        ("light", ""),
        "四色对比 · 团队合作", f"{tail} / {total}",
        f"""    <div class="kicker" data-anim>放在一起看</div>
    <h2 class="h-xl" data-anim>四种色彩在团队里的样子</h2>
    <div class="grid-4" style="margin-top:5vh">
{rows}
    </div>""",
        "团队合作中的优势与过当", "Compare"))

    # ---- 沟通方式 ----
    rows = "".join(
        f'      <div class="cc" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">和{esc(cs[k]["name"])}沟通</div>\n'
        f'        <div style="margin-top:1.2vh;display:grid;gap:.4vh">{lis(cs[k]["howToCommunicate"])}</div>\n'
        f'      </div>' for k in order)
    add(slide(
        ("dark", ""),
        "协作 · 沟通", f"{tail + 1} / {total}",
        f"""    <div class="kicker" data-anim>减少耗费在人际关系上的精力</div>
    <h2 class="h-xl" data-anim>怎么和每种色彩沟通</h2>
    <div class="grid-4" style="margin-top:5vh">
{rows}
    </div>""",
        "FPA®沟通", "Communication"))

    # ---- 上司与部属 ----
    boss = "".join(
        f'      <div class="cc cc-tight" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">上司：怎么影响 TA</div>\n'
        f'        <div style="margin-top:1vh;display:grid;gap:.3vh">{lis(cs[k]["howToInfluenceBoss"])}</div>\n'
        f'        <div class="cc-sep">\n'
        f'          <div class="cc-name">部属：怎么带 TA</div>\n'
        f'          <div style="margin-top:1vh;display:grid;gap:.3vh">{lis(cs[k]["howToLeadSubordinate"])}</div>\n'
        f'        </div>\n'
        f'      </div>' for k in order)
    sub = ""
    add(slide(
        ("light", ""),
        "协作 · 管理", f"{tail + 2} / {total}",
        f"""    <div class="kicker" data-anim>向上与向下</div>
    <h2 class="h-xl" data-anim>如何影响上司 · 如何带领部属</h2>
    <div class="grid-4" style="margin-top:3vh">
{boss}
    </div>""",
        "FPA®管理", "Management"))

    # ---- 职业与领导风格 ----
    rows = "".join(
        f'      <div class="cc" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">适合的方向</div>\n'
        f'        <div style="margin-top:1.2vh;display:grid;gap:.45vh">{lis(cs[k]["careerDirection"])}</div>\n'
        f'      </div>' for k in order)
    add(slide(
        ("dark", ""),
        "职业 · 方向", f"{tail + 3} / {total}",
        f"""    <div class="kicker" data-anim>让优势发挥得更好</div>
    <h2 class="h-xl" data-anim>职业发展方向</h2>
    <div class="grid-4" style="margin-top:5vh">
{rows}
    </div>""",
        "FPA®职业生涯规划", "Career"))

    rows = "".join(
        f'      <div class="cc" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">领导品质和风格</div>\n'
        f'        <div style="margin-top:1.2vh;display:grid;gap:.45vh">{lis(cs[k]["leadershipStyle"])}</div>\n'
        f'      </div>' for k in order)
    add(slide(
        ("light", ""),
        "职业 · 领导", f"{tail + 4} / {total}",
        f"""    <div class="kicker" data-anim>带人也有色彩</div>
    <h2 class="h-xl" data-anim>领导品质和风格</h2>
    <div class="grid-4" style="margin-top:5vh">
{rows}
    </div>""",
        "FPA®领导", "Leadership"))

    # ---- 客户视角 ----
    a = "".join(
        f'      <div class="cc" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">作为客户</div>\n'
        f'        <div style="margin-top:1.2vh;display:grid;gap:.45vh">{lis(cs[k]["asCustomer"])}</div>\n'
        f'      </div>' for k in order)
    add(slide(
        ("dark", ""),
        "销售 · 客户", f"{tail + 5} / {total}",
        f"""    <div class="kicker" data-anim>换个位置看</div>
    <h2 class="h-xl" data-anim>作为客户，他们是什么样</h2>
    <div class="grid-4" style="margin-top:5vh">
{a}
    </div>""",
        "FPA®销售", "Customer"))

    b = "".join(
        f'      <div class="cc" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">抱怨时需要什么</div>\n'
        f'        <div style="margin-top:1.2vh;display:grid;gap:.45vh">{lis(cs[k]["whenComplaining"])}</div>\n'
        f'      </div>' for k in order)
    add(slide(
        ("light", ""),
        "服务 · 抱怨", f"{tail + 6} / {total}",
        f"""    <div class="kicker" data-anim>出了问题时</div>
    <h2 class="h-xl" data-anim>客户抱怨时，他们需要什么</h2>
    <div class="grid-4" style="margin-top:5vh">
{b}
    </div>""",
        "FPA®客户服务", "Complaint"))

    # ---- 培训表现 ----
    rows = "".join(
        f'      <div class="cc cc-tight" style="--cc:{cs[k]["color"]}" data-anim>\n'
        f'        <div class="cc-name">培训中的表现</div>\n'
        f'        <div style="margin-top:1vh;display:grid;gap:.3vh">{lis(cs[k]["inTraining"])}</div>\n'
        f'      </div>' for k in order)
    add(slide(
        ("dark", ""),
        "培训 · 组织", f"{tail + 7} / {total}",
        f"""    <div class="kicker" data-anim>课堂上与组织里</div>
    <h2 class="h-xl" data-anim>培训中的表现</h2>
    <div class="grid-4" style="margin-top:5vh">
{rows}
    </div>
    <p class="lead" style="margin-top:4vh;max-width:70vw" data-anim>
      团队不能发挥其功效的最大原因是：成员的个性差别被无端忽视。
    </p>""",
        "FPA®培训 / 团队合作", "Training"))

    # ---- 婚恋与教育 ----
    add(slide(
        ("hero dark", ""),
        "延伸 · 生活", f"{tail + 8} / {total}",
        f"""    <div class="frame" style="display:grid;gap:3.5vh;align-content:center;min-height:78vh">
      <div class="kicker" data-anim>不止于工作</div>
      <h1 class="h-hero" style="font-size:6.4vw" data-anim>婚恋 与 教育</h1>
      <div style="display:grid;gap:1.4vh;max-width:62vw;margin-top:2vh" data-anim>
        <div class="li">更好地理解你的爱人</div>
        <div class="li">欣赏伴侣的不同之处，以及他对这段关系的独特贡献</div>
        <div class="li">认识到冲突的原因，平心静气坐下来双向讨论怎么解决</div>
        <div class="li">肯定双方对婚姻的贡献</div>
        <div class="li">认识到配偶在关系中得不到满足的需要</div>
        <div class="li">重新认识自己的行为，适当调整以满足双方需要</div>
      </div>
    </div>""",
        "FPA®婚恋关系 / 子女教育", "Beyond Work"))

    # ---- 收束 ----
    add(slide(
        ("light", ""),
        "收束 · Takeaway", f"{tail + 9} / {total}",
        f"""    <div class="kicker" data-anim>带上这三句话走</div>
    <h2 class="h-xl" data-anim>了解自己 · 理解他人 · 高效协作</h2>
    <div class="grid-3" style="margin-top:6vh">
      <div class="cc" style="--cc:{cs['red']['color']}" data-anim>
        <div class="cc-name">先看清自己</div>
        <div class="cc-line">你的长处是什么，它用过头会变成什么样。</div>
      </div>
      <div class="cc" style="--cc:{cs['blue']['color']}" data-anim>
        <div class="cc-name">再理解他人</div>
        <div class="cc-line">别人不是针对你，他只是另一种颜色。</div>
      </div>
      <div class="cc" style="--cc:{cs['green']['color']}" data-anim>
        <div class="cc-name">最后换方式</div>
        <div class="cc-line">用对方需要的方式沟通，而不是你自己习惯的方式。</div>
      </div>
    </div>
    <p class="lead" style="margin-top:5vh;max-width:64vw" data-anim>
      没有最好，只有更好。
    </p>""",
        "内容整理自性格色彩培训讲义 · 仅作学习交流", "Takeaway"))

    return "\n".join(S)


def main():
    if not TEMPLATE.exists():
        sys.exit(f"找不到 guizang-ppt-skill 模板：{TEMPLATE}")

    data = json.loads((ROOT / "data" / "colors.json").read_text(encoding="utf-8"))
    colors, order = data["colors"], data["order"]

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("[必填] 替换为 PPT 标题 · Deck Title", TITLE)
    html = html.replace("</title>", "</title>\n" + FAVICON, 1)
    html = html.replace("</style>", EXTRA_CSS + "\n  </style>")
    html = html.replace("<!-- SLIDES_HERE -->", build(colors, order))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    count = html.count('<section class="slide')
    print(f"已生成 {OUT}")
    print(f"共 {count} 页（{OUT.stat().st_size / 1024:.1f} KB）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
