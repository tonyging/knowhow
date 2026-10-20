# 諾豪資訊 官方網站

一頁式靜態網站，沒有建置步驟、沒有外部資源。

| 檔案 | 用途 |
|---|---|
| `index.html` | 網站本體（含 JSON-LD 結構化資料） |
| `logo.png` | 標誌與 favicon |
| `llms.txt` | 給 AI 搜尋與 LLM 讀的網站摘要（llmstxt.org 格式） |

## 公開前檢查

客服資訊（電話、Email、LINE ID、服務時間）已填入。公開前確認：

```
grep -n "待填" index.html
```

沒有輸出才代表沒有殘留的佔位符。

## 公開（GitHub Pages）

儲存庫要改成 public，免費方案才能開 Pages：

```
gh repo edit --visibility public --accept-visibility-change-consequences
gh api -X POST repos/{owner}/{repo}/pages -f "source[branch]=main" -f "source[path]=/"
```

## 網址假設（上線後要核對）

`index.html` 的 JSON-LD 與 `llms.txt` 裡的網址，都假設網站公開在
`https://tonyging.github.io/knowhow/`。

如果實際網址不同（例如改用自訂網域），要把這個網址在兩個檔案裡全部取代掉：

```
grep -n "tonyging.github.io/knowhow" index.html llms.txt
```

## AI 搜尋可讀性

- **`llms.txt`**：公司名稱、一句話介紹、服務項目與價格、合作方式與政策、聯絡方式、主要區塊連結。
- **JSON-LD**（`index.html` 的 `<head>`）：`Organization`（含聯絡方式、服務時間）、
  `OfferCatalog`（三項服務，前兩項有最低價 `minPrice`）、`WebSite`。
- 不含地址（沒有公開地址）、不含 LINE ID（schema.org 沒有對應欄位，已寫在 `llms.txt`）。
- 內容必須和頁面可見內容一致；改價格、時間或聯絡方式時，三個地方都要改：
  頁面、JSON-LD、`llms.txt`。

公開後可用下列工具驗證：

- https://validator.schema.org/ ：貼上網址，檢查結構化資料語法。
- https://search.google.com/test/rich-results ：Google 的測試工具。
  注意：`Organization` 本身不屬於 Google 的 Rich Results 類型，工具可能顯示「沒有偵測到支援的項目」，
  這不代表錯誤；以 schema.org 驗證器沒有錯誤為準。
