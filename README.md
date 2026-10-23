# 諾豪資訊 官方網站

「諾豪」取自 **Know-how**：把專業知識，變成可以直接使用的成品。
諾豪資訊提供小型軟體開發服務，包含一頁式網站、資料轉換、API 串接、LINE 官方帳號機器人，以及網站維運與資安健檢。

**網站：https://tonyging.github.io/knowhow/**

---

## 概要

| 項目 | 說明 |
|---|---|
| 形式 | 單頁式靜態網站；目前只提供中文（泰文、日文版暫時隱藏，見「多語系」）。除了成效統計（Umami）之外，不載入任何外部資源 |
| 版面 | 6 個整屏區塊，滾輪一格翻一整頁；矮螢幕、窄螢幕與「減少動態效果」設定自動改為一般捲動 |
| 響應式 | 桌機、平板、手機（最小支援 320px 寬） |
| 色彩 | 固定淺色，不跟隨系統深色模式（深色樣式保留，在 `<html>` 加上 `data-theme="dark"` 可手動啟用） |
| 託管 | GitHub Pages，`main` 分支根目錄，強制 HTTPS |

### 區塊

1. **首頁**：品牌由來與主要服務入口
2. **服務與流程**：服務項目、起算價格、合作流程
3. **作品範例**：微光指尖（美甲美睫線上預約＋店家後台）、嵐岸咖啡（形象官網＋後台），桌機用分頁切換、手機上下排列；另有諾豪自己的 LINE 官方帳號
4. **維運與資安**：月費維運方案與資安健檢
5. **關於與付款**：關於我們、付款方式、依進度的退款政策（完整條款為彈出視窗）
6. **客服資訊**：LINE 官方帳號、電話、Email、服務時間

## 專案結構

| 檔案 | 用途 |
|---|---|
| `index.html` | 網站本體（**中文原稿，唯一的內容來源**），內含樣式、互動腳本與 JSON-LD 結構化資料 |
| `th/index.html`、`ja/index.html` | 泰文、日文版（**目前隱藏、未連結，內容已過期**），由腳本產生，不要手動修改 |
| `tools/` | `build_i18n.py`（產生多語言版本）、`translations.py`（翻譯對照表）、`i18n_units.py`（列出需翻譯的文字） |
| `img/work-*.webp` | 作品範例屏的截圖：`work-glimmer`、`work-coffee` 是桌機首頁（1200×712），`*-mobile` 是手機版（780×1688，疊在桌機圖右下角）；`work-glimmer-book`、`work-glimmer-admin` 是預約流程與店家後台截圖，備用 |
| `sitemap.xml` | 網站地圖（目前只有中文；加回多語系時由腳本重新產生） |
| `og.png` | 社群分享預覽圖（1200×630） |
| `google112b97dce942d55e.html` | Google Search Console 擁有權驗證檔，**不要刪除**，刪除會失去驗證 |
| `logo.png` | 標誌與 favicon |
| `llms.txt` | 提供給 AI 搜尋與 LLM 讀取的網站摘要（[llmstxt.org](https://llmstxt.org/) 格式） |

## 成效追蹤（Umami）

使用 [Umami Cloud](https://umami.is/) 免費版統計，不使用 cookie，不蒐集可識別個人的資料。追蹤碼在 `index.html` 的 `<head>`，只統計 `tonyging.github.io`（本機預覽不會送出資料），並尊重瀏覽器的「Do Not Track」設定。頁尾有「隱私說明」彈窗，三種語言都有。

按鈕點擊以 `data-track` 屬性標記，Umami 載入後才會送出事件：

| 事件名稱 | 對應的元素 |
|---|---|
| `hero-line-cta` | 首屏「LINE 洽談」 |
| `hero-view-services` | 首屏「查看服務與價格」 |
| `copy-line-id` | 複製 LINE ID |
| `click-phone` | 點電話 |
| `click-email` | 點 Email |
| `open-refund-terms` | 開啟完整退款條款 |
| `open-privacy` | 開啟隱私說明 |
| `work-tab-glimmer`、`work-tab-coffee` | 作品範例切換分頁 |
| `work-glimmer-site` | 微光指尖「看網站」 |
| `work-glimmer-admin` | 微光指尖「看店家後台」 |
| `work-coffee-site` | 嵐岸咖啡「看網站」 |
| `work-coffee-backend` | 嵐岸咖啡「看後台怎麼改」 |
| `work-line-oa` | 作品範例 LINE 官方帳號卡「看聯絡方式」 |

新增要追蹤的按鈕時，加上 `data-track="事件名稱"` 即可。更換追蹤工具或網域時，記得同步修改隱私說明的內容。

## 多語系（目前隱藏，如何加回來）

泰文、日文版目前**暫時隱藏**：`th/`、`ja/` 資料夾與翻譯字典 `tools/translations.py` 都保留，但中文頁面不再連到它們，`sitemap.xml`、`llms.txt` 也不列出。`th/`、`ja/` 的內容是隱藏前產生的，**沒有包含「作品範例」屏與新的選單編號**。

加回來的步驟：

1. 在 `index.html` 還原三處：`<head>` 的 `hreflang="th"`、`hreflang="ja"` 兩條 `<link rel="alternate">` 與兩條 `og:locale:alternate`；全螢幕選單與頁尾各一個被註解掉的 `<nav class="langs">`（搜尋「語言切換」）。
2. 到 `tools/translations.py` 補上新增文字（作品範例屏等）的泰文與日文翻譯。
3. 執行 `py -m pip install beautifulsoup4`，再執行 `py tools/build_i18n.py`（只檢查用 `--check`）。腳本會重新產生 `th/`、`ja/`、含 hreflang 的 `sitemap.xml`，以及校對稿 `i18n/review-*.md`。
4. 在 `llms.txt` 補回「其他語言」段落，一起提交。

校對稿是內部工作文件，已列入 `.gitignore`，不進公開 repo。法律與退款條款以中文版為準。
