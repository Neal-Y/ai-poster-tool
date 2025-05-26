"""
Publisher Interface Module
Defines the abstract interface for social media publishers
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class PublishResult:
    """Result of publishing to a platform"""
    success: bool
    post_url: Optional[str] = None
    post_id: Optional[str] = None
    error: Optional[str] = None

class Publisher(ABC):
    """Abstract base class for social media publishers"""
    
    @abstractmethod
    def publish(self, image_path: str, caption: str, metadata: Dict[str, Any] = None) -> PublishResult:
        """
        Publish content to a social media platform
        
        Args:
            image_path: Path to the image file
            caption: Text caption for the post
            metadata: Additional metadata for the post
            
        Returns:
            PublishResult with success status and post details or error
        """
        pass
    
    @abstractmethod
    def delete(self, post_id: str) -> bool:
        """
        Delete a post from the platform
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
