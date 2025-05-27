from dotenv import load_dotenv
load_dotenv()

from notion.trigger import NotionTrigger
from preview.cli import review_prompt_batch

def main():
    print("🚀 啟動 Notion 圖文審核流程")
    trigger = NotionTrigger()
    notes = trigger.get_ready_notes()

    if not notes:
        print("📭 沒有待處理的筆記")
        return

    # 直接使用 note_id 作為識別
    prompts = [(note["id"], note.get("prompt") or f"{note['title']}\n{note['content']}") for note in notes]

    reviewed_results = review_prompt_batch(prompts)

    for note_id, decision in reviewed_results:
        if decision == "posted":
            trigger.mark_as_published(note_id, post_url=None)
        elif decision == "skipped":
            trigger.mark_as_skipped(note_id)
        else:
            trigger.mark_for_retry(note_id)

if __name__ == "__main__":
    main()
