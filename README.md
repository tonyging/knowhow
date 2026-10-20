# 諾豪資訊 官方網站

「諾豪」取自 **Know-how**：把專業知識，變成可以直接使用的成品。
諾豪資訊提供小型軟體開發服務，包含一頁式網站、資料轉換、API 串接、LINE 官方帳號機器人，以及網站維運與資安健檢。

**網站：https://tonyging.github.io/knowhow/**

---

## 概要

| 項目 | 說明 |
|---|---|
| 形式 | 單頁式靜態網站；中文為內容來源，泰文與日文版由腳本產生。除了成效統計（Umami）之外，不載入任何外部資源 |
| 版面 | 5 個整屏區塊，滾輪一格翻一整頁；矮螢幕、窄螢幕與「減少動態效果」設定自動改為一般捲動 |
| 響應式 | 桌機、平板、手機（最小支援 320px 寬） |
| 色彩 | 固定淺色，不跟隨系統深色模式（深色樣式保留，在 `<html>` 加上 `data-theme="dark"` 可手動啟用） |
| 託管 | GitHub Pages，`main` 分支根目錄，強制 HTTPS |

### 區塊

1. **首頁**：品牌由來與主要服務入口
2. **服務與流程**：服務項目、起算價格、合作流程
3. **維運與資安**：月費維運方案與資安健檢
4. **關於與付款**：關於我們、付款方式、依進度的退款政策（完整條款為彈出視窗）
5. **客服資訊**：LINE 官方帳號、電話、Email、服務時間

## 專案結構

| 檔案 | 用途 |
|---|---|
| `index.html` | 網站本體（**中文原稿，唯一的內容來源**），內含樣式、互動腳本與 JSON-LD 結構化資料 |
| `th/index.html`、`ja/index.html` | 泰文、日文版，**由腳本產生，不要手動修改** |
| `tools/` | `build_i18n.py`（產生多語言版本）、`translations.py`（翻譯對照表）、`i18n_units.py`（列出需翻譯的文字） |
| `i18n/review-th.md`、`i18n/review-ja.md` | 給母語者校對用的對照稿（由腳本產生） |
| `sitemap.xml` | 三種語言的網站地圖（含 hreflang，由腳本產生） |
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

新增要追蹤的按鈕時，加上 `data-track="事件名稱"` 即可。更換追蹤工具或網域時，記得同步修改隱私說明的內容。

## 多語系（中文／泰文／日文）

每個語言一個獨立網址：`/`（中文）、`/th/`、`/ja/`，搜尋引擎可以分別收錄（已設定 `hreflang`）。

**修改內容的流程：**

1. 只編輯中文的 `index.html`。
2. 如果新增或改了文字，到 `tools/translations.py` 補上泰文與日文翻譯。
3. 產生多語言版本：

```
py -m pip install beautifulsoup4
py tools/build_i18n.py
```

腳本會檢查每一段文字是否都有翻譯，缺漏會列出來；全部涵蓋後才會輸出 `th/`、`ja/`、`sitemap.xml` 與校對稿。只想檢查不輸出：`py tools/build_i18n.py --check`。

4. 一起提交 `index.html`、`th/`、`ja/`、`sitemap.xml`、`i18n/`。

**翻譯品質**：初譯由 AI 完成，請母語者以 `i18n/review-th.md`、`i18n/review-ja.md` 校對。法律與退款條款以中文版為準，頁尾與條款視窗都有註明。

**語言注意事項**：泰文不適合直排，標語與章節標題改為橫排，並關閉逐字動畫（會拆散組合字元）；日文沿用直排。

## 本機預覽

不需要安裝任何東西，在專案目錄啟動任一靜態伺服器即可：

```
py -m http.server 8768
```

然後開啟 http://localhost:8768/ 。

## 部署

推送到 `main` 後，GitHub Pages 會自動重新建置，通常一至兩分鐘內生效。

網站網址寫在 `index.html`（JSON-LD）與 `llms.txt`。如果改用自訂網域，需要把兩個檔案裡的網址一併取代：

```
grep -n "tonyging.github.io/knowhow" index.html llms.txt
```

## 內容維護

**價格、服務項目、時間、聯絡方式與退款規則，必須同時更新三個地方**，否則 AI 搜尋與搜尋引擎讀到的內容會和頁面不一致：

| 位置 | 內容 |
|---|---|
| `index.html` 頁面本文 | 使用者看到的內容 |
| `index.html` 的 JSON-LD（`<head>`） | `Organization`、`OfferCatalog`（7 項服務）、`WebSite` |
| `llms.txt` | 服務、價格、政策與聯絡方式的文字版 |

JSON-LD 不含地址（沒有公開地址）與 LINE ID（schema.org 沒有對應欄位，已寫在 `llms.txt`）。

## 修改版面時的注意事項

- **新增 CSS 前先確認 class 名稱沒有重複**，以區塊專屬前綴命名（例：`cmp`、`scan`、`cf`），避免覆蓋既有區塊的樣式。
- 每次修改後，逐屏檢查桌機（1366、1440、1920）與手機（320、390）：區塊是否被裁切、是否橫向溢出、同排卡片高度是否一致。
- 所有區塊共用同一套版面骨架（內容框、標題位置、圓角、間距），新區塊要維持一致。
- 文字閱讀方向一律由左往右，包含直排標語。

## 結構化資料驗證

- [Schema.org 驗證器](https://validator.schema.org/)：貼上網址，確認 JSON-LD 語法無誤。
- [Google Rich Results Test](https://search.google.com/test/rich-results)：`Organization` 不屬於 Google 的 Rich Results 類型，工具可能顯示「沒有偵測到支援的項目」，這不代表錯誤，以 Schema.org 驗證器為準。

## 聯絡

洽談需求請見網站的[客服資訊](https://tonyging.github.io/knowhow/#contact)。
