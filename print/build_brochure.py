#!/usr/bin/env python3
"""A4 三つ折りパンフレット（巻き三つ折り・両面）を生成する。

data/projects.json と data/store.json を読み、print/brochure.html を作って
Chrome で print/tiritara-brochure.pdf に書き出す。
QR コードの生成に segno が必要: pip install segno
使い方: python3 print/build_brochure.py
"""
import json
import random
import subprocess
from datetime import date
from html import escape
from pathlib import Path

import segno

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SITE = "https://tiritara-dev.github.io/"
PLAY_DEV = "https://play.google.com/store/apps/dev?id=5924475083153244319"
IOS_DEV = "https://apps.apple.com/jp/developer/id6800308304"
CONTACT = "tiritara.dev@gmail.com"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 内側の右パネル「おすすめ」に載せるアプリ（Android・iOS 両対応のもの）
FEATURED = ["dazen", "train-alarm", "kattalyst"]


def e(s):
    return escape(str(s), quote=True)


def qr_svg(url, dark="#0d1222"):
    q = segno.make(url, error="m")
    svg = q.svg_inline(scale=1, border=2, dark=dark, light="#ffffff", omitsize=True)
    return svg.replace("<svg ", '<svg class="qr" preserveAspectRatio="xMidYMid meet" ', 1)


CLOUD_W, CLOUD_H, LOGO = 74, 104, 30  # 表紙のアイコン雲の領域とロゴの大きさ（mm）


def cloud_layout(n):
    """表紙のアイコンを、ロゴにも互いにも重ならない位置へ散らす（配置が見つかるシードを順に試す）。"""
    for seed in range(500):
        layout = _try_cloud(n, seed)
        if layout:
            return layout
    raise SystemExit("cloud layout failed")


def _try_cloud(n, seed):
    rnd = random.Random(seed)
    sizes = [14, 11, 12, 10, 13, 11, 14, 10, 12, 11, 13, 10, 12, 11, 10, 13, 11]
    lx0, ly0 = (CLOUD_W - LOGO) / 2 - 3, (CLOUD_H - LOGO) / 2 - 3
    lx1, ly1 = lx0 + LOGO + 6, ly0 + LOGO + 6
    placed = []
    for i in range(n):
        w = sizes[i % len(sizes)]
        r = w * 0.6  # 傾けても収まる半径
        for _ in range(3000):
            cx = rnd.uniform(r, CLOUD_W - r)
            cy = rnd.uniform(r, CLOUD_H - r)
            if lx0 - r < cx < lx1 + r and ly0 - r < cy < ly1 + r:
                continue
            if all((cx - px) ** 2 + (cy - py) ** 2 > (r + pr + 1.2) ** 2 for px, py, pr, _ in placed):
                break
        else:
            return None
        placed.append((cx, cy, r, w))
    return [(cx - w / 2, cy - w / 2, w, rnd.choice([-9, -6, -4, 4, 6, 9])) for cx, cy, _, w in placed]


def platforms(app):
    out = []
    if app.get("play"):
        out.append('<span class="pf">Android</span>')
    if app.get("ios"):
        out.append('<span class="pf">iOS</span>')
    return "".join(out)


def app_row(app, store):
    s = store[app["slug"]]
    return f"""<li class="app">
  <img src="../{s['icon']}" alt="">
  <div><p class="name">{e(app['name'])}{platforms(app)}</p><p class="tag">{e(app['tagline'])}</p></div>
</li>"""


def main():
    projects = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    store = json.loads((ROOT / "data/store.json").read_text(encoding="utf-8"))
    apps = projects["apps"]
    by_slug = {a["slug"]: a for a in apps}
    featured = [by_slug[s] for s in FEATURED]
    life = [a for a in apps if a["genre"] == "life" and a["slug"] not in FEATURED]
    games = [a for a in apps if a["genre"] == "game"]
    n_android = sum(1 for a in apps if a.get("play"))
    n_ios = sum(1 for a in apps if a.get("ios"))

    # 表紙：ロゴのまわりにアイコンを浮かべる（サイトのスマホ版と同じ雰囲気）
    cloud = "\n".join(
        f'<img class="float" src="../{store[a["slug"]]["icon"]}" alt="" '
        f'style="left:{x:.1f}mm;top:{y:.1f}mm;width:{w}mm;height:{w}mm;transform:rotate({r}deg)">'
        for a, (x, y, w, r) in zip(apps, cloud_layout(len(apps)))
    )

    feat_html = "\n".join(
        f"""<div class="feat">
  <div class="feat-shots">{''.join(f'<img src="../{p}" alt="">' for p in store[a['slug']]['screenshots'][:2])}</div>
  <div class="feat-body">
    <div class="feat-head"><img class="ficon" src="../{store[a['slug']]['icon']}" alt="">
      <div><p class="name">{e(a['name'])}</p><p class="pfs">{platforms(a)}</p></div></div>
    <p class="tag">{e(a['tagline'])}</p>
    <div class="feat-qr">{qr_svg(SITE + 'apps/' + a['slug'] + '/')}<span>詳細・<br>ダウンロード</span></div>
  </div>
</div>"""
        for a in featured
    )

    web_html = "\n".join(
        f"""<li class="web"><p class="name">{e(w['name'])}</p><p class="tag">{e(w['tagline'])}</p>
<p class="url">{e(w['url'].replace('https://', '').rstrip('/')) if w.get('url') else '導入のご相談を承ります'}</p></li>"""
        for w in projects["web"]
    )

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>tiritara.dev パンフレット</title>
<style>
@page {{ size: 297mm 210mm; margin: 0; }}
:root {{
  --ink: #0d1222; --muted: #4f5a72; --faint: #8a93a8; --line: #e3e7f0;
  --accent: #2f6fe4; --accent-2: #7b4fe0; --navy: #0a0e1a; --soft: #f4f6fb;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{
  font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
  color: var(--ink); font-size: 8.4pt; line-height: 1.6;
}}
.sheet {{
  position: relative; width: 297mm; height: 210mm; overflow: hidden;
  display: grid; break-after: page; background: #fff;
}}
.sheet:last-child {{ break-after: auto; }}
.outside {{ grid-template-columns: 97mm 100mm 100mm; }}
.inside {{ grid-template-columns: 100mm 100mm 97mm; }}
.panel {{ position: relative; padding: 12mm 9mm 11mm; display: flex; flex-direction: column; }}
.en {{ font-family: "Avenir Next", "Helvetica Neue", sans-serif; }}

/* 折り位置のトンボ（上下の端に小さく） */
.fold {{ position: absolute; top: 0; bottom: 0; width: 0; }}
.fold::before, .fold::after {{ content: ""; position: absolute; left: -0.15mm; width: 0.3mm; height: 4mm; background: #c9cfdc; }}
.fold::before {{ top: 0; }} .fold::after {{ bottom: 0; }}

.eyebrow {{ font-family: "Avenir Next", sans-serif; font-weight: 700; font-size: 6.6pt; letter-spacing: .28em; color: var(--accent); text-transform: uppercase; }}
h2 {{ font-size: 14pt; font-weight: 700; letter-spacing: .02em; margin: 1.2mm 0 1.5mm; }}
.lead {{ color: var(--muted); font-size: 7.8pt; margin-bottom: 4mm; }}
.rule {{ height: 0.9mm; width: 14mm; border-radius: 1mm; background: linear-gradient(90deg, var(--accent), var(--accent-2)); margin: 2.5mm 0 3mm; }}

/* ---- 表紙 ---- */
.cover {{ padding: 6mm 6mm 6mm 6mm; }}
.cover-card {{
  position: relative; flex: 1; border-radius: 5mm; overflow: hidden; color: #fff;
  background:
    radial-gradient(70% 45% at 15% 5%, rgba(118,168,255,.35), transparent 70%),
    radial-gradient(60% 40% at 95% 30%, rgba(162,107,255,.30), transparent 70%),
    var(--navy);
  display: flex; flex-direction: column; align-items: center; padding: 9mm 7mm 8mm;
}}
.cloud {{ position: relative; width: {CLOUD_W}mm; height: {CLOUD_H}mm; }}
.cloud .float {{ position: absolute; border-radius: 24%; box-shadow: 0 1.5mm 3mm rgba(0,0,0,.45); border: .2mm solid rgba(255,255,255,.12); }}
.cloud .logo-box {{
  position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  width: {LOGO}mm; height: {LOGO}mm; border-radius: 7mm; background: #fff; display: grid; place-items: center;
  box-shadow: 0 0 9mm rgba(118,168,255,.55);
}}
/* ロゴ画像の下の文字は表紙の見出しと重複するので、マーク部分だけを切り出す */
.cloud .logo-box .mark {{ width: 24mm; height: 17mm; background: url(../tiritara_logo_t.png) no-repeat -3.5mm -0.9mm / 32.2mm auto; }}
.cover h1 {{ font-family: "Avenir Next", sans-serif; font-weight: 800; font-size: 25pt; letter-spacing: -.01em; margin-top: 5mm; }}
.cover .catch {{
  font-family: "Avenir Next", sans-serif; font-weight: 700; font-size: 12pt; line-height: 1.25; text-align: center; margin-top: 2mm;
  background: linear-gradient(100deg, #fff 15%, #8fb8ff 55%, #b48cff 95%); -webkit-background-clip: text; color: transparent;
}}
.cover .sub {{ margin-top: auto; text-align: center; font-size: 8pt; color: #c7cee3; line-height: 1.75; }}
.cover .sub b {{ color: #fff; font-weight: 600; }}

/* ---- 裏表紙 ---- */
.back {{ align-items: center; text-align: center; }}
.back .big-qr {{ width: 46mm; height: 46mm; margin: 5mm 0 3mm; padding: 2mm; border-radius: 3mm; border: .3mm solid var(--line); }}
.back .big-qr .qr {{ width: 100%; height: 100%; display: block; }}
.back .url {{ font-family: "Avenir Next", sans-serif; font-weight: 700; font-size: 11.5pt; letter-spacing: .01em; }}
.back .hint {{ color: var(--muted); font-size: 7.4pt; margin-top: 1mm; }}
.stores {{ display: flex; gap: 6mm; margin-top: 8mm; }}
.store {{ display: flex; flex-direction: column; align-items: center; gap: 1.2mm; font-size: 7pt; color: var(--muted); }}
.store .qr {{ width: 20mm; height: 20mm; }}
.store b {{ color: var(--ink); font-size: 7.6pt; }}
.contact {{ margin-top: auto; width: 100%; padding-top: 4mm; border-top: .3mm solid var(--line); font-size: 7.6pt; color: var(--muted); }}
.contact b {{ display: block; color: var(--ink); font-size: 9pt; font-family: "Avenir Next", sans-serif; }}

/* ---- 折り込み面（about） ---- */
.about p.body {{ font-size: 8.2pt; line-height: 1.9; color: var(--muted); }}
.stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2.5mm; margin: 5mm 0; }}
.stat {{ background: var(--soft); border-radius: 2.5mm; padding: 3mm 3.5mm; }}
.stat b {{ display: block; font-family: "Avenir Next", sans-serif; font-weight: 700; font-size: 17pt; line-height: 1.1;
  background: linear-gradient(100deg, var(--accent), var(--accent-2)); -webkit-background-clip: text; color: transparent; }}
.stat span {{ font-size: 7pt; color: var(--muted); }}
.points {{ list-style: none; display: grid; gap: 3mm; }}
.points li {{ padding-left: 4.5mm; position: relative; font-size: 7.8pt; color: var(--muted); }}
.points li::before {{ content: ""; position: absolute; left: 0; top: 1.6mm; width: 2mm; height: 2mm; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-2)); }}
.points b {{ display: block; color: var(--ink); font-size: 8.6pt; }}

/* ---- アプリ一覧 ---- */
.list {{ list-style: none; display: grid; gap: 2.6mm; }}
.list.roomy {{ gap: 5.2mm; }}
.app {{ display: flex; gap: 3mm; align-items: center; }}
.app img {{ width: 11.5mm; height: 11.5mm; border-radius: 2.8mm; border: .2mm solid var(--line); flex: none; }}
.name {{ font-weight: 700; font-size: 8.6pt; line-height: 1.35; display: flex; align-items: center; flex-wrap: wrap; gap: 1mm; }}
.tag {{ font-size: 7.1pt; color: var(--muted); line-height: 1.5; }}
.pf {{ font-family: "Avenir Next", sans-serif; font-weight: 600; font-size: 5.6pt; letter-spacing: .02em; color: var(--accent);
  border: .2mm solid #c8d6f6; border-radius: 1mm; padding: 0 1mm; line-height: 1.6; }}
.section-gap {{ margin-top: 6mm; }}
.webs {{ list-style: none; display: grid; gap: 2.5mm; }}
.web {{ background: var(--soft); border-radius: 2.5mm; padding: 2.8mm 3.5mm; }}
.web .url {{ font-family: "Avenir Next", sans-serif; font-size: 6.8pt; color: var(--accent); margin-top: .5mm; }}

/* ---- おすすめ ---- */
.feats {{ display: grid; gap: 3.5mm; }}
.feat {{ display: grid; grid-template-columns: 30mm 1fr; gap: 3mm; padding-bottom: 3.5mm; border-bottom: .3mm solid var(--line); }}
.feat:last-child {{ border-bottom: 0; padding-bottom: 0; }}
.feat-shots {{ display: flex; gap: 1.2mm; }}
.feat-shots img {{ width: 14.4mm; height: 30mm; object-fit: cover; border-radius: 1.6mm; border: .2mm solid var(--line); }}
.feat-head {{ display: flex; gap: 2mm; align-items: center; margin-bottom: 1mm; }}
.ficon {{ width: 9mm; height: 9mm; border-radius: 2.2mm; border: .2mm solid var(--line); }}
.pfs {{ display: flex; gap: 1mm; margin-top: .3mm; }}
.feat-qr {{ display: flex; align-items: center; gap: 2mm; margin-top: 1.5mm; font-size: 6.4pt; color: var(--muted); line-height: 1.35; }}
.feat-qr .qr {{ width: 13mm; height: 13mm; flex: none; }}
.foot {{ margin-top: auto; font-size: 6.6pt; color: var(--faint); }}
</style>
</head>
<body>

<!-- 外側（1ページ目）: 折り込み面 | 裏表紙 | 表紙 -->
<section class="sheet outside">
  <div class="panel about">
    <p class="eyebrow">About</p>
    <h2>tiritara.dev について</h2>
    <div class="rule"></div>
    <p class="body">tiritara.dev は、Android・iOS アプリと Web サービスを個人で企画・開発しています。毎日のちょっとした不便をなくすツールから、気軽に遊べるゲーム、お店や会社で使える業務システムまで。使う人がちょっと笑顔になれるものづくりを目指しています。</p>
    <div class="stats">
      <div class="stat"><b>{len(apps)}</b><span>公開中のアプリ</span></div>
      <div class="stat"><b>{len(projects['web'])}</b><span>Web サービス</span></div>
      <div class="stat"><b>{n_android}</b><span>Android</span></div>
      <div class="stat"><b>{n_ios}</b><span>iOS</span></div>
    </div>
    <ul class="points">
      <li><b>暮らしを少し便利に</b>買い物リスト、乗り過ごし防止、六曜カレンダー、ガーデニング記録など。</li>
      <li><b>すきま時間に遊べるゲーム</b>アーケード、ボードゲーム、カードゲーム、脳トレパズル。</li>
      <li><b>Web サービス・業務システム</b>オンライン絵馬や、QR コードで打刻する勤怠システム。</li>
    </ul>
  </div>

  <div class="panel back">
    <p class="eyebrow">Website</p>
    <h2>すべてのアプリはこちら</h2>
    <div class="big-qr">{qr_svg(SITE)}</div>
    <p class="url en">tiritara-dev.github.io</p>
    <p class="hint">スマホのカメラで読み取ると、アプリの紹介ページが開きます</p>
    <div class="stores">
      <div class="store">{qr_svg(PLAY_DEV)}<b>Google Play</b>Android 版</div>
      <div class="store">{qr_svg(IOS_DEV)}<b>App Store</b>iPhone・iPad 版</div>
    </div>
    <div class="contact"><b>{CONTACT}</b>ご感想・ご要望・お仕事のご相談はお気軽にどうぞ</div>
  </div>

  <div class="panel cover">
    <div class="cover-card">
      <div class="cloud">
        {cloud}
        <div class="logo-box"><div class="mark"></div></div>
      </div>
      <h1 class="en">tiritara.dev</h1>
      <p class="catch">Code smarter.<br>Live smiler.</p>
      <p class="sub"><b>Android・iOS アプリと Web サービス</b><br>個人開発のアプリ紹介</p>
    </div>
  </div>
  <span class="fold" style="left:97mm"></span><span class="fold" style="left:197mm"></span>
</section>

<!-- 内側（2ページ目）: 暮らし・ツール | ゲーム・Web | おすすめ -->
<section class="sheet inside">
  <div class="panel">
    <p class="eyebrow">Apps</p>
    <h2>暮らし・ツールのアプリ</h2>
    <div class="rule"></div>
    <ul class="list roomy">
{''.join(app_row(a, store) for a in life)}
    </ul>
  </div>

  <div class="panel">
    <p class="eyebrow">Games</p>
    <h2>ゲーム</h2>
    <div class="rule"></div>
    <ul class="list">
{''.join(app_row(a, store) for a in games)}
    </ul>
    <div class="section-gap"></div>
    <p class="eyebrow">Web</p>
    <h2>Web サービス</h2>
    <div class="rule"></div>
    <ul class="webs">
{web_html}
    </ul>
  </div>

  <div class="panel">
    <p class="eyebrow">Pick up</p>
    <h2>おすすめアプリ</h2>
    <div class="rule"></div>
    <div class="feats">
{feat_html}
    </div>
    <p class="foot">掲載内容は {date.today().year}年{date.today().month}月 時点のものです。</p>
  </div>
  <span class="fold" style="left:100mm"></span><span class="fold" style="left:200mm"></span>
</section>

</body>
</html>
"""
    out_html = HERE / "brochure.html"
    out_html.write_text(html, encoding="utf-8")
    out_pdf = HERE / "tiritara-brochure.pdf"
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
         f"--print-to-pdf={out_pdf}", out_html.as_uri()],
        check=True, capture_output=True,
    )
    print("wrote", out_pdf.relative_to(ROOT))


if __name__ == "__main__":
    main()
