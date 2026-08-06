# PCCSIM (Problem Containment and Countermeasure System)

本專案是一個基於 Flask 框架開發的內部問題追蹤與對策管理系統。提供使用者建立、查詢、編輯問題報告，並支援將系統資訊與附件直接匯出為 PowerPoint (.pptx) 格式的報告簡報。

## 系統架構與設計模式

- **後端架構 (Controller)**：使用 Flask 處理 HTTP 請求與路由。透過 **Dependency Injection (依賴注入)** 降低與服務層的耦合。
- **資料庫 (Factory Pattern)**：採用 SQLite 作為資料儲存，並使用 `DatabaseManager` 作為工廠動態提供獨立連線，避免 Multi-threading 的 Concurrency Safety 問題。
- **商業邏輯 (Service / Repository Pattern)**：將所有資料庫 CRUD 操作封裝於 `PCCIMService` 中，達成 Controller 與資料庫的完美解耦。
- **資料模型 (DTO Pattern)**：利用 `Application` 與 `Attachment` 等類別（並搭配 Python Type Hints）封裝請求資料。
- **簡報匯出**：結合 `python-pptx` 與 `Pillow` 函式庫，將表單資訊與附件圖片精確填入 PowerPoint 模板中。

## 快速開始 (Quick Start)

### 1. 安裝環境依賴

詳細套件與精確版本請參閱 [DEPENDENCIES.md](DEPENDENCIES.md)。

```bash
pip install -r requirements.txt
```

### 2. 啟動 Web 伺服器

執行以下指令啟動 Flask 網頁伺服器：

```bash
python app.py
```
伺服器啟動後，請開啟瀏覽器瀏覽 `http://127.0.0.1:5005`。系統會在第一次啟動時自動建立 SQLite 資料庫（預設路徑：`pccim.db`）。

### 3. 批次匯入舊有 PPT (Batch Import)

若您有舊版的 PowerPoint 報告需要匯入系統建檔，您可以透過網頁介面雙擊左上角「PCCSIM」Logo 進入隱藏的 **Batch Import PPTs** 頁面。該頁面提供兩種匯入方式：
1. **瀏覽器檔案多選/拖曳**：一次選取多個 `.ppt` 或 `.pptx` 檔案進行線上匯入。
2. **本機資料夾路徑掃描**：輸入伺服器或本機的資料夾路徑（例如：`C:\Users\User\Documents\PPT_Reports`），系統會自動掃描該資料夾下所有 PPT 檔並進行建檔，原始檔案將完好保留於原處。

## PPT 模板佔位符 (Placeholder) 設定指南

系統支援匯出 PowerPoint 報告（會讀取 `pccim_template.pptx`）。為確保資料能成功替換，請在您的 PPT 模板中加入對應的字串佔位符。系統在匯出時，會掃描簡報中所有的文字方塊並進行自動替換。

### 1. 基本資訊文字佔位符

您可以在文字方塊或表格內直接輸入以下標籤，系統將自動轉換為對應的使用者輸入文字：

- `{{REQUEST_NO}}`：申請單號
- `{{APPLY_DATE}}`：申請日期
- `{{TITLE}}`：問題標題
- `{{IN_DN}}`：IN/DN
- `{{CREATE_DATE}}`：建立日期
- `{{CLOSE_DATE}}`：結案日期
- `{{MACHINE_OR_TOOL}}`：機台/工具
- `{{MODULE_NAME}}`：模組名稱
- `{{DEPARTMENT}}`：部門
- `{{AUTHOR}}`：作者

### 2. 問題處理流程文字佔位符

針對各個處理階段的描述內容：

- `{{PROBLEM_DESCRIPTION}}`：問題描述
- `{{PROBLEM_TIMELINE}}`：問題發生時間軸
- `{{ACTION_TAKEN}}`：採取行動
- `{{IMPACT}}`：影響範圍
- `{{CONTAINER}}`：防堵措施 (Containment)
- `{{NEED_HELP}}`：需要 PE/DE 協助事項
- `{{ROOT_CAUSE_DESCRIPTION}}`：真因描述
- `{{ROOT_CAUSE_POSSIBLE_CAUSE}}`：可能原因
- `{{ROOT_CAUSE_TROUBLESHOOTING_TIMELINE}}`：除錯時間軸
- `{{SOLUTION}}`：解決方案
- `{{IMPLEMENTATION}}`：執行對策
- `{{MONITORING}}`：監控計畫

### 3. 附件清單佔位符

若要將某個區段的所有附件資訊（包含檔名、類型、備註）以文字條列出來，可使用：

- `{{ACTION_TAKEN_ATTACHMENT_LIST}}`
- `{{CONTAINER_ATTACHMENT_LIST}}`
- `{{ROOT_CAUSE_ATTACHMENT_LIST}}`
- `{{SOLUTION_ATTACHMENT_LIST}}`
- `{{IMPLEMENTATION_ATTACHMENT_LIST}}`
- `{{MONITORING_ATTACHMENT_LIST}}`
- `{{PROBLEM_PPT_ATTACHMENT_LIST}}`
- `{{ALL_ATTACHMENT_LIST}}`：列出全案所有的附件資訊

### 4. 圖片/附件插入佔位符

**圖片自動取代機制**：
若要將使用者上傳的圖片直接貼入簡報中，請在簡報內建立一個文字方塊，調整至您期望的圖片尺寸與位置，並填入下方對應的佔位符。系統匯出時會自動將該文字方塊刪除，並在該位置貼上按比例縮放過的圖片。

每個區段最多支援 N 張圖片（依據系統 `MAX_IMAGE_COUNT` 設定，預設最高為 10），請將下方的 `N` 替換為 `1` ~ `10` 之間的數字（例如第一張圖片為 `{{PROBLEM_IMAGE_1}}`）：

- 問題區段：`{{PROBLEM_IMAGE_N}}`
- 採取行動：`{{ACTION_TAKEN_IMAGE_N}}`
- 防堵措施：`{{CONTAINER_IMAGE_N}}`
- 真因分析：`{{ROOT_CAUSE_IMAGE_N}}`
- 解決方案：`{{SOLUTION_IMAGE_N}}`
- 執行對策：`{{IMPLEMENTATION_IMAGE_N}}`
- 監控計畫：`{{MONITORING_IMAGE_N}}`

除了圖片本體，也可搭配以下佔位符來顯示單一圖片的關聯資訊：
- `{{PROBLEM_IMAGE_N_REMARK}}`：該圖片之備註（將 `PROBLEM` 替換為其他區段名稱亦可）
- `{{PROBLEM_IMAGE_N_FILENAME}}`：該圖片之原始檔名
- `{{PROBLEM_IMAGE_N_NO}}`：該圖片之編號

> **防錯機制提醒 (Fail Fast)**
> 如果佔位符的拼寫錯誤，或是在 PowerPoint 內部將文字方塊的單一佔位符拆成了多個不同的文字片段（Run），系統可能無法成功辨識並替換該區塊。設計模板時，請確保大括號 `{{}}` 內為連續字元，且沒有包含斷行或多餘的格式變更。
