/*
 * トップページの演出：最初の画面ではアプリのアイコンがヒーローの左右に浮かび、
 * スクロールに合わせて下のアプリ一覧の本来の位置へ飛んでいって収まる。
 * 左右に十分な余白がない画面幅と「視差効果を減らす」設定では何もしない。
 */
(function () {
  var hero = document.querySelector('.hero');
  var grid = document.querySelector('.app-grid');
  if (!hero || !grid || !window.requestAnimationFrame) return;

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.app-card'));
  var CONTENT_HALF = 360;   // ヒーロー中央のテキスト幅の半分（px）
  var MIN_SIDE = 110;       // 左右の余白がこれ未満なら演出しない
  var TARGET = 60;          // 一覧のアイコンの大きさ（px）

  // 左右それぞれの配置（余白内の相対位置 x, ヒーロー内の相対位置 y, 大きさ, 傾き）
  var SLOTS = [
    [0.30, 0.10, 76, -8], [0.78, 0.20, 56, 6], [0.18, 0.36, 60, 5],
    [0.62, 0.45, 84, -4], [0.30, 0.62, 52, 10], [0.80, 0.70, 64, -9],
    [0.15, 0.86, 70, 4], [0.55, 0.92, 48, -6], [0.48, 0.25, 44, 12]
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
      el: a, card: card, icon: icon, side: side, slot: slot,
      delay: (Math.floor(i / 2) % SLOTS.length) / SLOTS.length * 0.3,
      start: null
    };
  });

  var enabled = false;
  var endScroll = 1;
  var ticking = false;

  function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  function measure() {
    var vw = document.documentElement.clientWidth;
    var sideW = vw / 2 - CONTENT_HALF - 24;
    enabled = !reduce.matches && sideW >= MIN_SIDE;
    document.body.classList.toggle('fly-on', enabled);
    if (!enabled) return;

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
    });
    var gridTop = grid.getBoundingClientRect().top + window.scrollY;
    endScroll = Math.max(1, gridTop - window.innerHeight * 0.45);
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
      var sy = s.y + window.scrollY;
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
