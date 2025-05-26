from image.client.client import generate_image
from utils.history import record_decision
from PIL import Image

def preview_image(filepath):
    img = Image.open(filepath)
    img.show()

def review_prompt(prompt: str) -> tuple[str, str]:
    filepath, prompt_hash = generate_image(prompt)
    preview_image(filepath)

    while True:
        decision = input("\n是否發佈這張圖片？ [Y] 發佈 / [R] 重產 / [S] 略過：").strip().lower()
        if decision in ["y", "r", "ss"]:
            break

    if decision == "y":
        print("📤 已記錄：發佈")
        record_decision(prompt_hash, "posted")
    elif decision == "ss":
        print("❌ 已記錄：略過")
        record_decision(prompt_hash, "skipped")
    elif decision == "r":
        print("🔁 重新產圖...")
        return review_prompt(prompt)

    return prompt_hash, decision