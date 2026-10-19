# 諾豪資訊 官方網站

一頁式靜態網站，沒有建置步驟、沒有外部資源。檔案：`index.html`、`logo.png`。

## 上線前必做

`index.html` 的「客服資訊」還有 4 個 `【待填：…】` 欄位（電話、Email、LINE ID、服務時間）。
這些必須和藍新金流商店填的客服資訊一致，填完才能公開。

檢查指令（沒有輸出才代表填完）：

```
grep -n "待填" index.html
```

## 公開（GitHub Pages）

儲存庫要改成 public，免費方案才能開 Pages：

```
gh repo edit --visibility public --accept-visibility-change-consequences
gh api -X POST repos/{owner}/{repo}/pages -f "source[branch]=main" -f "source[path]=/"
```
