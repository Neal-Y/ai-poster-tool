# AI 圖文自動發布系統（Notion → IG/Threads）

一個結合 Notion 筆記、OpenAI 圖像產生、人工審核與 IG 自動發文的 AI 圖文系統。

## 🚀 專案總覽

這是一個結合 Notion 筆記、OpenAI 圖像產生、人工審核與 IG 自動發文的 AI 圖文系統。

用戶可透過點選 Notion 中的按鈕（或設置欄位狀態），觸發自動圖像產生與審核流程，最後一鍵將圖文貼文發佈至 Instagram。系統架構解耦、模組化、支援多平台擴展（如 Threads、Facebook）與高併發處理。

本專案目前開發者主要專注於 Golang 圖片處理與後端微服務邏輯的實作，Python 相關控制流程由輔助開發者維護與支援。

## 💡 核心功能目標（G-level）

| 目標編號 | 描述 |
|---------|------|
| G1 | 使用者透過 Notion 勾選筆記並設為 Ready 狀態觸發圖文處理 |
| G2 | 自動擷取筆記內容並組成 AI 圖像 prompt |
| G3 | 圖像任務由 Go gRPC server 執行，支援 goroutine worker pool、限流、快取重用（Redis） |
| G4 | 圖片返回 Python 控制邏輯，透過 CLI 審核（後續可擴展至 Telegram bot） |
| G5 | 人工確認後，將圖文自動發佈至 IG（並抽象成 Publisher 介面支援 Threads、FB） |
| G6 | 每次任務處理皆有 log、錯誤追蹤與紀錄功能（CSV / SQLite） |

## 🔄 系統流程圖

```mermaid
        [main.py]                         <<== 主控流程
            ↓
   ┌────── get_ready_notes ───────┐       <<== Notion.trigger 抓筆記
   │ title + content              │
   └──────────────────────────────┘
            ↓
     拼接 prompt: f\"{title}\\n{content}\"
            ↓
    call review_prompt(prompt)           <<== preview.cli
            ↓
 ┌────────────────────────────────────┐
 │    generate_image(prompt)          │ <<== image.client
 │    - 快取判斷（hash）                │
 │    - gRPC 傳給 Go Server            │
 │    - 儲存本地圖片 output/xxx.png     │
 └────────────────────────────────────┘
            ↓
    顯示圖片 + 審核 CLI
        - [Y] 發佈
        - [S] 略過
        - [R] 重產（重跑 generate_image）
            ↓
      回傳 prompt_hash + decision
            ↓
[main.py] 根據 decision 做後續：
  - 發佈則更新 Notion 狀態
  - 略過則寫 history
  - 重產則 repeat

```

## 專案架構

```
ai_poster/
├── main.py                        # Python 控制流程入口
├── notion/
│   └── trigger.py                 # 擷取待處理筆記
├── prompt/
│   ├── engine.py                  # 組 prompt 與風格模板
│   └── templates.json             # 提示詞模板配置
├── image/
│   ├── client/                    # Python gRPC client
│   │   ├── client.py
│   │   ├── image.proto
│   │   ├── image_pb2.py
│   │   └── image_pb2_grpc.py
│   └── server/                    # Golang gRPC server（核心）
│       ├── main.go                # 啟動與 router 綁定服務
│       ├── handler.go             # gRPC handler 接收請求
│       ├── worker_pool.go         # 任務併發核心（goroutine + channel）
│       ├── openai.go              # OpenAI API 客戶端
│       ├── pb/                    # gRPC 生成的 Golang pb 檔案
│       │   ├── image.pb.go
│       │   └── image_grpc.pb.go
│       ├── cache.go               # 快取管理（prompt hash）
│       ├── limiter.go             # 請求限流策略（可選）
│       └── image.proto            # gRPC 定義（共用）
├── preview/
│   ├── cli.py                     # 人工審核 CLI 介面
│   └── telegram_bot.py            # Telegram bot 審核介面（可選）
│   ├── interface.py               # 發佈抽象定義
│   ├── ig.py                      # IG 發佈實作
│   └── threads.py                 # Threads 發佈實作（擴展）
├── utils/
│   └── history.py                 # 發佈記錄追蹤
├── config.yaml                    # 系統參數設定檔
├── .env.example                   # API 金鑰環境變數設定
├── requirements.txt               # Python 套件依賴
├── logs/                          # 日誌紀錄夾
├── output/                        # 圖片儲存目錄
└── history.csv                    # 圖文發佈歷史記錄
```


