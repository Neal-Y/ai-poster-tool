from dotenv import load_dotenv
load_dotenv()

from notion.trigger import NotionTrigger
from preview.cli import review_prompt

def main():
    print("🚀 啟動 Notion 圖文審核流程")
    trigger = NotionTrigger()
    notes = trigger.get_ready_notes()

    if not notes:
        print("📭 沒有待處理的筆記")
        return

    for note in notes:
        prompt = note.get("prompt") or f"{note['title']}\n{note['content']}"
        print(f"\n📝 處理筆記：{note['title']}")

        prompt_hash, decision = review_prompt(prompt)

        if decision == "posted":
            trigger.update_note_status(note['id'], "Published")
        elif decision == "skipped":
            trigger.update_note_status(note['id'], "Skipped")
        else:
            print("🔁 重產未更新狀態")

if __name__ == "__main__":
    main()
