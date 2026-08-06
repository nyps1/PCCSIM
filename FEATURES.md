# PCCSIM 功能總覽 (Features Overview)

本專案是一個用來管理與追蹤製程或設備異常 (Problem & Containment) 的網頁應用程式。提供高度整合的 PPT 上傳、附件管理與標籤系統，以下為目前系統支援的詳細功能列表。

## 1. 核心網頁功能 (Web Interface)

### 1.1 申請單建立 (Application Form)
提供兩種輸入模式供使用者選擇，所有的申請單都會自動配發一組唯一的申請單號 (Apply Number)。
* **手動輸入模式 (Manual Mode)**：使用者可以在表單內手動填寫完整的 8D Report 或異常報告欄位（Problem, Action Taken, Impact, Containment, Root Cause, Solution, Implementation, Monitoring）。針對各個階段皆可上傳對應的佐證附件與備註。
* **PPT 上傳模式 (PPT Upload Mode)**：若使用者已經有一份標準格式的 PPT 報告，只需填寫基本資訊（如標題、作者、機台等），並將該 PPT 拖曳至上傳區塊。系統會在後端自動解析 PPT 內容，並將 PPT 內的文字與圖片抽取出建立為系統附件資料。
  * *UI 回饋*：上傳區塊具備互動式視覺回饋，選取檔案後外框與背景會自動切換為紅色，並顯示選取的檔案名稱。

### 1.2 動態標籤系統 (Dynamic Labels)
* 系統首創整合 **Choices.js**，提供現代化且直覺的標籤多選介面，取代傳統需要按住 Ctrl/Cmd 才能多選的選單。
* 支援**即時建立新標籤**：若選單中沒有合適的標籤，使用者可以直接在旁邊的輸入框輸入新標籤名稱並點擊 Add，系統會透過 API 即時寫入資料庫，並自動為使用者勾選該新標籤，無需重新整理網頁。

### 1.3 搜尋與過濾 (Search & Filter)
* 提供多維度的條件搜尋，包含：Apply Date, Title, IN/DN, Create Date, Close Date, Machine/Tool, Module Name, Department, Author 等。
* 支援依照**標籤 (Labels)** 進行精準過濾，快速找尋特定類別的異常案件。
* 提供表格化的搜尋結果呈現，並支援一鍵導航至案件詳細頁面或編輯頁面。

### 1.4 案件詳情與附件檢視 (Detail & Attachments)
* **資料預覽**：所有填寫的文字與關聯的標籤都會在 Detail 頁面結構化呈現。
* **附件預覽與下載**：
  * 圖片類型附件會直接在網頁上渲染顯示，並附帶專屬的 Download Image 按鈕。
  * PPT 檔案（不論是透過 PPT 模式或是 Batch Import 模式上傳的原檔）會以卡片形式呈現，並提供 Download PowerPoint 按鈕。
  * 支援將目前的案件資料匯出為一份新的 PPTX 報告檔 (Export PPT功能)。

### 1.5 批次匯入介面 (Batch Import UI)
* **入口方式**：在網頁左上角的「PCCSIM」導覽列 Logo **連續點擊兩下 (Double-Click)** 即可進入 Batch Import 頁面。
* **瀏覽器線上檔案上傳**：允許使用者一次選取（或拖曳）多個 PPT/PPTX 檔案，系統會在背景循序解析每一個檔案，將其內容、圖片與原版 PPT 檔案一併寫入資料庫。
* **本機資料夾路徑掃描**：直接輸入伺服器/本機的資料夾路徑，系統會透過 `PCCIMService.import_batch_from_directory()` 自動掃描該資料夾下所有 PPT 檔並建檔，原始檔案保持完好不搬移。
* **詳細狀態回饋**：執行後會即時列出每個檔案的處理狀態表格（包含檔名、成功/失敗狀態標籤、對應申請單號連結與錯誤詳細說明）。

---

## 2. 系統底層與架構 (Architecture)

* **後端框架**：Flask (Python)。
* **商業邏輯與批次服務**：採用 Service / Repository Pattern，將批次資料夾掃描與解析完整封裝至 `PCCIMService`，在打包為單一可執行檔 (`PCCSIM.exe`) 後亦能完整運作。
* **資料庫**：SQLite (`database/pccim.db`)，採用 Factory Pattern (DatabaseManager) 與 Service Layer (PCCIMService) 分離資料庫操作與業務邏輯。
* **PPT 解析引擎**：使用 `python-pptx` 函式庫來深度解析 PowerPoint XML 結構、抓取內嵌圖片、以及根據模板建立新的匯出報告。
* **前端技術**：純 HTML, CSS (自訂樣式庫) 與原生 JavaScript，無依賴重型前端框架（如 React/Vue），確保極快的載入速度與極低的維護成本。僅針對下拉選單輕量級引入了 Choices.js。
