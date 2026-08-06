# PCCSIM 系統維護與營運手冊 (MAINTENANCE.md)

本手冊提供系統維護人員進行日常營運、開發環境配置、PyInstaller 自動化打包、資料庫備份還原以及常見故障排除 (Troubleshooting) 之標準作業程序 (SOP)。

---

## 1. 開發環境與依賴管理 (Environment & Dependencies)

### 1.1 系統需求
* **作業系統**：Windows 10 / Windows 11 / Windows Server 2016+ (64-bit)
* **Python 版本**：Python 3.10.x 或 3.12.x (64-bit)

### 1.2 環境建置步驟
1. 複製專案庫並切換至專案根目錄。
2. 建立並啟動 Python 虛擬環境 (Virtual Environment)：
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. 安裝第三方套件依賴：
   ```bash
   pip install -r requirements.txt
   ```

### 1.3 核心依賴套件對照表
| Package Name | Exact Version | Purpose (用途簡述) |
| :--- | :--- | :--- |
| `Flask` | `== 3.1.1` | Web 後端控制器框架與 WSGI 伺服器 |
| `python-pptx` | `== 1.0.2` | PowerPoint (.pptx) 檔案 XML 結構解析與生成 |
| `Pillow` | `== 11.1.0` | 圖片處理、尺寸量測與格式轉換 |
| `Werkzeug` | `== 3.1.8` | 安全檔案名稱處理 (`secure_filename`) 與 HTTP 工具 |
| `PyInstaller` | `== 6.12.0` | 獨立執行檔打包與靜態資源封裝工具 |

---

## 2. 自動化打包與部署作業 (Build & Deployment)

專案已配置自動化腳本 `build.bat` 與 PyInstaller 規格檔 `PCCIM.spec`。

### 2.1 執行打包指令
在專案根目錄下，開啟 CMD 或 PowerShell 執行：
```cmd
build.bat
```

### 2.2 打包運作流程 (`build.bat` SOP)
1. **清理舊建構檔**：自動刪除 `build/` 與 `dist/` 資料夾。
2. **執行 PyInstaller**：執行 `pyinstaller -y --clean PCCIM.spec` 進行模組與靜態檔 (`templates/`, `static/`) 封裝。
3. **複製關鍵資產**：
   - 複製 `pccim.db` 至 `dist\PCCIM\pccim.db`。
   - 複製 `ppt_templates/` 模板資料夾至 `dist\PCCIM\ppt_templates\`。
4. **初始化執行目錄**：自動建立空資料夾 `dist\PCCIM\uploads\` 與 `dist\PCCIM\exports\`。

### 2.3 部署綠色套件 (Deployment Directory Structure)
打包完成後，`dist\PCCIM\` 即為一個獨立運作的綠色解壓套件。將該資料夾複製至目標主機即可直接執行：

```
dist\PCCIM\
├── PCCIM.exe              <-- 主程式執行檔 (雙擊即可開啟 Web 伺服器)
├── pccim.db               <-- SQLite 資料庫檔案
├── _internal\             <-- Python runtime 與 DLL 依賴庫
├── ppt_templates\         <-- PowerPoint 匯出模板 (pccim_template.pptx)
├── uploads\               <-- 使用者上傳附件儲存區
└── exports\               <-- 匯出簡報暫存區
```

---

## 3. 資料庫維護作業 (Database Maintenance)

### 3.1 資料庫備份 (Backup Procedure)
SQLite 為單一檔案結構，備份時只需複製 `pccim.db` 檔案。

* **熱備份 (Hot Backup)**：若系統運作中，建議透過 SQLite CLI 執行線上備份命令，避免併發寫入造成鎖定：
  ```bash
  sqlite3 pccim.db ".backup 'pccim_backup_YYYYMMDD.db'"
  ```
* **冷備份 (Cold Backup)**：關閉 `PCCIM.exe` 後，直接複製 `pccim.db` 檔至備份磁碟。

### 3.2 資料庫還原 (Restore Procedure)
1. 停止 `PCCIM.exe` 伺服器進程。
2. 將原 `pccim.db` 重命名為 `pccim.db.bak`。
3. 將備份檔複製並重命名為 `pccim.db`。
4. 重新啟動 `PCCIM.exe` 並檢查日誌。

### 3.3 架構變更 (Schema Migration Procedure)
當需新增資料表欄位時，請依據以下 SOP 手動執行 SQL 升級指令：
```sql
-- 範例：新增欄位
ALTER TABLE applications ADD COLUMN priority TEXT DEFAULT 'Medium';
```

---

## 4. 故障排除與日誌診斷 (Troubleshooting FAQ)

### 4.1 通訊埠 5005 被佔用 (`OSError: [Errno 98] Address already in use`)
* **原因**：已有另一個 `PCCIM.exe` 或 Python 進程在背景運作並綁定 PORT 5005。
* **解法**：
  1. 開啟 CMD 尋找佔用進程 PID：
     ```cmd
     netstat -ano | findstr :5005
     ```
  2. 強制終止該進程：
     ```cmd
     taskkill /PID <PID> /F
     ```

### 4.2 網頁找不到模板 (`jinja2.exceptions.TemplateNotFound`)
* **原因**：PyInstaller 執行檔啟動時無法找到 `templates/` 資料夾。
* **解法**：確認 `config.py` 中使用了 `sys.frozen` 判斷路徑，且 `PCCIM.spec` 中的 `datas` 正確包含 `('templates', 'templates')`。

### 4.3 匯出 PPT 失敗 (`FileNotFoundError: pccim_template.pptx`)
* **原因**：`ppt_templates/` 目錄內缺少預設模板檔案 `pccim_template.pptx`。
* **解法**：確認 `dist\PCCIM\ppt_templates\` 目錄下包含正確的 `.pptx` 模板檔案。

### 4.4 批次匯入包含非 PPT 檔案導致系統異常
* **原因**：使用者選取的資料夾包含過大檔或損壞檔案。
* **解法**：系統已於 `app.py` 中實作自動過濾機制，非 `.ppt` / `.pptx` 檔將自動 Skip 忽略，不影響其他正常檔案之建檔。
