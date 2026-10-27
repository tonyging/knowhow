# -*- coding: utf-8 -*-
"""接上自有網域時，一次換掉全站的網址。

用法（在 repo 根目錄）：
    py tools/set_domain.py knowhow.tw --dry-run   只列出會改的地方，不寫檔
    py tools/set_domain.py knowhow.tw             實際執行

會做的事：
1. 寫 CNAME（內容為網域）
2. 把 index.html、llms.txt、robots.txt、sitemap.xml、tools/site_config.py 裡的舊網站網址
   （目前的 SITE，例如 https://tonyging.github.io/knowhow）換成 https://<網域>
   只換「網站自己」的網址；連到 demo-booking／demo-coffee 的網址不會動
3. Umami 的 data-domains 改成「<網域>,tonyging.github.io」
4. 重跑 tools/build_pages.py（服務頁、案例頁、sitemap 會用新網址重新產生）
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import site_config as S  # noqa: E402

FILES = ["index.html", "llms.txt", "robots.txt", "sitemap.xml", os.path.join("tools", "site_config.py")]
OLD_DOMAIN_ATTR = f'data-domains="{S.UMAMI_DOMAINS}"'


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 1 or not re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}", args[0]):
        print(__doc__)
        sys.exit(1)
    domain = args[0].lower()
    old = S.SITE
    new = f"https://{domain}"
    old_host = S.UMAMI_DOMAINS
    new_hosts = f"{domain},{old_host}" if domain not in old_host.split(",") else old_host
    print(f"{'[dry-run] ' if dry else ''}{old}  ->  {new}")
    print(f"Umami data-domains：{old_host}  ->  {new_hosts}")
    print(f"CNAME：{domain}")
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print(f"  (略過，檔案不存在) {rel}")
            continue
        text = open(p, encoding="utf-8", newline="").read()
        n_url = text.count(old)
        out = text.replace(old, new)
        n_dom = 0
        if rel.endswith("index.html"):
            n_dom = out.count(OLD_DOMAIN_ATTR)
            out = out.replace(OLD_DOMAIN_ATTR, f'data-domains="{new_hosts}"')
        if rel.endswith("site_config.py"):
            out2 = re.sub(r'UMAMI_DOMAINS = "[^"]*"', f'UMAMI_DOMAINS = "{new_hosts}"', out)
            n_dom = int(out2 != out)
            out = out2
        print(f"  {rel}：網址 {n_url} 處、追蹤網域 {n_dom} 處")
        if dry:
            shown = 0
            for i, line in enumerate(text.splitlines(), 1):
                if old in line and shown < 3:
                    shown += 1
                    print(f"      {rel}:{i}: {line.strip()[:110]}")
            if n_url > 3:
                print(f"      …（其餘 {n_url - 3} 處同樣會換）")
        else:
            open(p, "w", encoding="utf-8", newline="").write(out)
    # 保險：確認沒有誤傷 demo 網址
    if dry:
        demo = 0
        for rel in FILES:
            p = os.path.join(ROOT, rel)
            if os.path.exists(p):
                t = open(p, encoding="utf-8").read()
                demo += t.count("tonyging.github.io/demo-")
        print(f"demo-booking／demo-coffee 網址共 {demo} 處，不會被更動")
        print("（dry-run：沒有寫任何檔案，也沒有重跑 build_pages.py）")
        return
    with open(os.path.join(ROOT, "CNAME"), "w", encoding="utf-8", newline="\n") as f:
        f.write(domain + "\n")
    subprocess.run([sys.executable, os.path.join(HERE, "build_pages.py")], check=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    print("完成。記得到 GitHub Pages 設定填入自訂網域並勾選 Enforce HTTPS。")


if __name__ == "__main__":
    main()
