from image.client.client import generate_image, generate_batch
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
        if decision in ["y", "r", "s"]:
            break

    if decision == "y":
        print("📤 已記錄：發佈")
        record_decision(prompt_hash, "posted")
    elif decision == "s":
        print("❌ 已記錄：略過")
        record_decision(prompt_hash, "skipped")
    elif decision == "r":
        print("🔁 重新產圖...")
        return review_prompt(prompt)

    return prompt_hash, decision

def review_prompt_batch(prompts: list[str]) -> list[tuple[str, str]]:
    responses = generate_batch(prompts)
    results = []

    for prompt, prompt_hash, filepath in responses:
        preview_image(filepath)

        while True:
            decision = input(f"\n是否發佈這張圖片？\n👉 Prompt: {prompt}\n[Y] 發佈 / [R] 重產 / [S] 略過：").strip().lower()
            if decision in ["y", "r", "s"]:
                break

        if decision == "y":
            record_decision(prompt_hash, "posted")
        elif decision == "s":
            record_decision(prompt_hash, "skipped")
        elif decision == "r":
            print("🔁 重新產圖...")
            # 單張重產
            new_hash, new_file = generate_image(prompt)
            preview_image(new_file)
            record_decision(new_hash, "posted")
            prompt_hash = new_hash

        results.append((prompt_hash, decision))

    return results