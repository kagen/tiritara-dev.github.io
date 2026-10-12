#!/usr/bin/env python3
"""Google Play / App Store から各アプリの掲載情報と画像を取得する。

data/projects.json の apps を読み、data/store.json と assets/apps/<slug>/ を更新する。
使い方: python3 tools/fetch_store_data.py
"""
import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_SHOTS = 6
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def save(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(get(url))
    return path.relative_to(ROOT).as_posix()


def play_listing(pkg):
    s = get(f"https://play.google.com/store/apps/details?id={pkg}&hl=ja&gl=JP").decode("utf-8")

    def meta(prop):
        m = re.search(r'<meta [^>]*property="%s"[^>]*content="([^"]*)"' % prop, s)
        return html.unescape(m.group(1)) if m else ""

    icon = re.search(r'<img src="(https://play-lh[^"=]+)=w240-h480[^"]*"[^>]*alt="アイコン画像"', s)
    desc = re.search(r'data-g-id="description"[^>]*>(.*?)</div>', s, re.S)
    full = ""
    if desc:
        full = re.sub(r"<br\s*/?>", "\n", desc.group(1))
        full = html.unescape(re.sub(r"<[^>]+>", "", full))
    shots = re.findall(r'<img src="(https://play-lh[^"=]+)=w526-h296[^"]*"[^>]*alt="スクリーンショット画像"', s)
    updated = re.search(r'"146":\[\["([0-9/]+)"', s)
    version = re.search(r'"141":\[\[\["([^"]+)"\]\]', s)
    return {
        "title": meta("og:title").replace(" - Google Play のアプリ", ""),
        "short": meta("og:description"),
        "description": full.strip(),
        "icon": icon.group(1) if icon else "",
        "screenshots": list(dict.fromkeys(shots)),
        "updated": updated.group(1) if updated else "",
        "version": version.group(1) if version else "",
        "url": f"https://play.google.com/store/apps/details?id={pkg}",
    }


def ios_listing(track_id):
    d = json.loads(get(f"https://itunes.apple.com/lookup?id={track_id}&country=jp"))
    r = d["results"][0]
    return {
        "title": r["trackName"],
        "description": r.get("description", "").strip(),
        "icon": r["artworkUrl512"],
        "screenshots": r.get("screenshotUrls", []),
        "version": r.get("version", ""),
        "minimumOsVersion": r.get("minimumOsVersion", ""),
        "url": r["trackViewUrl"].split("?")[0],
    }


def main():
    projects = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    store = {}
    for app in projects["apps"]:
        slug = app["slug"]
        out = ROOT / "assets/apps" / slug
        entry = {}
        print("fetching", slug)
        if app.get("play"):
            entry["play"] = play_listing(app["play"])
        if app.get("ios"):
            entry["ios"] = ios_listing(app["ios"])

        if "play" in entry and entry["play"]["icon"]:
            entry["icon"] = save(entry["play"]["icon"] + "=s256-rw", out / "icon.webp")
        else:
            entry["icon"] = save(entry["ios"]["icon"].replace("512x512bb.jpg", "256x256bb.png"), out / "icon.png")

        # スクリーンショットは Play を優先し、Android 版がなければ iOS 版を使う
        shots = []
        if "play" in entry and entry["play"]["screenshots"]:
            for i, u in enumerate(entry["play"]["screenshots"][:MAX_SHOTS]):
                shots.append(save(u + "=h720-rw", out / f"shot-{i + 1}.webp"))
        elif "ios" in entry:
            for i, u in enumerate(entry["ios"]["screenshots"][:MAX_SHOTS]):
                u = re.sub(r"/\d+x\d+bb\.(png|jpg)$", "/392x696bb.jpg", u)
                shots.append(save(u, out / f"shot-{i + 1}.jpg"))
        entry["screenshots"] = shots
        for k in ("play", "ios"):
            if k in entry:
                entry[k].pop("icon", None)
                entry[k].pop("screenshots", None)
        store[slug] = entry

    (ROOT / "data/store.json").write_text(json.dumps(store, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("wrote data/store.json")


if __name__ == "__main__":
    main()
