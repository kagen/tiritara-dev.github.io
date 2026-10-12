/*
 * トップページの演出：最初の画面ではアプリのアイコンがヒーローの左右に浮かび、
 * スクロールに合わせて下のアプリ一覧の本来の位置へ飛んでいって収まる。
 * 左右に余白がない画面幅（スマホなど）では、ロゴのまわりに雲のように浮かべる。
 * 「視差効果を減らす」設定では何もしない。
 */
(function () {
  var hero = document.querySelector('.hero');
  var grid = document.querySelector('.app-grid');
  if (!hero || !grid || !window.requestAnimationFrame) return;

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.app-card'));
  var CONTENT_HALF = 360;   // ヒーロー中央のテキスト幅の半分（px）
  var MIN_SIDE = 110;       // 左右の余白がこれ未満ならロゴのまわりに浮かべる
  var TARGET = 60;          // 一覧のアイコンの大きさ（px）

  // 左右それぞれの配置（余白内の相対位置 x, ヒーロー内の相対位置 y, 大きさ, 傾き）
  var SLOTS = [
    [0.30, 0.10, 76, -8], [0.78, 0.20, 56, 6], [0.18, 0.36, 60, 5],
    [0.62, 0.45, 84, -4], [0.30, 0.62, 52, 10], [0.80, 0.70, 64, -9],
    [0.15, 0.86, 70, 4], [0.55, 0.92, 48, -6], [0.48, 0.25, 44, 12]
  ];
  // ロゴのまわりの配置（画面幅に対する x, ロゴ中心からの縦のずれ px, 大きさ, 傾き）
  var CLOUD = [
    [0.10, -120, 44, -8], [0.30, -138, 36, 6], [0.52, -142, 40, -4], [0.74, -132, 48, 8],
    [0.93, -105, 38, -6], [0.17, -55, 52, 5], [0.84, -50, 46, -10], [0.04, 5, 36, 10],
    [0.28, 15, 40, -5], [0.72, 0, 42, 7], [0.97, 35, 34, -4], [0.14, 75, 46, -9],
    [0.87, 85, 50, 6], [0.38, 120, 38, 8], [0.62, 130, 44, -7], [0.06, 150, 40, 4],
    [0.95, 155, 38, -5]
  ];

  var layer = document.createElement('div');
  layer.className = 'flyers';
  layer.setAttribute('aria-hidden', 'true');
  document.body.appendChild(layer);

  var flyers = cards.map(function (card, i) {
    var icon = card.querySelector('.app-icon');
    var a = document.createElement('a');
    a.className = 'flyer';
    a.href = card.getAttribute('href');
    a.tabIndex = -1;
    var inner = document.createElement('span');
    inner.className = 'flyer-bob';
    inner.style.animationDuration = (5 + (i * 7) % 5) + 's';
    inner.style.animationDelay = (-(i * 1.3) % 6) + 's';
    var img = document.createElement('img');
    img.src = icon.getAttribute('src');
    img.alt = '';
    inner.appendChild(img);
    a.appendChild(inner);
    layer.appendChild(a);
    var side = i % 2;                       // 0 = 左, 1 = 右
    var slot = SLOTS[Math.floor(i / 2) % SLOTS.length];
    return {
      el: a, card: card, icon: icon, side: side, slot: slot, index: i,
      delay: 0, start: null
    };
  });

  var enabled = false;
  var logo = hero.querySelector('.hero-logo');
  var endScroll = 1;
  var ticking = false;

  function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  function measure() {
    var vw = document.documentElement.clientWidth;
    var sideW = vw / 2 - CONTENT_HALF - 24;
    var side = sideW >= MIN_SIDE;
    enabled = !reduce.matches && (side || !!logo);
    document.body.classList.toggle('fly-on', enabled);
    document.body.classList.toggle('fly-side', enabled && side);
    document.body.classList.toggle('fly-cloud', enabled && !side);
    if (!enabled) return;
    if (side) placeSides(vw, sideW); else placeCloud(vw);
    var gridTop = grid.getBoundingClientRect().top + window.scrollY;
    endScroll = Math.max(1, gridTop - window.innerHeight * 0.45);
  }

  function placeCloud(vw) {
    var r = logo.getBoundingClientRect();
    var cy = r.top + window.scrollY + r.height / 2;
    flyers.forEach(function (f, i) {
      var c = CLOUD[i % CLOUD.length];
      var size = c[2];
      f.start = {
        x: window.scrollX + Math.min(vw - size - 8, Math.max(8, c[0] * vw - size / 2)),
        y: cy + c[1] - size / 2,
        size: size,
        rot: c[3],
        // スマホでは雲ごとページと一緒に流れ、その途中で一覧へ降りていく
        scrolls: true
      };
      f.delay = (i % CLOUD.length) / CLOUD.length * 0.3;
    });
  }

  function placeSides(vw, sideW) {
    // 開始位置は画面基準で持つ。スクロールしてもその場に浮かんだまま、一覧へ降りていく
    var heroRect = hero.getBoundingClientRect();
    var top = heroRect.top + window.scrollY + 24;
    var h = heroRect.height - 72;
    var sx = window.scrollX;
    flyers.forEach(function (f) {
      var s = f.slot;
      // 左右の余白内に配置。右側は左右反転させて単調にならないようにする
      var fx = f.side === 0 ? s[0] : 1 - s[0];
      var x0 = f.side === 0 ? 24 : vw / 2 + CONTENT_HALF;
      f.start = {
        x: sx + x0 + fx * (sideW - s[2]),
        y: top + (f.side === 0 ? s[1] : 1 - s[1]) * (h - s[2]),
        size: s[2],
        rot: f.side === 0 ? s[3] : -s[3]
      };
      f.delay = (Math.floor(f.index / 2) % SLOTS.length) / SLOTS.length * 0.3;
    });
  }

  function render() {
    ticking = false;
    if (!enabled) return;
    var p = clamp(window.scrollY / endScroll);
    var landed = p >= 1;
    grid.classList.toggle('icons-landed', landed);
    layer.classList.toggle('is-landed', landed);
    if (landed) return;

    // 先にすべての位置を読み取ってから書き込む（レイアウトの再計算を1回に抑える）
    var targets = flyers.map(function (f) {
      if (f.card.hidden) return null;
      var r = f.icon.getBoundingClientRect();
      return { x: r.left + window.scrollX, y: r.top + window.scrollY };
    });
    flyers.forEach(function (f, i) {
      var t = targets[i];
      if (!t) { f.el.style.opacity = '0'; return; }
      var k = ease(clamp((p - f.delay) / (1 - f.delay)));
      var s = f.start;
      var size = s.size + (TARGET - s.size) * k;
      var x = s.x + (t.x - s.x) * k;
      var sy = s.scrolls ? s.y : s.y + window.scrollY;
      var y = sy + (t.y - sy) * k;
      var rot = s.rot * (1 - k);
      f.el.style.opacity = '';
      f.el.style.width = f.el.style.height = size + 'px';
      f.el.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0) rotate(' + rot + 'deg)';
      f.el.style.setProperty('--bob', (1 - k).toFixed(3));
    });
  }

  function request() {
    if (!ticking) { ticking = true; requestAnimationFrame(render); }
  }
  function refresh() { measure(); request(); }

  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', refresh);
  window.addEventListener('load', refresh);
  if (reduce.addEventListener) reduce.addEventListener('change', refresh);
  // 絞り込みでカードの位置が変わったときも追従させる
  grid.addEventListener('transitionend', request);
  document.querySelectorAll('.chip[data-filter]').forEach(function (c) {
    c.addEventListener('click', function () { setTimeout(refresh, 0); });
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);
  refresh();
})();
