"""從中文原稿 index.html 產生泰文（th/）與日文（ja/）版本。

中文 index.html 是唯一的內容來源，直接手動編輯它；其他語言一律由本腳本產生，不要手改。
翻譯放在 tools/translations.py。

用法：
  py tools/build_i18n.py            # 檢查翻譯是否涵蓋所有單位，並產生 th/index.html、ja/index.html、sitemap.xml、校對稿
  py tools/build_i18n.py --check    # 只檢查，不輸出

需要 beautifulsoup4：py -m pip install beautifulsoup4
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n_units as U  # noqa: E402
from translations import PAIRS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://tonyging.github.io/knowhow/"

LANGS = {
    "th": {
        "idx": 1, "html_lang": "th", "og_locale": "th_TH", "name": "ไทย",
        "note": "ข้อความภาษาจีนเป็นฉบับหลัก หากการแปลมีความแตกต่างกัน ให้ถือฉบับภาษาจีนเป็นหลัก",
        "css": """
html[lang="th"] body{font-family:"Noto Sans Thai","Leelawadee UI","Tahoma","Thonburi","Sarabun",system-ui,sans-serif;line-height:1.75}
html[lang="th"] body *{letter-spacing:0 !important}
html[lang="th"] .label,html[lang="th"] .vt-head .en,html[lang="th"] .menu-foot,html[lang="th"] .tg,html[lang="th"] .cap,html[lang="th"] ol.steps li::before{letter-spacing:.2em !important}
html[lang="th"] .rail-cta .vt{writing-mode:vertical-rl;text-orientation:sideways}
html[lang="th"] .rail-brand .vt{letter-spacing:.14em !important}
/* 泰文不適合直排：標語改橫排，章節直排標題隱藏（每屏本來就有橫排標題） */
html[lang="th"] .vt-h2{display:none}
html[lang="th"] .tag{writing-mode:horizontal-tb;max-width:none;font-size:clamp(28px,min(3.2vw,5vh),46px);line-height:1.45;font-weight:600;margin:0}
html[lang="th"] .col{display:inline;padding:0}
html[lang="th"] .col::before{display:none}
html[lang="th"] .col+.col::before{display:none}
@media (min-width:1000px){
  html[lang="th"] .hero-grid{grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);row-gap:clamp(14px,3vh,28px)}
  html[lang="th"] .tag{grid-column:1/-1}
}
""",
    },
    "ja": {
        "idx": 2, "html_lang": "ja", "og_locale": "ja_JP", "name": "日本語",
        "note": "翻訳に差異がある場合は、中国語版を正とします。",
        "css": """
html[lang="ja"] body{font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans","Yu Gothic UI","Yu Gothic","Meiryo","Noto Sans JP",system-ui,sans-serif;line-break:strict}
""",
    },
}


def resolve(units):
    """把 PAIRS 對應到實際單位。回傳 ({lang: {unit: translation}}, errors)。"""
    out = {k: {} for k in LANGS}
    errors, used = [], {}
    for row in PAIRS:
        zh = U.norm(row[0]) if "<" not in row[0] else row[0]
        exact = [u for u in units if u == zh]
        cands = exact or [u for u in units if u.startswith(zh)]
        if len(cands) != 1:
            errors.append(("缺漏" if not cands else f"不唯一（{len(cands)}）") + f"：{row[0][:60]}")
            continue
        u = cands[0]
        if u in used:
            errors.append(f"重複對應同一單位：{row[0][:40]} ＆ {used[u][:40]}")
            continue
        used[u] = row[0]
        for lg, cfg in LANGS.items():
            out[lg][u] = row[cfg["idx"]]
    uncovered = [u for u in units if u not in used]
    return out, errors, uncovered


def set_inner(el, html):
    for ch in list(el.contents):
        ch.extract()
    frag = BeautifulSoup(html, "html.parser")
    for node in list(frag.contents):
        el.append(node)


def build(lang, cfg, src_html, tr):
    soup = BeautifulSoup(src_html, "html.parser")
    url = f"{BASE}{lang}/"

    # 1) 區塊文字（先收集再取代，避免走訪時修改樹）
    for el, key in U.collect_blocks(soup):
        if key in tr:
            set_inner(el, tr[key])

    # 2) 屬性
    for el in soup.body.find_all(True):
        for a in U.ATTRS:
            v = el.get(a)
            if v and U.norm(v) in tr:
                el[a] = tr[U.norm(v)]

    # 3) title 與 meta
    if soup.title and soup.title.string and U.norm(soup.title.string) in tr:
        soup.title.string = tr[U.norm(soup.title.string)]
    for m in soup.find_all("meta"):
        name = m.get("name") or m.get("property") or ""
        c = m.get("content")
        if c and U.norm(c) in tr:
            m["content"] = tr[U.norm(c)]
        if name == "og:locale":
            m["content"] = cfg["og_locale"]
        if name == "og:url":
            m["content"] = url
        if name == "og:locale:alternate":
            m["content"] = {"th_TH": "zh_TW", "ja_JP": "zh_TW"}.get(m["content"], m["content"]) if m["content"] == cfg["og_locale"] else m["content"]
    # 備用語系：移除與本頁相同的，補上中文
    alts = soup.find_all("meta", attrs={"property": "og:locale:alternate"})
    for m in alts:
        if m["content"] == cfg["og_locale"]:
            m["content"] = "zh_TW"
    can = soup.find("link", rel="canonical")
    if can:
        can["href"] = url

    # 4) JSON-LD
    for sc in soup.find_all("script", type="application/ld+json"):
        data = json.loads(sc.string)

        def rec(v):
            if isinstance(v, dict):
                for k in list(v):
                    x = v[k]
                    if isinstance(x, str):
                        if x in tr:
                            v[k] = tr[x]
                        elif x.startswith(BASE + "#"):
                            v[k] = url + x[len(BASE):]
                        if k == "inLanguage":
                            v[k] = cfg["html_lang"]
                    else:
                        rec(x)
            elif isinstance(v, list):
                for i, x in enumerate(v):
                    if isinstance(x, str) and x in tr:
                        v[i] = tr[x]
                    else:
                        rec(x)

        rec(data)
        sc.string = json.dumps(data, ensure_ascii=False, indent=2)

    # 5) 語言、資源路徑、切換器
    soup.html["lang"] = cfg["html_lang"]
    for el in soup.find_all(True):
        for a in ("src", "href"):
            v = el.get(a)
            if v in ("logo.png", "og.png"):
                el[a] = "../" + v
    hrefs = {"zh": "../", "th": "../th/", "ja": "../ja/"}
    hrefs[lang] = "./"
    for a in soup.select("a[data-lang]"):
        code = a["data-lang"]
        a["href"] = hrefs[code]
        if code == lang:
            a["aria-current"] = "true"
        elif a.has_attr("aria-current"):
            del a["aria-current"]

    # 6) 泰文：字元逐一動畫會拆散組合字元，移除
    if lang == "th":
        for el in soup.find_all(attrs={"data-split": True}):
            del el["data-split"]

    # 7) 字型與直排修正
    st = soup.new_tag("style")
    st.string = cfg["css"]
    soup.head.append(st)

    # 8) 以中文為準的提醒
    note_html = f'<p class="tr-note">{cfg["note"]}</p>'
    foot = soup.find("footer", class_="foot")
    if foot:
        foot.append(BeautifulSoup(note_html, "html.parser"))
    tin = soup.select_one(".terms-in")
    if tin:
        tin.append(BeautifulSoup(note_html, "html.parser"))
    st2 = soup.new_tag("style")
    st2.string = ".tr-note{flex-basis:100%;margin:6px 0 0;font-size:13px;line-height:1.6;color:var(--muted)}.terms-in .tr-note{margin-top:14px;padding-top:12px;border-top:1px solid var(--line)}"
    soup.head.append(st2)

    return str(soup)


def write_sitemap():
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    pages = [("", "zh-Hant-TW"), ("th/", "th"), ("ja/", "ja")]
    for path, _ in pages:
        xml.append("  <url>")
        xml.append(f"    <loc>{BASE}{path}</loc>")
        for p2, lg in pages:
            xml.append(f'    <xhtml:link rel="alternate" hreflang="{lg}" href="{BASE}{p2}"/>')
        xml.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}"/>')
        xml.append("    <changefreq>monthly</changefreq>")
        xml.append(f"    <priority>{'1.0' if path == '' else '0.8'}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")


def write_review(units, tr_all):
    d = ROOT / "i18n"
    d.mkdir(exist_ok=True)
    for lg, cfg in LANGS.items():
        lines = [f"# {cfg['name']} 翻譯校對稿",
                 "",
                 "請母語者逐列檢查右欄的翻譯是否通順、自然、專業；有問題請直接在該列旁標註建議用字。",
                 "含有 `<b>`、`<span>` 等標籤的列，請保留標籤，只改文字。",
                 "",
                 "| # | 中文原文 | 譯文 |", "|---|---|---|"]
        for i, u in enumerate(units, 1):
            if u in tr_all[lg] and tr_all[lg][u] != u:
                a = u.replace("|", "\\|").replace("\n", " ")
                b = tr_all[lg][u].replace("|", "\\|").replace("\n", " ")
                lines.append(f"| {i} | {a} | {b} |")
        (d / f"review-{lg}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    check = "--check" in sys.argv
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    units = U.all_units(src)
    tr_all, errors, uncovered = resolve(units)
    if errors:
        print("翻譯對照表有問題：")
        for e in errors:
            print("  -", e)
    if uncovered:
        print(f"尚未翻譯的單位 {len(uncovered)} 個（會保留中文）：")
        for u in uncovered:
            print("  -", u[:100])
    if errors:
        sys.exit(1)
    if check:
        print(f"檢查完成：{len(units)} 個單位，缺漏 {len(uncovered)}")
        return
    for lg, cfg in LANGS.items():
        out = build(lg, cfg, src, tr_all[lg])
        d = ROOT / lg
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(out, encoding="utf-8")
        print(f"已產生 {lg}/index.html")
    write_sitemap()
    write_review(units, tr_all)
    print("已更新 sitemap.xml 與 i18n/review-*.md")


if __name__ == "__main__":
    main()
