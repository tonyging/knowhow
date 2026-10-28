# -*- coding: utf-8 -*-
"""網站共用設定。換網域時用 `py tools/set_domain.py 新網域`，不要手動改。"""

# 網站根網址（不含結尾斜線）
SITE = "https://tonyging.github.io/knowhow"

# Umami 追蹤碼
UMAMI_ID = "61f8dd1d-a873-4ab9-80a0-dcf2a8809eeb"
UMAMI_DOMAINS = "tonyging.github.io"

# 對外的官方頁面（給搜尋引擎辨認同一個品牌）
SAME_AS = [
    "https://line.me/R/ti/p/@879gqgah",
    "https://www.tasker.com.tw/workroom/nuohao",
    "https://www.linkedin.com/in/%E9%98%BF%E9%87%91-undefined-15b0aa38b",
    # TODO: PRO360 專家頁網址還沒有，拿到後加在這裡
]

# 線上購買頁（/shop/）結帳按鈕連到的 TapPay 付款連結。
# 空字串＝按鈕是「LINE 下單」（預填訂購訊息，我們再把付款連結傳給客人）；
# 有值＝按鈕改成「前往結帳」，連到這個付款連結。填好後重跑 build_pages.py。
SHOP_PAY_URL = ""
