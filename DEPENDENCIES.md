# 環境依賴 (Dependencies)

以下為本專案所需的外部依賴套件。開發環境建議使用 Python 3.12 以上版本。

| Package Name | Version | Purpose |
| :--- | :--- | :--- |
| `Flask` | `== 3.1.3` | 提供後端 API 與網頁伺服器功能（路由、模板渲染）。 |
| `python-pptx` | `== 1.0.2` | 讀取 PPT 模板並將系統資料匯出為 PowerPoint 簡報，以及批次匯入舊有 PPT 報告。 |
| `Pillow` | `== 12.2.0` | 處理圖片縮放與裁剪，以適應 PowerPoint 佔位符大小與比例。 |

## 安裝指令

請在專案根目錄下執行以下指令，以安裝所有必要的套件：

```bash
pip install -r requirements.txt
```
