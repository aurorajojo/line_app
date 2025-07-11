## 各檔案說明

### `app.py`
- 主程式入口。
- 使用 Flask 建立伺服器，並設定 `/callback` 路由處理 LINE Webhook。
- 導入 `line_handlers` 模組進行事件處理。

### `config.py`
- 儲存環境變數的載入，例如 Groq API 金鑰、伺服器網址等。
- 與 `.env` 檔案結合，集中管理設定值。

### `line_handlers.py`
- 處理來自 LINE 的訊息事件。
- 匯入 GPT 模型處理邏輯（來自 `llm.py`）。
- 定義收到文字訊息後的應對流程。

### `llm.py`
- 封裝與語言模型（Groq / LLaMA）溝通的邏輯。
- 定義如何將使用者訊息送出並取得回應。

### `system_prompt.py`
- 載入 `system_prompt.txt`，提供語言模型的指令（角色、語氣等）。

## `render_wake_up.py`
- 定時 ping Render 平台以防止伺服器自動休眠。

### `system_prompt.txt`
- 儲存語言模型的 system prompt，用於引導模型回應風格與身份定位。

## `requirements.txt`
- 記錄所需的 Python 套件。

## 指令

下載套件：
```bash
pip install -r requirements.txt
```
啟動程式：
```bash
python app.py
```
