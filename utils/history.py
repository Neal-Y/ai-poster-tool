import os

def record_decision(prompt_hash: str, action: str, file_path: str = "history.csv"):
    """
    紀錄使用者對某個 prompt 的決策，例如：'posted'、'skipped'
    """
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{prompt_hash},{action}\n")
