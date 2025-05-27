from image.client.client import generate_image, generate_batch
from utils.history import record_decision
from PIL import Image

def preview_image(filepath: str):
    img = Image.open(filepath)
    img.show()

def review_prompt_batch(prompts: list[tuple[str, str]]) -> list[tuple[str, str]]:
    results = []
    ids = [note_id for note_id, _ in prompts]
    prompt_texts = [p for _, p in prompts]

    response_list = generate_batch(prompt_texts)

    for i, (prompt_hash, prompt, filepath) in enumerate(response_list):
        note_id = ids[i]
        preview_image(filepath)

        while True:
            decision = input(f"\n是否發佈這張圖片？\n👉 Prompt: {prompt}\n[Y] 發佈 / [R] 重產 / [S] 略過：").strip().lower()
            if decision in ["y", "r", "s"]:
                break

        if decision == "y":
            print("📤 已記錄：發佈")
            record_decision(prompt_hash, "posted")
        elif decision == "s":
            print("❌ 已記錄：略過")
            record_decision(prompt_hash, "skipped")
        elif decision == "r":
            print("🔁 重新產圖中...")
            new_file, new_hash = generate_image(prompt)
            preview_image(new_file)
            record_decision(new_hash, "posted")

        status_map = {"y": "posted", "s": "skipped", "r": "retry"}
        results.append((note_id, status_map[decision]))

    return results