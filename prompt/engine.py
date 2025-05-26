"""
Prompt Engine Module
Handles creation of prompts for image generation
"""
import logging
import os
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PromptEngine:
    """Creates prompts for image generation based on note content and templates"""
    
    def __init__(self):
        """Initialize the prompt engine with templates"""
        self.templates_path = os.path.join(os.path.dirname(__file__), "templates.json")
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load prompt templates from file"""
        try:
            if os.path.exists(self.templates_path):
                with open(self.templates_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Default templates if file doesn't exist
                default_templates = {
                    "default": {
                        "prefix": "Create a professional, visually appealing image for social media that represents: ",
                        "suffix": " Style: clean, modern, minimalist, suitable for Instagram.",
                        "parameters": {
                            "quality": "high quality, detailed, sharp focus",
                            "lighting": "soft lighting, balanced exposure",
                            "composition": "centered composition, rule of thirds"
                        }
                    },
                    "quote": {
                        "prefix": "Create an inspirational quote image with text that says: ",
                        "suffix": " Style: elegant typography, motivational, shareable.",
                        "parameters": {
                            "background": "subtle gradient or abstract background",
                            "text": "clear, readable font, prominent placement",
                            "mood": "inspiring, uplifting, positive"
                        }
                    },
                    "tech": {
                        "prefix": "Create a tech-focused image that illustrates: ",
                        "suffix": " Style: futuristic, digital, tech-oriented.",
                        "parameters": {
                            "elements": "digital elements, tech symbols, code snippets",
                            "colors": "blue tones, high contrast, glowing accents",
                            "mood": "innovative, cutting-edge, professional"
                        }
                    }
                }
                
                # Save default templates
                os.makedirs(os.path.dirname(self.templates_path), exist_ok=True)
                with open(self.templates_path, "w", encoding="utf-8") as f:
                    json.dump(default_templates, f, indent=2, ensure_ascii=False)
                
                return default_templates
        
        except Exception as e:
            logger.exception(f"Error loading templates: {str(e)}")
            # Fallback to minimal default template
            return {
                "default": {
                    "prefix": "Create an image that represents: ",
                    "suffix": " Style: clean, professional, suitable for social media.",
                    "parameters": {}
                }
            }
    
    def create_prompt(self, note: Dict[str, Any]) -> str:
        """
        Create a prompt for image generation based on note content
        
        Args:
            note: Note object containing content and metadata
            
        Returns:
            Prompt string for image generation
        """
        try:
            # Determine which template to use based on tags
            template_name = self._select_template(note.get("tags", []))
            template = self.templates.get(template_name, self.templates["default"])
            
            # Extract key content from the note
            title = note.get("title", "").strip()
            content = note.get("content", "").strip()
            
            # Use title as the main subject if content is too long
            main_subject = title
            if len(content) > 0 and len(content) < 500:
                # Use first paragraph of content if it'ss not too long
                paragraphs = content.split("\n\n")
                if paragraphs:
                    main_subject = paragraphs[0]
            
            # Build the prompt
            prompt = f"{template['prefix']}{main_subject}{template['suffix']}"
            
            # Add parameters
            parameters = []
            for param_name, param_value in template.get("parameters", {}).items():
                parameters.append(f"{param_value}")
            
            if parameters:
                prompt += f" {', '.join(parameters)}"
            
            return prompt
        
        except Exception as e:
            logger.exception(f"Error creating prompt: {str(e)}")
            # Fallback to a simple prompt
            return f"Create a simple image for: {note.get('title', 'Untitled')}"
    
    def _select_template(self, tags: List[str]) -> str:
        """
        Select the appropriate template based on note tags
        
        Args:
            tags: List of tags from the note
            
        Returns:
            Template name to use
        """
        # Convert tags to lowercase for case-insensitive matching
        tags_lower = [tag.lower() for tag in tags]
        
        # Check if any tag matches a template name
        for tag in tags_lower:
            if tag in self.templates:
                return tag
        
        # Check for category matches
        if any(tag in ["quote", "quotes", "inspiration"] for tag in tags_lower):
            return "quote"
        elif any(tag in ["tech", "technology", "coding", "programming"] for tag in tags_lower):
            return "tech"
        
        # Default template
        return "default"
