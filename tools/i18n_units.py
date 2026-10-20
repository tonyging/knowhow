"""列出 index.html（中文原稿）裡所有需要翻譯的單位。

翻譯單位有三種：
  1. 區塊文字：只含文字與行內標籤（b、br、span、i、small、strong）的元素，鍵為它的 innerHTML。
  2. 屬性：aria-label、alt、title。
  3. 頁面層級：<title>、meta description、Open Graph 文字、JSON-LD 內的字串。

用法：
  py tools/i18n_units.py            # 印出數量與缺漏
  py tools/i18n_units.py th ja      # 檢查 i18n/th.json、i18n/ja.json 是否涵蓋全部單位
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent
INLINE = {"b", "strong", "em", "i", "br", "span", "small", "wbr"}
SKIP = {"script", "style", "svg", "noscript"}
ATTRS = ("aria-label", "alt", "title")
CJK = re.compile(r"[㐀-鿿＀-￯　-〿]")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def inline_only(tag: Tag) -> bool:
    for ch in tag.children:
        if isinstance(ch, Tag):
            if ch.name not in INLINE or not inline_only(ch):
                return False
    return True


def has_text(tag: Tag) -> bool:
    return bool(norm(tag.get_text()))


def collect_blocks(soup: BeautifulSoup):
    """回傳 [(element, key)]：葉節點區塊與其 innerHTML。"""
    out = []

    def walk(el: Tag):
        for ch in list(el.children):
            if not isinstance(ch, Tag) or ch.name in SKIP:
                continue
            if ch.name in INLINE and ch.parent is not None and ch.parent.name not in INLINE and not has_text(ch):
                continue
            if has_text(ch) and inline_only(ch) and ch.name not in {"br"}:
                key = norm(ch.decode_contents())
                if CJK.search(key):
                    out.append((ch, key))
            else:
                walk(ch)

    body = soup.body
    walk(body)
    return out


def jsonld_strings(soup: BeautifulSoup):
    out = []
    for sc in soup.find_all("script", type="application/ld+json"):
        data = json.loads(sc.string or "{}")

        def rec(v):
            if isinstance(v, dict):
                for k, x in v.items():
                    if isinstance(x, str) and CJK.search(x) and k not in {"@id", "url", "logo", "email", "telephone"}:
                        out.append(x)
                    else:
                        rec(x)
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, str) and CJK.search(x):
                        out.append(x)
                    else:
                        rec(x)

        rec(data)
    return out


def meta_strings(soup: BeautifulSoup):
    out = []
    if soup.title and soup.title.string:
        out.append(norm(soup.title.string))
    for m in soup.find_all("meta"):
        name = m.get("name") or m.get("property") or ""
        if name in {"description", "og:title", "og:description", "og:image:alt", "og:site_name"} and m.get("content"):
            out.append(norm(m["content"]))
    return out


def attr_strings(soup: BeautifulSoup):
    out = []
    for el in soup.body.find_all(True):
        for a in ATTRS:
            v = el.get(a)
            if v and CJK.search(v):
                out.append(norm(v))
    return out


def all_units(html: str):
    soup = BeautifulSoup(html, "html.parser")
    units = []
    units += meta_strings(soup)
    units += jsonld_strings(soup)
    units += attr_strings(soup)
    units += [k for _, k in collect_blocks(soup)]
    seen, uniq = set(), []
    for u in units:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


if __name__ == "__main__":
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    units = all_units(html)
    print(f"單位數：{len(units)}")
    langs = sys.argv[1:]
    if not langs:
        for u in units:
            print("-", u[:110])
    for lg in langs:
        f = ROOT / "i18n" / f"{lg}.json"
        d = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        missing = [u for u in units if u not in d]
        stale = [k for k in d if k not in units]
        print(f"[{lg}] 缺漏 {len(missing)}、多餘 {len(stale)}")
        for u in missing:
            print("  缺：", u[:100])
        for k in stale:
            print("  多：", k[:100])
