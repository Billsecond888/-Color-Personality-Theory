# 性格色彩测评 · Color Personality

一套零依赖的静态测评工具：30 道题测出你的性格主色，并给出基于培训讲义的完整解析。

在线体验：把 `web/` 目录丢到任意静态托管（GitHub Pages / Nginx / 对象存储）即可，无需构建。
本地预览：直接双击 `web/index.html`，不需要起服务器。

## 它做什么

1. **测试** — 30 道四选一，逐题作答，选完自动进入下一题。
2. **解析** — 统计 A/B/C/D 的选择次数，得出主色、辅色和四色占比，再按主色展开完整解析。

```
答题 → 计分（A红 B蓝 C黄 D绿）→ 主色揭晓 + 四色占比 → 主色解析 → 辅色提示
```

## 目录结构

```
.
├── data/                   唯一数据源，改内容只动这里
│   ├── colors.json         四色完整解析（长处/短处/动机/需求/优势/过当/团队/沟通/管理/职业）
│   └── questions.json      30 道题库
├── scripts/
│   ├── parse_questions.py  Excel 题库 → questions.json
│   └── build.py            data/*.json → web/assets/data.js
├── web/                    可直接托管的静态站点
│   ├── index.html          测试页（主入口）
│   ├── colors.html         四色全览页
│   └── assets/
│       ├── style.css
│       ├── app.js
│       └── data.js         自动生成，勿手改
└── docs/解析口径.md         解析内容从哪来、怎么校正
```

## 改内容不用改代码

解析文案和题库都在 `data/` 下，改完跑一次打包：

```bash
python3 scripts/build.py
```

`web/` 里没有任何写死的文案，页面全部读 `data.js` 渲染。

### 重新导入题库

```bash
pip install openpyxl
python3 scripts/parse_questions.py "性格色彩测试.xlsx"
python3 scripts/build.py
```

脚本会逐题打印四个选项的字数，缺选项会标出来，方便肉眼核对。

## 计分口径

- 每道题记一个字母：A=红，B=蓝，C=黄，D=绿
- 30 题答完后统计四个字母的命中次数
- 次数最多的是**主色**，第二多的是**辅色**
- 出现并列时，按 A > B > C > D 的固定顺序取前者
- 占比 = 该色命中数 ÷ 30

## 来源与授权

- 题库：2023-12 版《性格色彩测试》Excel
- 解析：《性格分析之性格色彩 - 2026 Leader Offsite》PPT（31 页），逐条照录，未做内容校正
- 代码：MIT，见 [LICENSE](LICENSE)
- **内容授权另说**：讲义内容含 FPA® 注册商标，版权归原权利人。本仓库代码开源，内容仅作学习用途，**请勿用于商业培训或二次分发**。详见 [NOTICE](NOTICE.md)
