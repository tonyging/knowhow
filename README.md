# 諾豪資訊 官方網站

「諾豪」取自 **Know-how**：把專業知識，變成可以直接使用的成品。
諾豪資訊提供小型軟體開發服務，包含一頁式網站、資料轉換、API 串接、LINE 官方帳號機器人，以及網站維運與資安健檢。

**網站：https://tonyging.github.io/knowhow/**

---

## 概要

| 項目 | 說明 |
|---|---|
| 形式 | 單頁式靜態網站，單一 HTML 檔，無建置步驟、無外部資源、無第三方追蹤 |
| 版面 | 5 個整屏區塊，滾輪一格翻一整頁；矮螢幕、窄螢幕與「減少動態效果」設定自動改為一般捲動 |
| 響應式 | 桌機、平板、手機（最小支援 320px 寬） |
| 色彩 | 淺色與深色模式皆支援，依系統設定切換 |
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
| `index.html` | 網站本體，內含樣式、互動腳本與 JSON-LD 結構化資料 |
| `logo.png` | 標誌與 favicon |
| `llms.txt` | 提供給 AI 搜尋與 LLM 讀取的網站摘要（[llmstxt.org](https://llmstxt.org/) 格式） |

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
