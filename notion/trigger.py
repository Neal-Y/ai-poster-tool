import logging
import os
from typing import Dict, List, Any, Optional

from notion_client import Client

logger = logging.getLogger(__name__)

class NotionTrigger:
    """負責從 Notion 取得待處理筆記，並進行狀態更新"""

    def __init__(self):
        """初始化 Notion 客戶端"""
        self.notion = Client(auth=os.environ.get("NOTION_API_KEY"))
        self.database_id = os.environ.get("NOTION_DATABASE_ID")

        if not self.database_id:
            logger.error("NOTION_DATABASE_ID 環境變數未設定")
            raise ValueError("NOTION_DATABASE_ID environment variable not set")

    def get_ready_notes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        取得狀態為 Ready 且已勾選 Publish 的筆記
        """
        try:
            filter_params = {
                "filter": {
                    "and": [
                        {
                            "property": "Status",
                            "select": {
                                "equals": "Ready"
                            }
                        },
                        {
                            "property": "Publish",
                            "checkbox": {
                                "equals": True
                            }
                        }
                    ]
                },
                "sorts": [
                    {
                        "property": "Created",
                        "direction": "ascending"
                    }
                ],
                "page_size": limit
            }

            response = self.notion.databases.query(
                database_id=self.database_id,
                **filter_params
            )

            results = []
            for page in response.get("results", []):
                page_id = page["id"]
                page_content = self._get_page_content(page_id)
                properties = page.get("properties", {})
                title = self._extract_title(properties)
                tags = self._extract_tags(properties)
                prompt = self._extract_prompt(properties)
                if not prompt:
                    prompt = f"{title}\n{page_content}"

                results.append({
                    "id": page_id,
                    "title": title,
                    "content": page_content,
                    "tags": tags,
                    "url": page.get("url"),
                    "prompt":prompt
                })

            return results

        except Exception as e:
            logger.exception(f"取得待處理筆記失敗: {str(e)}")
            return []

    def _get_page_content(self, page_id: str) -> str:
        """取得指定頁面的內容"""
        try:
            blocks = self.notion.blocks.children.list(block_id=page_id).get("results", [])
            content = []

            for block in blocks:
                block_type = block.get("type")
                if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item"]:
                    text_content = self._extract_text_from_block(block, block_type)
                    if text_content:
                        content.append(text_content)

            return "\n".join(content)

        except Exception as e:
            logger.exception(f"取得頁面內容失敗 {page_id}: {str(e)}")
            return ""

    def _extract_text_from_block(self, block: Dict[str, Any], block_type: str) -> str:
        """從指定區塊中提取文字內容"""
        try:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            return "".join([text.get("plain_text", "") for text in rich_text])
        except Exception:
            return ""

    def _extract_title(self, properties: Dict[str, Any]) -> str:
        """從屬性中提取標題文字"""
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "title":
                title_parts = prop_value.get("title", [])
                return "".join([part.get("plain_text", "") for part in title_parts])
        return "Untitled"

    def _extract_tags(self, properties: Dict[str, Any]) -> List[str]:
        """從屬性中提取 tags 標籤"""
        for prop_name, prop_value in properties.items():
            if prop_value.get("type") == "multi_select":
                return [tag.get("name", "") for tag in prop_value.get("multi_select", [])]
        return []

    def _extract_prompt(self, properties: Dict[str, Any]) -> str:
        """從屬性中提取 Prompt 說明"""
        prop = properties.get("Prompt", {})
        if prop.get("type") == "rich_text":
            return "".join([t.get("plain_text", "") for t in prop.get("rich_text", [])])
        return ""

    def mark_as_published(self, page_id: str, post_url: str) -> None:
        """將筆記標記為已發佈"""
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {"select": {"name": "Published"}},
                    "Process": {"checkbox": False},
                    "Post URL": {"url": post_url}
                }
            )
            logger.info(f"標記 {page_id} 為 Published")
        except Exception as e:
            logger.exception(f"標記 {page_id} 為 Published 失敗: {str(e)}")

    def mark_as_failed(self, page_id: str, error: str) -> None:
        """將筆記標記為產圖失敗"""
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {"select": {"name": "Failed"}},
                    "Process": {"checkbox": False},
                    "Error": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": error[:2000]}
                            }
                        ]
                    }
                }
            )
            logger.info(f"標記 {page_id} 為 Failed")
        except Exception as e:
            logger.exception(f"標記 {page_id} 為 Failed 失敗: {str(e)}")

    def mark_as_skipped(self, page_id: str) -> None:
        """將筆記標記為略過"""
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {"select": {"name": "Skipped"}},
                    "Process": {"checkbox": False}
                }
            )
            logger.info(f"標記 {page_id} 為 Skipped")
        except Exception as e:
            logger.exception(f"標記 {page_id} 為 Skipped 失敗: {str(e)}")

    def mark_as_reviewed(self, page_id: str) -> None:
        """將筆記標記為已審核（但尚未發佈）"""
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {"select": {"name": "Reviewed"}},
                    "Process": {"checkbox": False}
                }
            )
            logger.info(f"標記 {page_id} 為 Reviewed")
        except Exception as e:
            logger.exception(f"標記 {page_id} 為 Reviewed 失敗: {str(e)}")

    def mark_for_retry(self, page_id: str) -> None:
        """將筆記標記為 Retry 以便再次處理"""
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {"select": {"name": "Retry"}}
                }
            )
            logger.info(f"標記 {page_id} 為 Retry")
        except Exception as e:
            logger.exception(f"標記 {page_id} 為 Retry 失敗: {str(e)}")