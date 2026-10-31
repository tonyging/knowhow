# -*- coding: utf-8 -*-
"""產生服務說明頁、案例頁、sitemap.xml。

用法（在 repo 根目錄）：  py tools/build_pages.py

- 內容來源：tools/pages_content.py（文字）、tools/site_config.py（網址與追蹤碼）
- 樣式：assets/page.css（手寫，不是產生的）
- 輸出：services/<slug>/index.html、work/<slug>/index.html、shop/index.html、sitemap.xml
- 只用標準函式庫。輸出檔可以隨時重跑覆蓋，不要手動修改。
"""
import html
import json
import os
import re
import struct
import sys
from datetime import date
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import pages_content as C  # noqa: E402
import site_config as S  # noqa: E402

SERVICES = {s["slug"]: s for s in C.SERVICES}
WORKS = {w["slug"]: w for w in C.WORKS}

# 這幾個是版面用的輔助資料，不屬於頁面主要文字
SERVICE_TYPE = {
    "booking-system": "線上預約系統開發",
    "website": "形象官網製作",
    "line-official-account": "LINE 官方帳號建置",
    "legacy-upgrade": "舊系統升級",
}
WORK_SHORT = {
    "glimmer-booking": "微光指尖",
    "lanan-coffee": "嵐岸咖啡",
    "knowhow-line-oa": "諾豪的 LINE 官方帳號",
}
WORK_TRACK = {"glimmer-booking": "glimmer", "lanan-coffee": "coffee", "knowhow-line-oa": "line"}
LINK_TRACK = {"看網站": "site", "看店家後台": "admin", "開一間示範店": "live",
              "看後台怎麼改": "backend", "加 LINE 好友看看": "add"}
# 首頁作品屏用的手機版截圖（內容檔的 shots 沒有列，這裡補上；alt 沿用首頁的寫法）
EXTRA_PHONE = {
    "glimmer-booking": ("../../img/work-glimmer-mobile.webp",
                        "微光指尖手機版畫面：美甲作品照片與底部「預約時段」按鈕"),
}
GEN_NOTE = "<!-- 由 tools/build_pages.py 產生，不要手動修改；要改文字請改 tools/pages_content.py 再重跑 -->"

TODAY = date.today().isoformat()
e = lambda t: html.escape(t, quote=True)  # noqa: E731


# ---------- 小工具 ----------
_FAQ_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def faq_plain(a):
    """FAQ 答案內的 [文字](連結) 在 JSON-LD 裡只留文字。"""
    return _FAQ_LINK.sub(lambda m: m.group(1), a)


def faq_html(a):
    """頁面上的 FAQ 答案：[文字](連結) 轉成站內連結，其餘照常跳脫。"""
    out, pos = "", 0
    for m in _FAQ_LINK.finditer(a):
        out += e(a[pos:m.start()]) + f'<a class="pg-u" href="{e(m.group(2))}" data-track="page-faq-link">{e(m.group(1))}</a>'
        pos = m.end()
    return out + e(a[pos:])


def webp_size(path):
    """讀 webp 檔頭取得寬高；失敗回傳 None。"""
    try:
        with open(path, "rb") as f:
            d = f.read(64)
        if d[:4] != b"RIFF" or d[8:12] != b"WEBP":
            return None
        k = d[12:16]
        if k == b"VP8X":
            w = 1 + int.from_bytes(d[24:27], "little")
            h = 1 + int.from_bytes(d[27:30], "little")
            return w, h
        if k == b"VP8 ":
            w, h = struct.unpack("<HH", d[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if k == b"VP8L":
            b = int.from_bytes(d[21:25], "little")
            return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    except OSError:
        pass
    return None


def img_dims(rel, w=None, h=None):
    if w and h:
        return w, h
    p = os.path.normpath(os.path.join(ROOT, rel.replace("../../", "")))
    return webp_size(p) or (1200, 712)


def first_price(s):
    m = re.search(r"NT\$\s*([\d,]+)", s["facts"][0][1])
    return int(m.group(1).replace(",", "")) if m else None


def first_sentence(t):
    i = t.find("。")
    return t if i < 0 else t[: i + 1]


def jsonld(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")


def url_service(slug):
    return f"{S.SITE}/services/{slug}/"


def url_work(slug):
    return f"{S.SITE}/work/{slug}/"


def h1_html(t):
    """h1 可以在內容檔用 <wbr> 指定中文斷點：只放行 <wbr>，其他照樣跳脫。"""
    return e(t).replace("&lt;wbr&gt;", "<wbr>")


def plain(t):
    """給 <title>、JSON-LD、麵包屑等純文字用：拿掉 <wbr>。"""
    return t.replace("<wbr>", "")


# 標題區右側的小插圖：首頁 hero 的母題縮小版（便條沿虛線箭頭飛進表格、格子亮起、最後打勾）。
# 純 CSS 動畫（assets/page.css 的 pg-art 段落）；減少動態時是靜止的完成狀態。裝飾用，不給讀屏。
HERO_ART = """<div class="pg-hero-art" aria-hidden="true">
    <svg class="pg-art" viewBox="0 0 360 220" focusable="false">
      <g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
        <g class="pg-fly pg-f0"><g class="pg-bob" style="--b:0"><g transform="rotate(-9 36 49)"><rect class="pg-d" style="--i:0" pathLength="1" x="12" y="34" width="48" height="30" rx="3"/><path class="pg-d" style="--i:1" pathLength="1" d="M22 46 h22 M22 54 h14"/></g></g></g>
        <g class="pg-fly pg-f1"><g class="pg-bob" style="--b:1"><g transform="rotate(6 91 93)"><rect class="pg-d" style="--i:2" pathLength="1" x="64" y="78" width="54" height="30" rx="3"/><path class="pg-d" style="--i:3" pathLength="1" d="M74 90 h30 M74 98 h18"/></g></g></g>
        <g class="pg-fly pg-f2"><g class="pg-bob" style="--b:2"><g transform="rotate(-4 40 133)"><rect class="pg-d" style="--i:4" pathLength="1" x="18" y="118" width="44" height="30" rx="3"/><path class="pg-d" style="--i:5" pathLength="1" d="M28 130 h20 M28 138 h12"/></g></g></g>
        <g class="pg-fly pg-f3"><g class="pg-bob" style="--b:3"><g transform="rotate(10 97 165)"><rect class="pg-d" style="--i:6" pathLength="1" x="72" y="150" width="50" height="30" rx="3"/><path class="pg-d" style="--i:7" pathLength="1" d="M82 162 h26 M82 170 h14"/></g></g></g>
        <path d="M142 112 H212" stroke-dasharray="2 6"/>
        <path class="pg-d" style="--i:8" pathLength="1" d="M205 105 L213 112 L205 119"/>
        <rect class="pg-d" style="--i:9" pathLength="1" x="238" y="44" width="110" height="128" rx="6"/>
        <path class="pg-d" style="--i:10" pathLength="1" d="M238 78 H348 M238 112 H348 M238 146 H348 M276 44 V172"/>
      </g>
      <g class="pg-g" fill="currentColor">
        <circle class="pg-dot" cx="142" cy="112" r="3.5"/>
        <rect class="pg-c0" x="248" y="54" width="18" height="14" rx="2"/>
        <rect class="pg-c1" x="248" y="88" width="18" height="14" rx="2"/>
        <rect class="pg-c2" x="248" y="122" width="18" height="14" rx="2"/>
        <rect class="pg-c3" x="248" y="156" width="18" height="10" rx="2"/>
        <circle class="pg-cc" cx="344" cy="176" r="13"/>
      </g>
      <path class="pg-tick" pathLength="1" d="M337 176 l5 5 l9 -10" fill="none" stroke="var(--card)" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>"""


def hero(n, en, h1, badge=""):
    b = f'\n    <span class="pg-badge pg-rise">{e(badge)}</span>' if badge else ""
    return (f'<header class="pg-hero">\n  <div class="pg-hero-txt">\n    {label(n, en)}\n'
            f'    <h1 class="pg-h1 pg-rise">{h1_html(h1)}</h1>{b}\n  </div>\n  {HERO_ART}\n</header>')


CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
         '<path d="M8 12.5l2.7 2.7L16 9.5" stroke="var(--green)"/></svg>')


# ---------- 共用區塊 ----------
def head(title, desc, canon, extra_ld):
    return f"""<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0E7A55">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="諾豪資訊 Knowhow">
<meta property="og:locale" content="zh_TW">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{S.SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="諾豪資訊 Knowhow：把專業知識，變成可以直接使用的成品">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{S.SITE}/og.png">
<link rel="icon" href="../../logo.png">
<link rel="stylesheet" href="../../assets/page.css">
<script defer src="https://cloud.umami.is/script.js" data-website-id="{S.UMAMI_ID}" data-domains="{S.UMAMI_DOMAINS}" data-do-not-track="true"></script>
<script type="application/ld+json">
{jsonld(extra_ld)}
</script>
</head>
"""


def topbar():
    return f"""<header class="pg-top">
  <div class="pg-top-in">
    <a class="pg-brand" href="../../"><img src="../../logo.png" width="34" height="34" alt=""><span>諾豪資訊</span></a>
    <a class="pg-pill" href="{C.LINE_URL}" target="_blank" rel="noopener" data-track="page-line-cta">LINE 洽談</a>
  </div>
</header>"""


def crumb(second_name, second_href, here):
    return f"""<nav class="pg-crumb pg-rise" aria-label="麵包屑">
    <a href="../../">首頁</a><span aria-hidden="true">/</span><a href="../../{second_href}">{second_name}</a><span aria-hidden="true">/</span><span aria-current="page">{e(here)}</span>
  </nav>"""


def label(n, text):
    return f'<p class="pg-label"><b>{n:02d}</b><i></i>{e(text)}</p>'


def cta_card(where):
    return f"""<section class="pg-cta pg-reveal" aria-labelledby="pg-cta-h">
    <div>
      <h2 id="pg-cta-h">想聊聊你的狀況？</h2>
      <p>LINE ID：{C.LINE_ID}・平日一個工作天內回覆</p>
    </div>
    <a class="pg-btn pg-btn-white" href="{C.LINE_URL}" target="_blank" rel="noopener" data-track="page-line-cta-{where}">LINE 洽談</a>
  </section>"""


def footer():
    sv = "".join(f'<li><a href="../../services/{s["slug"]}/">{e(s["short"])}</a></li>' for s in C.SERVICES)
    sv += '<li><a href="../../shop/">線上購買</a></li>'
    wk = "".join(f'<li><a href="../../work/{w["slug"]}/">{e(WORK_SHORT[w["slug"]])}</a></li>' for w in C.WORKS)
    return f"""<footer class="pg-foot">
  <div class="pg-wrap pg-foot-in">
    <div class="pg-foot-brand">
      <a class="pg-brand" href="../../"><img src="../../logo.png" width="34" height="34" alt=""><span>諾豪資訊</span></a>
      <p>把專業知識，變成可以直接使用的成品。</p>
      <p>負責人：阿金，全端工程師。參與過全國性公共服務系統開發，現在專做小店的網站、預約系統與 LINE 官方帳號。</p>
      <p><a class="pg-u" href="../../#refund">付款方式與退款政策</a></p>
    </div>
    <nav class="pg-foot-col" aria-label="服務說明"><h2>服務說明</h2><ul>{sv}</ul></nav>
    <nav class="pg-foot-col" aria-label="案例"><h2>案例</h2><ul>{wk}</ul></nav>
  </div>
  <div class="pg-wrap pg-foot-bar"><a class="pg-u" href="../../">回首頁</a><span>© 諾豪資訊</span><span class="pg-tg"><i></i>SMALL &amp; FAST</span></div>
</footer>"""


def page_shell(h, body):
    return f"{h}<body>\n{GEN_NOTE}\n{topbar()}\n<main class=\"pg-wrap pg-main\" id=\"main\">\n{body}\n</main>\n{footer()}\n</body>\n</html>\n"


def crumb_ld(second_name, second_url, here_name, here_url):
    return {
        "@type": "BreadcrumbList",
        "@id": here_url + "#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首頁", "item": S.SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": second_name, "item": second_url},
            {"@type": "ListItem", "position": 3, "name": here_name, "item": here_url},
        ],
    }


def webpage_ld(url, name, desc):
    return {
        "@type": "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": name,
        "description": desc,
        "inLanguage": "zh-Hant-TW",
        "isPartOf": {"@id": S.SITE + "/#website"},
        "breadcrumb": {"@id": url + "#breadcrumb"},
    }


# ---------- 服務頁 ----------
def build_service(s):
    slug = s["slug"]
    url = url_service(slug)
    n = 1
    parts = []
    parts.append(crumb("服務與價格", "#work", s["short"]))
    parts.append(hero(n, s["en"], s["h1"]))
    facts = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in s["facts"])
    parts.append(f"""<section class="pg-card pg-answer pg-rise" aria-label="簡短回答">
    <p class="pg-lead">{e(s["answer"])}</p>
    <dl class="pg-facts">{facts}</dl>
  </section>""")

    n += 1
    fit = "".join(f"<li>{CHECK}<span>{e(t)}</span></li>" for t in s["fit"])
    parts.append(f'<section class="pg-sec pg-reveal">\n  {label(n, "FIT")}\n  <h2 class="pg-h2">適合你，如果…</h2>\n  <ul class="pg-fit">{fit}</ul>\n</section>')

    n += 1
    spans = [4, 4, 4, 6, 6] if len(s["includes"]) == 5 else [6] * len(s["includes"])
    inc = "".join(
        f'<article class="pg-tile" style="--sp:{sp}"><h3>{e(t)}</h3><p>{e(d)}</p></article>'
        for (t, d), sp in zip(s["includes"], spans))
    parts.append(f'<section class="pg-sec pg-reveal">\n  {label(n, "INCLUDES")}\n  <h2 class="pg-h2">包含什麼</h2>\n  <div class="pg-bento">{inc}</div>\n</section>')

    n += 1
    steps = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in s["steps"])
    parts.append(f'<section class="pg-sec pg-reveal">\n  {label(n, "PROCESS")}\n  <h2 class="pg-h2">合作流程</h2>\n  <ol class="pg-steps">{steps}</ol>\n</section>')
    # 手機中段的次要行動（只在 ≤640px 顯示；全頁唯一的綠底卡仍是最下面的 pg-cta）
    parts.append(f'<p class="pg-mid"><a class="pg-btn pg-btn-ghost" href="{C.LINE_URL}" target="_blank" rel="noopener" data-track="page-mid-line">LINE 問問看</a></p>')

    if s["work"]:
        w = WORKS[s["work"]]
        n += 1
        if w["shots"]:
            src, sw0, sh0, alt = w["shots"][0]
            ww, hh = img_dims(src, sw0, sh0)
            left = f'<div class="pg-case-fig"><a class="pg-case-img" href="{src}" target="_blank" rel="noopener" data-track="page-case-img"><img src="{src}" width="{ww}" height="{hh}" loading="lazy" alt="{e(alt)}">{ZOOM_ICO}</a>{zoom_hint(src)}</div>'
        else:
            left = LINE_MOCK.replace("pg-card pg-mock", "pg-card pg-mock pg-mock-sm")
        parts.append(f"""<section class="pg-sec pg-reveal">
  {label(n, "CASE")}
  <h2 class="pg-h2">對應的作品</h2>
  <article class="pg-card pg-case">
    {left}
    <div class="pg-case-body">
      <span class="pg-badge">{e(w["kind"])}</span>
      <h3>{e(w["name"])}</h3>
      <p>{e(first_sentence(w["answer"]))}</p>
      <a class="pg-u pg-strong" href="../../work/{w["slug"]}/" data-track="page-case-link">看案例 →</a>
    </div>
  </article>
</section>""")

    n += 1
    faq = "".join(
        f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{faq_html(a)}</p></details>'
        for i, (q, a) in enumerate(s["faq"]))
    parts.append(f'<section class="pg-sec pg-reveal">\n  {label(n, "FAQ")}\n  <h2 class="pg-h2">常見問題</h2>\n  <div class="pg-faq">{faq}</div>\n</section>')

    parts.append(cta_card("bottom"))

    others = "".join(
        f'<a class="pg-card pg-link" href="../{o["slug"]}/" data-track="page-other-service"><span class="pg-mono">{e(o["en"])}</span><b>{e(o["short"])}</b><em>{e(o.get("card_price", o["facts"][0][1]))}</em></a>'
        for o in C.SERVICES if o["slug"] != slug)
    n += 1
    parts.append(f'<section class="pg-sec pg-reveal">\n  {label(n, "MORE SERVICES")}\n  <h2 class="pg-h2">其他服務</h2>\n  <div class="pg-links">{others}</div>\n</section>')

    price = first_price(s)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            crumb_ld("服務與價格", S.SITE + "/#work", s["short"], url),
            webpage_ld(url, s["title"], s["description"]),
            {
                "@type": "Service",
                "@id": url + "#service",
                "name": s["short"],
                "description": s["description"],
                "serviceType": SERVICE_TYPE[slug],
                "provider": {"@id": S.SITE + "/#org"},
                "areaServed": {"@type": "Country", "name": "TW"},
                "url": url,
                "offers": {
                    "@type": "Offer",
                    "priceSpecification": {"@type": "PriceSpecification", "minPrice": price, "priceCurrency": "TWD"},
                } if price else None,
            },
            {
                "@type": "FAQPage",
                "@id": url + "#faq",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": faq_plain(a)}}
                    for q, a in s["faq"]
                ],
            },
        ],
    }
    ld["@graph"][2] = {k: v for k, v in ld["@graph"][2].items() if v is not None}
    out = page_shell(head(s["title"], s["description"], url, ld), "\n".join(parts))
    write(os.path.join("services", slug, "index.html"), out)


# ---------- 案例頁 ----------
LINE_MOCK = """<figure class="pg-card pg-mock" role="img" aria-label="LINE 官方帳號畫面示意：歡迎訊息、作品卡片、我要報價，以及四格圖文選單">
    <div class="pg-chat" aria-hidden="true">
      <div class="pg-chat-bar"><i></i><span class="pg-mono">LINE OFFICIAL ACCOUNT</span></div>
      <div class="pg-chat-body">
        <div class="pg-bub pg-bub-bot"><span class="pg-mono">歡迎訊息</span><u></u><u></u></div>
        <div class="pg-cards"><div><span class="pg-mono">作品與案例</span><u></u></div><div><span class="pg-mono">作品案例</span><u></u></div><div class="pg-peek"></div></div>
        <div class="pg-bub pg-bub-me">我要報價</div>
        <div class="pg-bub pg-bub-bot"><span class="pg-mono">回答三個問題，摘要推播給負責人</span><u></u></div>
      </div>
      <div class="pg-menu4">
        <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3.5" width="16" height="17" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>服務項目</div>
        <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="14" rx="2"/><path d="M3.5 15l5-4 4 3 3-2 5 4"/></svg>作品與案例</div>
        <div class="pg-menu-hot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-6l-5 4v-4H6a2 2 0 0 1-2-2z"/></svg>我要報價</div>
        <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 5h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 14l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 6a1 1 0 0 1 1-1z"/></svg>聯絡方式</div>
      </div>
    </div>
  </figure>"""


# 桌機：圖片右下角的放大鏡小提示（hover／焦點時出現）。手機：圖下方一顆次要按鈕「看大圖」。
# 按鈕和圖片連到同一張大圖；圖片連結本身就有 alt 可以讀，按鈕對讀屏隱藏、不進 Tab 順序，避免重複。
ZOOM_ICO = ('<span class="pg-zoom-ico" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="10.5" cy="10.5" r="6"/>'
            '<path d="M15 15l5 5M10.5 8v5M8 10.5h5"/></svg></span>')


def zoom_hint(src):
    return (f'<a class="pg-zoom-hint" href="{src}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">'
            f'{ZOOM_ICO.replace("pg-zoom-ico", "pg-zoom-hint-ico")}看大圖</a>')


def zoom_img(src, w, h, alt):
    return f'<a class="pg-zoom" href="{src}" target="_blank" rel="noopener"><img src="{src}" width="{w}" height="{h}" loading="lazy" alt="{e(alt)}">{ZOOM_ICO}</a>{zoom_hint(src)}'


def shots_block(w):
    shots = w["shots"]
    if not shots:
        return LINE_MOCK
    desktop = [s for s in shots if not (s[2] and s[1] and s[2] > s[1])]
    phones = [s for s in shots if (s[2] and s[1] and s[2] > s[1])]
    phone = None
    if phones:
        phone = (phones[0][0], phones[0][1], phones[0][2], phones[0][3])
    elif w["slug"] in EXTRA_PHONE:
        p, alt = EXTRA_PHONE[w["slug"]]
        d = img_dims(p)
        phone = (p, d[0], d[1], alt)
    if not desktop:  # 全是手機直式截圖（LINE 案例）：三張並排，各附說明
        items = ""
        for src, sw, sh, alt in phones:
            rw, rh = img_dims(src, sw, sh)
            items += f'<figure class="pg-shot pg-shot-tall">{zoom_img(src, rw, rh, alt)}<figcaption>{e(alt.split("：", 1)[-1])}</figcaption></figure>'
        return f'<div class="pg-shots3">{items}</div>'
    main = desktop[0]
    mw, mh = img_dims(main[0], main[1], main[2])
    ph = ""
    if phone:
        pw, phh = img_dims(phone[0], phone[1], phone[2])
        ph = f'<figure class="pg-phone"><img src="{phone[0]}" width="{pw}" height="{phh}" loading="lazy" alt="{e(phone[3])}"></figure>'
    out = f'<div class="pg-fig{" pg-fig-phone" if phone else ""}"><figure class="pg-shot">{zoom_img(main[0], mw, mh, main[3])}</figure>{ph}</div>'
    rest = desktop[1:]
    if rest:
        items = ""
        for src, sw, sh, alt in rest:
            rw, rh = img_dims(src, sw, sh)
            cap = alt.split("：", 1)[-1]
            items += f'<figure class="pg-shot">{zoom_img(src, rw, rh, alt)}<figcaption>{e(cap)}</figcaption></figure>'
        out += f'<div class="pg-shots2">{items}</div>'
    return out


def build_work(w):
    slug = w["slug"]
    url = url_work(slug)
    sv = SERVICES[w["service"]]
    n = 1
    parts = []
    parts.append(crumb("作品範例", "#portfolio", WORK_SHORT[slug]))
    parts.append(hero(n, w["en"], w["h1"], w["kind"]))
    btns = ""
    for i, (name, href) in enumerate(w["links"]):
        cls = "pg-btn-solid" if i == 0 else "pg-btn-ghost"
        sfx = LINK_TRACK.get(name, str(i + 1))
        a = f'<a class="pg-btn {cls}" href="{href}" target="_blank" rel="noopener" data-track="case-{WORK_TRACK[slug]}-{sfx}">{e(name)}</a>'
        note = w.get("link_notes", {}).get(name)
        btns += f'<span class="pg-btn-wrap">{a}<small class="pg-btn-note">{e(note)}</small></span>' if note else a
    parts.append(f'<section class="pg-card pg-answer pg-rise" aria-label="簡短回答">\n    <p class="pg-lead">{e(w["answer"])}</p>\n    <div class="pg-btns">{btns}</div>\n  </section>')
    parts.append(f'<section class="pg-sec pg-reveal" aria-label="畫面">\n  {shots_block(w)}\n</section>')

    n += 1
    parts.append(f'<section class="pg-sec pg-reveal">\n  {label(n, "PROBLEM")}\n  <h2 class="pg-h2">遇到的問題</h2>\n  <p class="pg-text">{e(w["problem"])}</p>\n</section>')
    n += 1
    sol = "".join(f"<li>{CHECK}<span>{e(t)}</span></li>" for t in w["solution"])
    parts.append(f'<section class="pg-sec pg-reveal">\n  {label(n, "SOLUTION")}\n  <h2 class="pg-h2">怎麼做</h2>\n  <ul class="pg-fit pg-sol">{sol}</ul>\n</section>')
    n += 1
    parts.append(f'<section class="pg-sec pg-reveal">\n  {label(n, "RESULT")}\n  <h2 class="pg-h2">{e(w.get("result_title", "結果"))}</h2>\n  <p class="pg-text">{e(w["result"])}</p>\n  <p class="pg-stack">{e(w["stack"])}</p>\n</section>')

    n += 1
    parts.append(f"""<section class="pg-sec pg-reveal">
  {label(n, "SERVICE")}
  <h2 class="pg-h2">對應服務</h2>
  <a class="pg-card pg-link pg-link-wide" href="../../services/{sv["slug"]}/" data-track="case-to-service"><span class="pg-mono">{e(sv["en"])}</span><b>{e(w.get("service_label", sv["short"]))}</b><em>{e(w.get("service_price", sv["facts"][0][1]))}</em><span class="pg-go">看服務說明 →</span></a>
</section>""")

    parts.append(cta_card("bottom"))

    first_link = w["links"][0][1]
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            crumb_ld("作品範例", S.SITE + "/#portfolio", WORK_SHORT[slug], url),
            webpage_ld(url, w["title"], w["description"]),
            {
                "@type": "CreativeWork",
                "@id": url + "#work",
                "name": w["name"],
                "description": w["description"],
                "url": first_link,
                "inLanguage": "zh-Hant-TW",
                "creator": {"@id": S.SITE + "/#org"},
                "about": {"@id": url_service(w["service"]) + "#service"},
                "mainEntityOfPage": {"@id": url + "#webpage"},
            },
        ],
    }
    out = page_shell(head(w["title"], w["description"], url, ld), "\n".join(parts))
    write(os.path.join("work", slug, "index.html"), out)


# ---------- 線上購買頁（/shop/） ----------
SHOP_JS = """<script>
(function(){
  var KEY="nh-shop-cart", root=document.getElementById("pg-shop");
  if(!root) return;
  var add=document.getElementById("pg-add"), full=document.getElementById("pg-cart-full"),
      empty=document.getElementById("pg-cart-empty"), live=document.getElementById("pg-cart-live"),
      rm=document.getElementById("pg-cart-rm"), count=document.getElementById("pg-cart-count"),
      view=document.getElementById("pg-view-cart"), head=document.getElementById("pg-cart-h"),
      rd=document.getElementById("pg-refund-d");
  var inCart=false;
  /* 購物車只存在這個分頁的 sessionStorage（關掉分頁就清空），不收集、不傳送任何資料 */
  try{ inCart=sessionStorage.getItem(KEY)==="1"; }catch(x){}
  function save(){ try{ if(inCart) sessionStorage.setItem(KEY,"1"); else sessionStorage.removeItem(KEY); }catch(x){} }
  function rmo(){ return matchMedia("(prefers-reduced-motion:reduce)").matches; }
  function render(msg){
    full.hidden=!inCart; empty.hidden=inCart; view.hidden=!inCart;
    add.textContent=inCart?"已加入購物車":"加入購物車";
    add.setAttribute("aria-disabled",inCart?"true":"false");
    add.classList.toggle("is-done",inCart);
    count.textContent=inCart?"（1 件）":"（0 件）";
    if(msg) live.textContent=msg;
  }
  add.addEventListener("click",function(){
    if(inCart) return;
    inCart=true; save(); render("已加入購物車，合計 NT$1,500。");
  });
  /* 「查看購物車」：把焦點移到購物車標題並捲到那裡（鍵盤與讀屏使用者也知道購物車在哪） */
  view.addEventListener("click",function(e){
    e.preventDefault();
    head.focus({preventScroll:true});
    try{ head.scrollIntoView({block:"start",behavior:rmo()?"auto":"smooth"}); }catch(x){}
  });
  rm.addEventListener("click",function(){
    inCart=false; save(); render("已從購物車移除，購物車是空的。");
    add.focus();
  });
  /* 退換貨規則：桌機預設展開，手機預設收合（沒有 JS 時維持展開） */
  if(rd&&matchMedia("(max-width:767px)").matches) rd.removeAttribute("open");
  render("");
  /* 成效追蹤：與首頁相同，點擊帶有 data-track 的元素時送出事件；分析腳本未載入時什麼都不會發生 */
  document.addEventListener("click",function(e){
    var el=e.target.closest&&e.target.closest("[data-track]"); if(!el) return;
    try{ if(window.umami&&typeof window.umami.track==="function") window.umami.track(el.getAttribute("data-track")); }catch(x){}
  },true);
})();
</script>"""

NO_ICO = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
          '<path d="M9 9l6 6M15 9l-6 6" stroke="var(--muted)"/></svg>')


def build_shop():
    sh = C.SHOP
    url = f"{S.SITE}/shop/"
    p = sh["product"]
    price_txt = f"NT${p['price']:,}"
    pay_url = (getattr(S, "SHOP_PAY_URL", "") or "").strip()
    parts = []
    parts.append(crumb("服務與價格", "#services", "線上購買"))
    parts.append(hero(1, sh["en"], sh["h1"], sh["badge"]))
    facts = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in sh["facts"])
    parts.append(f"""<section class="pg-card pg-answer pg-rise" aria-label="簡短回答">
    <p class="pg-lead">{e(sh["answer"])}</p>
    <dl class="pg-facts">{facts}</dl>
  </section>""")

    # 結帳按鈕：build 時依 SHOP_PAY_URL 決定（前端不寫死）。
    # 空字串＝LINE 下單（預填訂購訊息）；有值＝前往 TapPay 付款連結
    if pay_url:
        checkout = (f'<a class="pg-btn pg-btn-solid" id="pg-checkout" href="{e(pay_url)}" rel="noopener" '
                    f'data-track="go-checkout">前往結帳</a>')
        note = ""
    else:
        order = "https://line.me/R/oaMessage/%40879gqgah/?text=" + quote(sh["order_text"], safe="")
        checkout = (f'<a class="pg-btn pg-btn-solid" id="pg-checkout" href="{order}" target="_blank" rel="noopener" '
                    f'data-track="go-order-line">LINE 下單</a>')
        note = f'<p class="pg-pay-note">{e(sh["order_note"])}</p>'

    parts.append(f"""<section class="pg-sec pg-sec-s pg-reveal" id="pg-shop">
  {label(2, "PRODUCT")}
  <h2 class="pg-h2" id="product">選購商品</h2>
  <article class="pg-card pg-prod">
    <div class="pg-prod-body">
      <h3>{e(p["name"])}<span class="pg-badge">{e(p["badge"])}</span></h3>
      <p>{e(p["desc"])}</p>
    </div>
    <div class="pg-prod-buy">
      <p class="pg-price"><b>{price_txt}</b><span>／{e(p["unit"])}，固定價</span></p>
      <button type="button" class="pg-btn pg-btn-solid" id="pg-add" aria-describedby="pg-cart-live" data-track="add-to-cart">加入購物車</button>
      <a class="pg-u pg-strong pg-viewcart" id="pg-view-cart" href="#pg-cart-h" hidden data-track="view-cart">查看購物車 ↓</a>
    </div>
  </article>
</section>
<section class="pg-sec pg-sec-s pg-reveal" id="pg-cart" aria-labelledby="pg-cart-h">
  {label(3, "CART")}
  <h2 class="pg-h2" id="pg-cart-h" tabindex="-1">購物車<span id="pg-cart-count" class="pg-cart-count">（0 件）</span></h2>
  <div class="pg-card pg-cart">
    <p class="pg-sr" id="pg-cart-live" role="status" aria-live="polite"></p>
    <div id="pg-cart-empty">
      <p class="pg-cart-empty-t">{e(sh["empty_title"])}</p>
      <p class="pg-cart-empty-h">{e(sh["empty_hint"])}<a class="pg-u pg-strong" href="#product" data-track="cart-back-to-product">回到商品</a></p>
    </div>
    <div id="pg-cart-full" hidden>
      <div class="pg-cart-row">
        <div class="pg-cart-name"><b>{e(p["name"])}</b><span>數量 1 份</span></div>
        <dl class="pg-cart-nums">
          <div><dt>單價</dt><dd>{price_txt}</dd></div>
          <div><dt>小計</dt><dd>{price_txt}</dd></div>
        </dl>
        <button type="button" class="pg-btn pg-btn-ghost pg-rm" id="pg-cart-rm" aria-label="從購物車移除{e(p["name"])}" data-track="remove-from-cart">移除</button>
      </div>
      <p class="pg-cart-total"><span>合計</span><b>{price_txt}</b></p>
      <div class="pg-cart-go">
        {checkout}
        {note}
      </div>
    </div>
    <noscript><p class="pg-cart-empty-h">購物車需要開啟 JavaScript。也可以直接<a class="pg-u pg-strong" href="{C.LINE_URL}" target="_blank" rel="noopener">加 LINE 洽談</a>。</p></noscript>
  </div>
</section>""")

    n = 4
    steps = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in sh["steps"])
    parts.append(f'<section class="pg-sec pg-sec-s pg-reveal">\n  {label(n, "ORDER")}\n  <h2 class="pg-h2">怎麼訂購</h2>\n  <ol class="pg-steps pg-steps3">{steps}</ol>\n</section>')

    n += 1
    inc = "".join(f'<article class="pg-tile" style="--sp:4"><h3>{e(t)}</h3><p>{e(d)}</p></article>' for t, d in sh["includes"])
    parts.append(f'<section class="pg-sec pg-sec-s pg-reveal">\n  {label(n, "INCLUDES")}\n  <h2 class="pg-h2">你會拿到什麼</h2>\n  <div class="pg-bento">{inc}</div>\n</section>')

    n += 1
    fit = "".join(f"<li>{CHECK}<span>{e(t)}</span></li>" for t in sh["fit"])
    fol = "".join(f"<li>{CHECK}<span>{e(t)}</span></li>" for t in sh["followup"])
    noi = "".join(f"<li>{NO_ICO}<span>{faq_html(t)}</span></li>" for t in sh["not_incl"])
    parts.append(f"""<section class="pg-sec pg-sec-s pg-reveal">
  {label(n, "SCOPE")}
  <h2 class="pg-h2">適合誰、不包含什麼</h2>
  <div class="pg-split">
    <div><h3 class="pg-h3">適合</h3><ul class="pg-fit pg-sol">{fit}</ul>
      <h3 class="pg-h3">後續</h3><ul class="pg-fit pg-sol">{fol}</ul></div>
    <div><h3 class="pg-h3">不包含</h3><ul class="pg-fit pg-sol">{noi}</ul></div>
  </div>
</section>""")

    n += 1
    parts.append(f"""<section class="pg-sec pg-sec-s pg-reveal">
  {label(n, "PAYMENT")}
  <h2 class="pg-h2">付款資訊</h2>
  <div class="pg-card pg-pay">
    <p class="pg-lead">{e(sh["pay_text"])}</p>
    <p class="pg-tappay"><img src="../../img/tappay/tappay-horizontal.png" width="662" height="261" alt="TapPay 金流"></p>
    <p class="pg-pay-sec">{e(sh["security"])}</p>
    <p class="pg-pay-sec">{e(sh["pci"])}</p>
  </div>
</section>""")

    comp = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in sh["company"])
    contact = (f'<div><dt>LINE ID</dt><dd><a class="pg-u" href="{C.LINE_URL}" target="_blank" rel="noopener" data-track="shop-line-id">{C.LINE_ID}</a></dd></div>'
               f'<div><dt>電話</dt><dd><a class="pg-u" href="tel:{sh["phone_href"]}" data-track="click-phone">{e(sh["phone"])}</a></dd></div>'
               f'<div><dt>Email</dt><dd><a class="pg-u" href="mailto:{e(sh["email"])}" data-track="click-email">{e(sh["email"])}</a></dd></div>')
    stages = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in sh["refund"])
    n += 1
    parts.append(f"""<section class="pg-sec pg-sec-s pg-reveal">
  {label(n, "COMPANY")}
  <h2 class="pg-h2">公司資訊與聯繫方式</h2>
  <dl class="pg-card pg-info">{comp}{contact}</dl>
</section>""")
    n += 1
    parts.append(f"""<section class="pg-sec pg-sec-s pg-reveal" id="refund-policy">
  {label(n, "REFUND")}
  <h2 class="pg-h2">退換貨與退款政策</h2>
  <div class="pg-faq"><details id="pg-refund-d" open>
    <summary>{e(sh["refund_summary"])}</summary>
    <div class="pg-refund">
      <p class="pg-text">{e(sh["refund_intro"])}</p>
      <ol class="pg-stages">{stages}</ol>
      <p class="pg-text pg-refund-via">{e(sh["refund_via"])}</p>
      <a class="pg-u pg-strong" href="../../#refund" data-track="shop-refund-link">查看完整付款與退款政策 →</a>
    </div>
  </details></div>
</section>""")
    parts.append(cta_card("bottom"))

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            crumb_ld("服務與價格", S.SITE + "/#services", "線上購買", url),
            webpage_ld(url, sh["title"], sh["description"]),
            {
                "@type": "Product",
                "@id": url + "#product",
                "name": p["name"],
                "description": sh["ld_desc"],
                "url": url,
                "brand": {"@id": S.SITE + "/#org"},
                "offers": {
                    "@type": "Offer",
                    "url": url,
                    "price": p["price"],
                    "priceCurrency": "TWD",
                    "availability": "https://schema.org/InStock",
                    "seller": {"@id": S.SITE + "/#org"},
                },
            },
        ],
    }
    body = "\n".join(parts) + "\n" + SHOP_JS
    out = page_shell(head(sh["title"], sh["description"], url, ld), body)
    # 本頁只有一層（shop/），共用區塊寫的是兩層（services/<slug>/）的相對路徑
    out = out.replace("../../", "../")
    write(os.path.join("shop", "index.html"), out)


# ---------- 檔案輸出 ----------
def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote", rel.replace("\\", "/"))


def lastmod(rel):
    """該頁最後實際改動日：有未提交的變更＝今天，否則取最後一次 commit 的日期（拿不到就用今天）。"""
    import subprocess
    try:
        run = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()  # noqa: E731
        if run("status", "--porcelain", "--", rel):
            return TODAY
        return run("log", "-1", "--format=%cs", "--", rel) or TODAY
    except Exception:
        return TODAY


def build_sitemap():
    pages = [("/", "index.html")] + [(f"/services/{s['slug']}/", f"services/{s['slug']}/index.html") for s in C.SERVICES] \
        + [(f"/work/{w['slug']}/", f"work/{w['slug']}/index.html") for w in C.WORKS] + [("/shop/", "shop/index.html")]
    rows = "".join(
        f"  <url>\n    <loc>{S.SITE}{path}</loc>\n    <lastmod>{lastmod(rel)}</lastmod>\n  </url>\n"
        for path, rel in pages)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<!-- 由 tools/build_pages.py 產生，不要手動修改 -->\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")


def main():
    for s in C.SERVICES:
        build_service(s)
    for w in C.WORKS:
        build_work(w)
    build_shop()
    build_sitemap()


if __name__ == "__main__":
    main()
