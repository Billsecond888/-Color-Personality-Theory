/* ============================================================
   性格色彩测评 · 引擎
   读 window.FPA_DATA（由 scripts/build.py 从 data/*.json 生成）
   页面里没有任何写死的文案，改内容只需改 data/ 后重新 build
   ============================================================ */
(function () {
  'use strict';

  var DATA = window.FPA_DATA;
  if (!DATA) { document.body.innerHTML = '<p style="padding:40px">数据未加载，请先运行 python3 scripts/build.py</p>'; return; }

  var COLORS = DATA.colors.colors;
  var ORDER = DATA.colors.order;          // ["red","blue","yellow","green"]
  var QUESTIONS = DATA.questions;
  var TOTAL = QUESTIONS.length;
  var KEY_TO_COLOR = {};                  // A -> red
  ORDER.forEach(function (id) { KEY_TO_COLOR[COLORS[id].key] = id; });

  var answers = new Array(TOTAL).fill(null);
  var current = 0;
  var locked = false;

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* 把主色写进 CSS 变量，页面所有强调色自动跟着变 */
  function applyPick(id) {
    var hex = COLORS[id].color;
    var r = parseInt(hex.slice(1, 3), 16);
    var g = parseInt(hex.slice(3, 5), 16);
    var b = parseInt(hex.slice(5, 7), 16);
    var root = document.documentElement.style;
    root.setProperty('--pick', hex);
    root.setProperty('--pick-soft', 'rgba(' + r + ',' + g + ',' + b + ',0.10)');
    root.setProperty('--pick-line', 'rgba(' + r + ',' + g + ',' + b + ',0.35)');
  }

  function show(name) {
    $$('.view').forEach(function (v) { v.classList.toggle('is-active', v.dataset.view === name); });
    window.scrollTo(0, 0);
  }

  function list(items, cls) {
    if (!items || !items.length) return '';
    return '<ul class="list ' + (cls || '') + '">' +
      items.map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') + '</ul>';
  }

  function tags(items, cls) {
    if (!items || !items.length) return '';
    return '<div class="tags">' +
      items.map(function (i) { return '<span class="tag ' + (cls || '') + '">' + esc(i) + '</span>'; }).join('') +
      '</div>';
  }

  /* ---------------- 开场 ---------------- */
  function renderStart() {
    var chips = ORDER.map(function (id) {
      var c = COLORS[id];
      return '<span class="chip"><span class="dot" style="background:' + c.color + '"></span>' + esc(c.name) + '</span>';
    }).join('');
    var el = $('#startInner');
    if (!el) return;
    el.innerHTML =
      '<p class="eyebrow">Color Personality</p>' +
      '<h1>性格色彩测评</h1>' +
      '<p class="lede">30 道题，凭第一感觉选。没有对错，只有你更像哪一个。</p>' +
      '<div class="start-meta">' +
        '<div><dt>' + TOTAL + '</dt><dd>道题</dd></div>' +
        '<div><dt>约 8</dt><dd>分钟</dd></div>' +
        '<div><dt>4</dt><dd>种性格色彩</dd></div>' +
      '</div>' +
      '<div class="color-chips">' + chips + '</div>' +
      '<div class="btn-row">' +
        '<button class="btn" id="btnStart">开始测试</button>' +
        '<a class="btn btn-ghost" href="colors.html">先看四色全览</a>' +
      '</div>';
    $('#btnStart').addEventListener('click', function () { show('quiz'); renderQuestion(0); });
  }

  /* ---------------- 答题 ---------------- */
  function renderQuestion(i) {
    current = i;
    var q = QUESTIONS[i];
    var box = $('#quizInner');
    box.innerHTML =
      '<div class="progress"><div class="wrap">' +
        '<div class="progress-row"><span class="progress-num">' + (i + 1) + ' / ' + TOTAL + '</span>' +
        '<span>选择最符合你的一项</span></div>' +
        '<div class="bar"><span id="barFill"></span></div>' +
      '</div></div>' +
      '<div class="wrap">' +
        '<p class="q-text">' + esc(q.question) + '</p>' +
        '<div class="options" id="opts"></div>' +
        '<div class="q-nav">' +
          '<button class="link-btn" id="btnPrev"' + (i === 0 ? ' disabled' : '') + '>上一题</button>' +
          '<span class="muted">键盘 1-4 可直接选择</span>' +
        '</div>' +
      '</div>';

    var opts = $('#opts');
    ['A', 'B', 'C', 'D'].forEach(function (k) {
      var cid = KEY_TO_COLOR[k];
      var btn = document.createElement('button');
      btn.className = 'opt' + (answers[i] === k ? ' is-picked' : '');
      btn.style.setProperty('--pick', COLORS[cid].color);
      btn.style.setProperty('--pick-soft', hexA(COLORS[cid].color, 0.08));
      btn.innerHTML =
        '<span class="opt-key">' + k + '</span><span>' + esc(q.options[k]) + '</span>';
      btn.addEventListener('click', function () { pick(k); });
      opts.appendChild(btn);
    });

    $('#barFill').style.width = ((i) / TOTAL * 100) + '%';
    var prev = $('#btnPrev');
    prev.addEventListener('click', function () { if (i > 0) renderQuestion(i - 1); });
  }

  function hexA(hex, a) {
    var r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
    return 'rgba(' + r + ',' + g + ',' + b + ',' + a + ')';
  }

  function pick(k) {
    if (locked) return;
    locked = true;
    answers[current] = k;
    var btns = $$('#opts .opt');
    btns.forEach(function (b) {
      b.classList.toggle('is-picked', b.querySelector('.opt-key').textContent === k);
    });
    setTimeout(function () {
      locked = false;
      if (current < TOTAL - 1) renderQuestion(current + 1);
      else finish();
    }, 260);
  }

  /* ---------------- 计分 ---------------- */
  function score() {
    var counts = {};
    ORDER.forEach(function (id) { counts[id] = 0; });
    answers.forEach(function (k) { if (k) counts[KEY_TO_COLOR[k]] += 1; });

    // 并列时按 A > B > C > D 的固定顺序取前者，ORDER 已按此顺序排列
    var ranked = ORDER.slice().sort(function (a, b) { return counts[b] - counts[a]; });
    return { counts: counts, ranked: ranked, primary: ranked[0], secondary: ranked[1] };
  }

  /* ---------------- 结果 ---------------- */
  function finish() {
    var s = score();
    var p = COLORS[s.primary];
    var sec = COLORS[s.secondary];
    applyPick(s.primary);

    var ratios = ORDER.map(function (id) {
      var c = COLORS[id], n = s.counts[id], pct = Math.round(n / TOTAL * 100);
      return '<div class="ratio">' +
        '<span class="ratio-name" style="color:' + (id === s.primary ? c.color : 'var(--ink-2)') + ';font-weight:' + (id === s.primary ? 600 : 400) + '">' + esc(c.name) + '</span>' +
        '<span class="ratio-bar"><i data-w="' + pct + '" style="background:' + c.color + '"></i></span>' +
        '<span class="ratio-val">' + n + ' · ' + pct + '%</span>' +
      '</div>';
    }).join('');

    var tc = p.teamContribution || {};
    var teamwork = p.teamwork || {};

    var html = ''
      + '<section class="wrap hero">'
      +   '<p class="eyebrow">你的性格主色</p>'
      +   '<span class="hero-badge"><span class="dot" style="background:' + p.color + '"></span>' + esc(p.name) + '性格</span>'
      +   '<div class="hero-title">' + esc(p.name) + '</div>'
      +   '<p class="hero-motto">' + esc(p.motto) + '</p>'
      + '</section>'

      + '<section class="wrap section">'
      +   '<div class="section-head"><h2>四色分布</h2><span class="muted">共 ' + TOTAL + ' 题</span></div>'
      +   '<div class="ratio-list">' + ratios + '</div>'
      + '</section>'

      + '<section class="wrap section">'
      +   '<div class="section-head"><h2>核心档案</h2></div>'
      +   '<dl class="facts">'
      +     '<div class="fact"><dt>最大的长处</dt><dd>' + esc(p.maxStrength) + '</dd></div>'
      +     '<div class="fact"><dt>最大的短处</dt><dd>' + esc(p.maxWeakness) + '</dd></div>'
      +     '<div class="fact"><dt>基本动机</dt><dd>' + esc((p.basicMotivation || []).join(' · ')) + '</dd></div>'
      +     '<div class="fact"><dt>对外界的需求</dt><dd>' + esc((p.needsFromOutside || []).join(' · ')) + '</dd></div>'
      +   '</dl>'
      + '</section>'

      + '<section class="wrap section">'
      +   '<div class="section-head"><h2>优势与过当</h2><span class="muted">过当 = 优势用过了头</span></div>'
      +   '<div class="two-col">'
      +     '<div class="panel accent"><h3><span class="dot" style="background:' + p.color + '"></span>优势</h3>' + tags(p.strengths, 'pick') + '</div>'
      +     '<div class="panel warn"><h3>优势过当</h3>' + tags(p.overuses) + '</div>'
      +   '</div>'
      + '</section>'

      + '<section class="wrap section">'
      +   '<div class="section-head"><h2>典型人物</h2></div>'
      +   '<div class="panel"><div class="figure">'
      +     '<span class="figure-name" style="color:' + p.color + '">' + esc(p.figure.name) + '</span>'
      +     '<span class="figure-desc">' + esc(p.figure.desc) + '</span>'
      +   '</div></div>'
      + '</section>'

      + '<section class="wrap section">'
      +   '<div class="section-head"><h2>在团队里</h2></div>'
      +   '<div class="panel">'
      +     '<div class="sub-block"><h4>发挥优势时</h4>' + list(tc.whenStrength, 'pick') + '</div>'
      +     '<div class="sub-block"><h4>优势过当时</h4>' + list(tc.whenOveruse) + '</div>'
      +     '<div class="sub-block"><h4>运用优势得当时</h4>' + list(tc.whenApplied, 'pick') + '</div>'
      +     '<div class="sub-block"><h4>团队合作中的优势</h4><p class="muted" style="font-size:14px;line-height:1.7">' + esc(teamwork.strength) + '</p></div>'
      +     '<div class="sub-block"><h4>团队合作中的过当</h4><p class="muted" style="font-size:14px;line-height:1.7">' + esc(teamwork.overuse) + '</p></div>'
      +   '</div>'
      + '</section>'

      + '<section class="wrap section">'
      +   '<div class="section-head"><h2>怎么和' + esc(p.name) + '打交道</h2></div>'
      +   '<div class="two-col">'
      +     '<div class="panel"><h3>沟通方式</h3>' + list(p.howToCommunicate, 'pick') + '</div>'
      +     '<div class="panel"><h3>TA 是你的上司</h3>' + list(p.howToInfluenceBoss, 'pick') + '</div>'
      +     '<div class="panel"><h3>TA 是你的部属</h3>' + list(p.howToLeadSubordinate, 'pick') + '</div>'
      +     '<div class="panel"><h3>适合的方向</h3>' + list(p.careerDirection, 'pick') + '</div>'
      +   '</div>'
      + '</section>'

      + '<section class="wrap section">'
      +   '<div class="section-head"><h2>辅色：' + esc(sec.name) + '</h2>' +
          '<span class="muted">' + s.counts[s.secondary] + ' 题 · ' + Math.round(s.counts[s.secondary] / TOTAL * 100) + '%</span></div>'
      +   '<div class="panel" style="border-left:3px solid ' + sec.color + '">'
      +     '<p class="muted" style="font-size:14px;line-height:1.75;margin-bottom:12px">'
      +       esc(sec.motto) + ' 你的第二特质带一点' + esc(sec.name) + '底色：长处是「' + esc(sec.maxStrength) + '」，要留意「' + esc(sec.maxWeakness) + '」。'
      +     '</p>'
      +     tags((sec.strengths || []).slice(0, 4))
      +   '</div>'
      + '</section>'

      + '<section class="wrap section">'
      +   '<div class="btn-row">'
      +     '<a class="btn" href="colors.html">看四色全览</a>'
      +     '<button class="btn btn-ghost" id="btnAgain">重新测试</button>'
      +   '</div>'
      + '</section>';

    $('#resultInner').innerHTML = html;
    show('result');

    requestAnimationFrame(function () {
      $$('#resultInner .ratio-bar i').forEach(function (i) { i.style.width = i.dataset.w + '%'; });
    });

    $('#btnAgain').addEventListener('click', function () {
      answers = new Array(TOTAL).fill(null);
      show('start'); renderStart();
    });
  }

  /* ---------------- 四色全览页 ---------------- */
  function renderColorsPage() {
    var host = $('#colorsInner');
    if (!host) return;
    host.innerHTML =
      '<p class="eyebrow">Color Personality</p>' +
      '<h1>四种性格色彩</h1>' +
      '<p class="lede">同一套解析口径，不测也能看。<a href="index.html" style="color:var(--ink)">去测一下</a>可以看到自己落在哪一格。</p>' +
      '<div class="color-grid section">' +
      ORDER.map(function (id) {
        var c = COLORS[id];
        return '<article class="color-card" style="--pick:' + c.color + ';--pick-soft:' + hexA(c.color, 0.1) + ';--pick-line:' + hexA(c.color, 0.35) + '">' +
          '<div class="cc-head"><span class="cc-name">' + esc(c.name) + '</span>' +
          '<span class="cc-motto">' + esc(c.motto) + '</span></div>' +
          '<p class="cc-meta">最大的长处：<strong>' + esc(c.maxStrength) + '</strong>　最大的短处：<strong>' + esc(c.maxWeakness) + '</strong></p>' +
          '<p class="cc-meta">基本动机：<strong>' + esc((c.basicMotivation || []).join(' · ')) + '</strong></p>' +
          '<div style="margin:14px 0">' + tags(c.strengths, 'pick') + '</div>' +
          '<p class="muted" style="margin-bottom:6px">优势过当</p>' +
          tags(c.overuses) +
          '<div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--line-soft)">' +
            '<p class="muted" style="margin-bottom:6px">怎么沟通</p>' + list(c.howToCommunicate, 'pick') +
          '</div>' +
        '</article>';
      }).join('') +
      '</div>';
  }

  /* ---------------- 键盘 ---------------- */
  document.addEventListener('keydown', function (e) {
    var quiz = $('.view[data-view="quiz"]');
    if (!quiz || !quiz.classList.contains('is-active')) return;
    var map = { '1': 'A', '2': 'B', '3': 'C', '4': 'D', 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D' };
    var k = map[e.key.toLowerCase()];
    if (k) { e.preventDefault(); pick(k); return; }
    if (e.key === 'ArrowLeft' && current > 0) renderQuestion(current - 1);
  });

  /* ---------------- 启动 ---------------- */
  renderStart();
  renderColorsPage();
  applyPick('red');
})();
