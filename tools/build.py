#!/usr/bin/env python3
"""data/projects.json と data/store.json から静的ページを生成する。

生成先: index.html, apps/<slug>/index.html, web/<slug>/index.html
使い方: python3 tools/build.py
ストアの掲載内容を更新したいときは先に tools/fetch_store_data.py を実行する。
"""
import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://tiritara-dev.github.io/"
CONTACT = "tiritara.dev@gmail.com"
PLAY_DEV = "https://play.google.com/store/apps/dev?id=5924475083153244319"
IOS_DEV = "https://apps.apple.com/jp/developer/id6800308304"
PRIVACY_ANDROID = "https://kagen.github.io/tiritara-privacy/"
PRIVACY_IOS = "https://kagen.github.io/tiritara-privacy/ios.html"
GITHUB = "https://github.com/kagen"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
    '&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">'
)

ICON_ANDROID = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M4 18a8 8 0 0 1 16 0zM8 14.2a1.1 1.1 0 1 0 2.2 0a1.1 1.1 0 1 0-2.2 0zM13.8 14.2a1.1 1.1 0 1 0 2.2 0a1.1 1.1 0 1 0-2.2 0z"/>'
    '<path d="M7.6 10.4 5.8 7.4M16.4 10.4l1.8-3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
)
ICON_APPLE = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M16.37 12.76c-.02-2.3 1.88-3.4 1.96-3.46-1.07-1.56-2.73-1.78-3.32-1.8-1.41-.14-2.76.83-3.48.83-.72 0-1.82-.81-3-.79-1.54.02-2.96.9-3.76 2.28-1.6 2.78-.41 6.9 1.15 9.16.76 1.1 1.67 2.34 2.86 2.3 1.15-.05 1.58-.74 2.97-.74 1.38 0 1.77.74 2.98.72 1.23-.02 2.01-1.12 2.76-2.23.87-1.28 1.23-2.52 1.25-2.58-.03-.01-2.4-.92-2.42-3.65zM14.1 6.01c.63-.77 1.06-1.83.94-2.89-.91.04-2.01.61-2.66 1.37-.58.67-1.1 1.76-.96 2.8 1.01.08 2.05-.52 2.68-1.28z"/></svg>'
)
ICON_PLAY = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="#00d7fe" d="M3.6 1.8 13.5 12l-9.9 10.2c-.36-.2-.6-.6-.6-1.07V2.87c0-.47.24-.87.6-1.07z"/>'
    '<path fill="#ffce00" d="M17.1 8.4 20.4 10.3c.95.55.95 1.85 0 2.4l-3.3 1.9-3.6-2.6z"/>'
    '<path fill="#ff3a44" d="M13.5 12 3.6 22.2c.36.2.83.22 1.24-.02L17.1 14.6z"/>'
    '<path fill="#00f076" d="M3.6 1.8 13.5 12l3.6-3.6L4.84 1.82c-.41-.24-.88-.22-1.24-.02z"/>'
    '</svg>'
)
ICON_GLOBE = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/></svg>'
)


def e(s):
    return escape(str(s), quote=True)


def page(*, title, description, prefix, body, canonical, og_image=None, extra_head="", nav_prefix=None):
    nav_prefix = prefix if nav_prefix is None else nav_prefix
    og = f'<meta property="og:image" content="{e(SITE + og_image)}">' if og_image else ""
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="dark light">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(SITE + canonical)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="tiritara.dev">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(SITE + canonical)}">
{og}
<meta name="twitter:card" content="summary">
<link rel="icon" href="{prefix}tiritara_logo_t.png">
<link rel="apple-touch-icon" href="{prefix}tiritara_logo_t.png">
{FONTS}
<link rel="stylesheet" href="{prefix}assets/site.css">
{extra_head}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{prefix or './'}"><img src="{prefix}tiritara_logo_t.png" alt="" width="30" height="30">tiritara.dev</a>
    <nav class="nav" aria-label="メイン">
      <a href="{nav_prefix}index.html#apps">アプリ</a>
      <a href="{nav_prefix}index.html#web">Web</a>
      <a href="{nav_prefix}index.html#tools">ツール</a>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>© {date.today().year} tiritara.dev</p>
    <nav class="footer-links" aria-label="フッター">
      <a href="{PLAY_DEV}" target="_blank" rel="noopener">Google Play</a>
      <a href="{IOS_DEV}" target="_blank" rel="noopener">App Store</a>
      <a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
      <a href="{PRIVACY_ANDROID}" target="_blank" rel="noopener">プライバシーポリシー</a>
      <a href="mailto:{CONTACT}">お問い合わせ</a>
    </nav>
  </div>
</footer>
</body>
</html>
"""


def platforms_html(app):
    out = []
    if app.get("play"):
        out.append(f'<span class="platform">{ICON_ANDROID}Android</span>')
    if app.get("ios"):
        out.append(f'<span class="platform">{ICON_APPLE}iOS</span>')
    return '<div class="platforms">' + "".join(out) + "</div>"


def app_card(app, store, prefix):
    s = store[app["slug"]]
    tags = ["all", app["genre"]] + (["ios"] if app.get("ios") else [])
    return f"""<a class="app-card" href="{prefix}apps/{app['slug']}/" data-tags="{' '.join(tags)}">
  <div class="app-card-top">
    <img class="app-icon" src="{prefix}{s['icon']}" alt="" width="60" height="60" loading="lazy">
    <div><h3>{e(app['name'])}</h3><p class="cat">{e(app['category'])}</p></div>
  </div>
  <p class="tagline">{e(app['tagline'])}</p>
  {platforms_html(app)}
  <span class="arrow" aria-hidden="true">↗</span>
</a>"""


QR_SVG = """<svg viewBox="0 0 29 29" aria-hidden="true" shape-rendering="crispEdges"><rect width="29" height="29" rx="2" fill="#fff"/><g fill="#0c1222">
<path d="M2 2h7v7H2zM3 3v5h5V3zM4 4h3v3H4zM20 2h7v7h-7zM21 3v5h5V3zM22 4h3v3h-3zM2 20h7v7H2zM3 21v5h5v-5zM4 22h3v3H4z"/>
<path d="M11 2h2v2h-2zM14 3h2v3h-2zM11 6h2v3h-2zM17 5h1v2h-1zM11 11h3v2h-3zM15 10h2v2h-2zM18 11h3v1h-3zM22 11h2v3h-2zM25 11h2v2h-2zM2 11h2v2H2zM5 12h3v2H5zM9 10h1v4H9zM12 14h2v2h-2zM16 13h3v3h-3zM20 15h2v2h-2zM24 15h3v2h-3zM2 15h3v2H2zM7 16h2v2H7zM11 17h2v2h-2zM14 18h3v2h-3zM18 18h2v3h-2zM21 19h3v2h-3zM25 18h2v3h-2zM11 21h2v3h-2zM14 22h2v2h-2zM17 23h3v2h-3zM21 22h2v2h-2zM24 23h3v2h-3zM11 25h3v2h-3zM15 25h1v2h-1zM20 25h2v2h-2z"/>
</g></svg>"""


def qr_art():
    return f"""<div class="qr-art" aria-hidden="true"><div class="qr-box">{QR_SVG}
<div class="qr-text"><b>QR勤怠</b><span>09:00 — 出勤</span><br><span class="stamp">✓ 打刻しました</span></div></div></div>"""


def web_visual(site, prefix):
    if site.get("image"):
        return f'<img src="{prefix}{site["image"]}" alt="" loading="lazy" width="1200" height="630">'
    return qr_art()


def build_index(projects, store):
    apps, web, tools = projects["apps"], projects["web"], projects["tools"]
    n_ios = sum(1 for a in apps if a.get("ios"))
    n_android = sum(1 for a in apps if a.get("play"))
    cards = "\n".join(app_card(a, store, "") for a in apps)
    web_cards = "\n".join(
        f"""<a class="web-card" href="web/{w['slug']}/">
  <div class="web-visual">{web_visual(w, '')}</div>
  <div class="web-body"><h3>{e(w['name'])}</h3><p>{e(w['tagline'])}</p>
  <ul class="tags">{''.join(f'<li>{e(t)}</li>' for t in w['stack'])}</ul></div>
</a>"""
        for w in web
    )
    tool_items = "\n".join(
        f"""<li><a href="{e(t['url'])}" target="_blank" rel="noopener"><b>{e(t['name'])}</b><span>{e(t['tagline'])}</span>
<span class="tool-meta">{e(t['platform'])} · GitHub ↗</span></a></li>"""
        for t in tools
    )
    body = f"""<section class="hero">
  <div class="wrap">
    <img class="hero-logo" src="tiritara_logo_t.png" alt="tiritara.dev ロゴ" width="120" height="120">
    <p class="eyebrow">Indie app developer</p>
    <h1><span class="gradient-text">Code smarter.<br>Live smiler.</span></h1>
    <p class="hero-lead">tiritara.dev は、Android・iOS アプリと Web サービスを個人で企画・開発しています。毎日のちょっとした不便をなくすツールから、気軽に遊べるゲームまで。</p>
    <ul class="hero-stats">
      <li><b>{len(apps)}</b><span>公開中のアプリ</span></li>
      <li><b>{n_android}</b><span>Android</span></li>
      <li><b>{n_ios}</b><span>iOS</span></li>
      <li><b>{len(web)}</b><span>Web サービス</span></li>
    </ul>
  </div>
</section>

<section class="section" id="apps">
  <div class="wrap">
    <div class="section-head">
      <div>
        <p class="eyebrow">Apps</p>
        <h2>アプリ</h2>
        <p>Google Play と App Store で公開しているアプリです。</p>
      </div>
      <div class="chips" role="group" aria-label="アプリの絞り込み">
        <button class="chip" type="button" data-filter="all" aria-pressed="true">すべて</button>
        <button class="chip" type="button" data-filter="life" aria-pressed="false">暮らし・ツール</button>
        <button class="chip" type="button" data-filter="game" aria-pressed="false">ゲーム</button>
        <button class="chip" type="button" data-filter="ios" aria-pressed="false">iOS 対応</button>
      </div>
    </div>
    <div class="app-grid">
{cards}
    </div>
  </div>
</section>

<section class="section" id="web">
  <div class="wrap">
    <div class="section-head">
      <div>
        <p class="eyebrow">Web</p>
        <h2>Web サービス</h2>
        <p>ブラウザで使える Web サービス・業務システムです。</p>
      </div>
    </div>
    <div class="web-grid">
{web_cards}
    </div>
  </div>
</section>

<section class="section" id="tools">
  <div class="wrap">
    <div class="section-head">
      <div>
        <p class="eyebrow">Open source</p>
        <h2>ツール</h2>
        <p>GitHub で公開している小さなツールです。</p>
      </div>
    </div>
    <ul class="tool-list">
{tool_items}
    </ul>
  </div>
</section>

<section class="section" id="featured" aria-labelledby="featured-heading">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Featured</p><h2 id="featured-heading">ご紹介いただきました</h2></div></div>
    <div class="featured-card">
      <a class="featured-brand" href="https://otokuboo.com/" target="_blank" rel="noopener noreferrer">
        <img src="assets/otokuboo-logo.png" alt="とくぶーのお得日記" width="980" height="460" loading="lazy">
      </a>
      <div>
        <h3><a href="https://otokuboo.com/" target="_blank" rel="noopener noreferrer">とくぶーのお得日記</a></h3>
        <p>格安SIM・節約のブログを運営するとくぶーさんに、当サイトをご紹介いただきました。</p>
        <a class="text-link" href="https://otokuboo.com/partner/" target="_blank" rel="noopener noreferrer">紹介ページを見る <span aria-hidden="true">↗</span></a>
      </div>
    </div>
  </div>
</section>

<script>
(function () {{
  var chips = document.querySelectorAll('.chip[data-filter]');
  var cards = document.querySelectorAll('.app-card');
  chips.forEach(function (chip) {{
    chip.addEventListener('click', function () {{
      var f = chip.getAttribute('data-filter');
      chips.forEach(function (c) {{ c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); }});
      cards.forEach(function (card) {{
        card.hidden = card.getAttribute('data-tags').split(' ').indexOf(f) === -1;
      }});
    }});
  }});
}})();
</script>
<script src="assets/hero-fly.js" defer></script>"""
    html = page(
        title="tiritara.dev — Android・iOS アプリと Web サービスの個人開発",
        description="tiritara.dev が開発する Android・iOS アプリと Web サービスの紹介。DaZen、電車GPS目覚まし、Kattalyst、RosaNauts、和風六曜暦カレンダー、絵馬掛け、QR勤怠など。",
        prefix="",
        nav_prefix="",
        body=body,
        canonical="",
        og_image="tiritara_logo_t.png",
    )
    (ROOT / "index.html").write_text(html, encoding="utf-8")


def format_description(text):
    """ストアの説明文を見出し・箇条書き・段落に整形する。"""
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>" + "<br>".join(e(x) for x in para) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>")
            items.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if re.match(r"^[■◆●【]", line):
            flush()
            heading = re.sub(r"^[■◆●]\s*", "", line)
            out.append(f"<h3>{e(heading)}</h3>")
        elif re.match(r"^[・•\-–]\s*", line):
            if para:
                flush()
            items.append(re.sub(r"^[・•\-–]\s*", "", line))
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return "\n".join(out)


def store_buttons(app, s):
    btns = []
    if "play" in s:
        btns.append(
            f'<a class="store-btn" href="{e(s["play"]["url"])}" target="_blank" rel="noopener">{ICON_PLAY}'
            '<span><small>Android 版を</small><b>Google Play</b></span></a>'
        )
    if "ios" in s:
        btns.append(
            f'<a class="store-btn" href="{e(s["ios"]["url"])}" target="_blank" rel="noopener">{ICON_APPLE}'
            '<span><small>iPhone・iPad 版を</small><b>App Store</b></span></a>'
        )
    note = ""
    if "play" in s and "ios" not in s:
        note = '<p class="store-note">現在は Android 版のみ公開しています。</p>'
    elif "ios" in s and "play" not in s:
        note = '<p class="store-note">現在は iOS 版のみ公開しています。</p>'
    return '<div class="store-buttons">' + "".join(btns) + "</div>" + note


def build_app(app, projects, store):
    slug = app["slug"]
    s = store[slug]
    prefix = "../../"
    desc_src = s.get("play", s.get("ios"))["description"]
    if len(desc_src) < 200 and "ios" in s and len(s["ios"]["description"]) > len(desc_src):
        desc_src = s["ios"]["description"]
    ver = s.get("play", {}).get("version") or s.get("ios", {}).get("version") or ""
    updated = s.get("play", {}).get("updated", "")
    support = " / ".join(x for x, k in (("Android", "play"), ("iOS", "ios")) if k in s)

    rows = [("カテゴリ", e(app["category"])), ("対応", e(support))]
    if ver:
        rows.append(("バージョン", e(ver)))
    if updated:
        rows.append(("最終更新", e(updated)))
    rows.append(("開発者", "tiritara.dev"))
    links = []
    if "play" in s:
        links.append(f'<a href="{PRIVACY_ANDROID}?app={e(app["name"])}" target="_blank" rel="noopener">Android</a>')
    if "ios" in s:
        links.append(f'<a href="{PRIVACY_IOS}" target="_blank" rel="noopener">iOS</a>')
    rows.append(("プライバシー", " · ".join(links)))
    info = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)

    shots = "\n".join(
        f'<img src="{prefix}{p}" alt="{e(app["name"])} のスクリーンショット {i + 1}" loading="lazy">'
        for i, p in enumerate(s["screenshots"])
    )
    others = [a for a in projects["apps"] if a["slug"] != slug and a["genre"] == app["genre"]]
    others = (others + [a for a in projects["apps"] if a["slug"] != slug and a not in others])[:3]
    other_cards = "\n".join(app_card(a, store, prefix) for a in others)

    ld = {
        "@context": "https://schema.org",
        "@type": "MobileApplication",
        "name": app["name"],
        "description": app["tagline"],
        "applicationCategory": app["category"],
        "operatingSystem": support,
        "image": SITE + s["icon"],
        "author": {"@type": "Organization", "name": "tiritara.dev", "url": SITE},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "sameAs": [s[k]["url"] for k in ("play", "ios") if k in s],
    }

    body = f"""<div class="wrap">
  <a class="back" href="{prefix}index.html#apps">← アプリ一覧</a>
  <section class="detail-hero">
    <img class="backdrop" src="{prefix}{s['icon']}" alt="" aria-hidden="true">
    <div class="detail-head">
      <img class="detail-icon" src="{prefix}{s['icon']}" alt="{e(app['name'])} のアイコン" width="128" height="128">
      <div>
        <h1>{e(app['name'])}</h1>
        <p class="meta">{e(app['category'])} · {e(support)}</p>
        <p class="lead">{e(app['tagline'])}</p>
      </div>
    </div>
    {store_buttons(app, s)}
  </section>
</div>

<section class="section" aria-label="スクリーンショット">
  <div class="wrap">
    <div class="shots">
{shots}
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap detail-body">
    <article class="prose">
{format_description(desc_src)}
    </article>
    <dl class="info">{info}</dl>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <h2 class="h-sub">ほかのアプリ</h2>
    <div class="app-grid">
{other_cards}
    </div>
  </div>
</section>"""
    html = page(
        title=f"{app['name']} — {app['tagline']} | tiritara.dev",
        description=f"{app['name']}：{app['tagline']}。{support} 対応。",
        prefix=prefix,
        body=body,
        canonical=f"apps/{slug}/",
        og_image=s["icon"],
        extra_head=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>',
    )
    out = ROOT / "apps" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def build_web(site, projects):
    slug = site["slug"]
    prefix = "../../"
    if site.get("url"):
        cta = f'<div class="store-buttons"><a class="web-cta" href="{e(site["url"])}" target="_blank" rel="noopener">{ICON_GLOBE.replace("<svg", "<svg width=20 height=20")} サイトを開く ↗</a></div>'
    else:
        cta = (
            f'<div class="store-buttons"><a class="web-cta" href="mailto:{CONTACT}?subject={e(site["name"])}%20について">導入について問い合わせる</a></div>'
            f'<p class="store-note">{e(site.get("note", ""))}</p>'
        )
    features = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in site["features"])
    rows = [("種類", "Web サービス"), ("技術", e(" / ".join(site["stack"])))]
    if site.get("url"):
        host = re.sub(r"^https?://|/$", "", site["url"])
        rows.append(("URL", f'<a href="{e(site["url"])}" target="_blank" rel="noopener">{e(host)}</a>'))
    rows.append(("開発者", "tiritara.dev"))
    info = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
    others = [w for w in projects["web"] if w["slug"] != slug]
    other_cards = "\n".join(
        f"""<a class="web-card" href="{prefix}web/{w['slug']}/"><div class="web-visual">{web_visual(w, prefix)}</div>
<div class="web-body"><h3>{e(w['name'])}</h3><p>{e(w['tagline'])}</p></div></a>"""
        for w in others
    )

    body = f"""<div class="wrap">
  <a class="back" href="{prefix}index.html#web">← Web サービス一覧</a>
  <section class="detail-hero">
    <div class="detail-head">
      <div>
        <p class="eyebrow">Web service</p>
        <h1>{e(site['name'])}</h1>
        <p class="lead">{e(site['tagline'])}</p>
      </div>
    </div>
    {cta}
  </section>
</div>

<section class="section">
  <div class="wrap">
    <div class="web-card web-showcase"><div class="web-visual">{web_visual(site, prefix)}</div></div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap detail-body">
    <article class="prose">
      <p>{e(site['summary'])}</p>
      <h3>主な機能</h3>
      <ul class="features">{features}</ul>
    </article>
    <dl class="info">{info}</dl>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <h2 class="h-sub">ほかの Web サービス</h2>
    <div class="web-grid">
{other_cards}
    </div>
  </div>
</section>"""
    html = page(
        title=f"{site['name']} — {site['tagline']} | tiritara.dev",
        description=site["summary"],
        prefix=prefix,
        body=body,
        canonical=f"web/{slug}/",
        og_image=site.get("image") or "tiritara_logo_t.png",
    )
    out = ROOT / "web" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def build_sitemap(projects):
    urls = [""] + [f"apps/{a['slug']}/" for a in projects["apps"]] + [f"web/{w['slug']}/" for w in projects["web"]]
    today = date.today().isoformat()
    body = "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n",
        encoding="utf-8",
    )


def main():
    projects = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    store = json.loads((ROOT / "data/store.json").read_text(encoding="utf-8"))
    build_index(projects, store)
    for app in projects["apps"]:
        build_app(app, projects, store)
    for site in projects["web"]:
        build_web(site, projects)
    build_sitemap(projects)
    print("built", 1 + len(projects["apps"]) + len(projects["web"]), "pages")


if __name__ == "__main__":
    main()
