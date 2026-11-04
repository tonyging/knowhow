"""通知 Bing（以及 Yandex 等支援 IndexNow 的搜尋引擎）哪些頁面更新了。

push 上線後跑一次：
  py -X utf8 -I tools/indexnow.py            # 送出 sitemap.xml 的全部網址
  py -X utf8 -I tools/indexnow.py <網址>...   # 只送指定網址

金鑰檔是 repo 根目錄那個 32 碼十六進位檔名的 .txt（內容等於檔名），必須在線上
https://nuohao.tw/<金鑰>.txt 讀得到，不能刪。金鑰本來就是公開的，不算機密。
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "nuohao.tw"


def find_key():
    for p in ROOT.glob("*.txt"):
        if re.fullmatch(r"[0-9a-f]{32}", p.stem) and p.read_text().strip() == p.stem:
            return p.stem
    sys.exit("找不到 IndexNow 金鑰檔（根目錄的 <32 碼>.txt）")


def main():
    key = find_key()
    urls = sys.argv[1:] or re.findall(r"<loc>([^<]+)", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    urls = [u for u in urls if u.startswith(f"https://{HOST}/")]
    body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt",
                       "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow 回應 {r.status}（200／202 都是成功），送出 {len(urls)} 個網址")
    except urllib.error.HTTPError as e:
        # 403＝線上讀不到金鑰檔（還沒 push？）；422＝網址不屬於這個網域
        sys.exit(f"IndexNow 失敗 {e.code}：{e.read().decode('utf-8', 'replace')[:200]}")


if __name__ == "__main__":
    main()
