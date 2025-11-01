"""
AI Chat Service - Gemini 2.5 Flash with RAG
Uses vector database for context retrieval
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from google import genai
from sqlalchemy.orm import Session
from models.database_models import ChatHistory, EmployeeProfile
from services.vector_service import get_vector_service
import os
import json


class AIChatService:
    """Service for AI-powered chat with project context"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client"""
        self.genai_client = genai.Client(api_key=api_key or os.getenv('GEMINI_API_KEY'))
        self.vector_service = get_vector_service()
        self.model = "gemini-2.0-flash-exp"
    
    def chat(
        self,
        db: Session,
        user_id: str,
        message: str,
        project_ids: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with AI assistant using RAG (Retrieval Augmented Generation)
        
        Args:
            db: Database session
            user_id: User ID making the request
            message: User's message/question
            project_ids: Optional list of project IDs to filter context
            content_types: Optional list of content types to search (pr, issue, jira_task, comment)
            conversation_history: Optional previous conversation context
        
        Returns:
            Dict with response, context items, and metadata
        """
        try:
            # Step 1: Retrieve relevant context from vector database
            relevant_items = self.vector_service.semantic_search(
                query=message,
                content_types=content_types,
                project_ids=project_ids,
                n_results=10
            )
            
            # Step 2: Build context string from retrieved items
            context_str = self._build_context_string(relevant_items)
            
            # Step 3: Build conversation history
            history_str = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    history_str += f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}\n\n"
            
            # Step 4: Create prompt with context
            system_prompt = """You are an AI assistant for AutoPM, a project management system that integrates with GitHub and Jira. 

You have access to:
- GitHub Pull Requests (PRs) with their status, reviews, and code changes
- GitHub Issues with labels, assignees, and priorities
- Jira Tasks with story points, dependencies, and statuses
- Comments from both GitHub and Jira

Your role is to help users:
- Understand project status and progress
- Find specific PRs, issues, or tasks
- Analyze blockers and dependencies
- Track team performance and velocity
- Answer questions about code reviews and testing
- Identify risks and delays

Use the provided context to answer questions accurately. If the context doesn't contain enough information, say so clearly.
Always cite specific PR IDs, issue IDs, or task IDs when referencing them.
"""
            
            user_prompt = f"""
Context from project data:
{context_str}

{f"Previous conversation:\n{history_str}" if history_str else ""}

User question: {message}

Please provide a helpful, accurate response based on the context provided. If you reference specific items, include their IDs.
"""
            
            # Step 5: Call Gemini API
            response = self.genai_client.models.generate_content(
                model=self.model,
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt}]},
                    {"role": "model", "parts": [{"text": "Understood. I'm ready to help with AutoPM queries."}]},
                    {"role": "user", "parts": [{"text": user_prompt}]}
                ],
                config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048
                }
            )
            
            # Extract response text
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Step 6: Store in chat history
            chat_id = f"CHAT-{user_id}-{int(datetime.utcnow().timestamp())}"
            context_item_ids = [item['id'] for item in relevant_items]
            
            chat_entry = ChatHistory(
                chat_id=chat_id,
                user_id=user_id,
                message=message,
                response=response_text,
                context_items=context_item_ids
            )
            db.add(chat_entry)
            db.commit()
            
            # Step 7: Return structured response
            return {
                "success": True,
                "chat_id": chat_id,
                "response": response_text,
                "context_items": relevant_items,
                "context_count": len(relevant_items),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "context_items": [],
                "context_count": 0
            }
    
    def _build_context_string(self, items: List[Dict[str, Any]]) -> str:
        """Build a formatted context string from retrieved items"""
        if not items:
            return "No relevant context found."
        
        context_parts = []
        for i, item in enumerate(items, 1):
            context_parts.append(f"""
--- Context Item {i} (Relevance: {item['similarity_score']:.2%}) ---
Type: {item['content_type']}
ID: {item['id']}
Content:
{item['document']}
""")
        
        return "\n".join(context_parts)
    
    def get_conversation_history(
        self,
        db: Session,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's conversation history"""
        try:
            chats = db.query(ChatHistory).filter(
                ChatHistory.user_id == user_id
            ).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
            
            return [{
                "chat_id": chat.chat_id,
                "message": chat.message,
                "response": chat.response,
                "context_items": chat.context_items,
                "timestamp": chat.timestamp.isoformat()
            } for chat in reversed(chats)]
            
        except Exception as e:
            print(f"Error getting conversation history: {str(e)}")
            return []
    
    def get_suggested_questions(self, db: Session, project_id: Optional[str] = None) -> List[str]:
        """Get suggested questions based on project data"""
        suggestions = [
            "What are the current open PRs that need review?",
            "Show me high priority issues that are unassigned",
            "What are the blocked tasks and their dependencies?",
            "Which PRs have failing builds?",
            "What is the status of [project name]?",
            "Show me recent comments on PRs",
            "What tasks are assigned to me?",
            "Are there any critical bugs open?",
            "What's the progress on sprint tasks?",
            "Show me PRs merged this week"
        ]
        
        return suggestions
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of comments or messages"""
        try:
            prompt = f"""
Analyze the sentiment and tone of the following text from a project management context.
Categorize as: Positive, Neutral, Negative, or Urgent.
Also identify if it indicates a blocker or critical issue.

Text: {text}

Respond in JSON format:
{{
    "sentiment": "Positive/Neutral/Negative/Urgent",
    "is_blocker": true/false,
    "is_critical": true/false,
    "summary": "brief explanation"
}}
"""
            
            response = self.genai_client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Parse JSON response
            response_text = response.text if hasattr(response, 'text') else str(response)
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {
                "sentiment": "Neutral",
                "is_blocker": False,
                "is_critical": False,
                "summary": "Unable to parse sentiment"
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {
                "sentiment": "Neutral",
                "is_blocker": False,
                "is_critical": False,
                "summary": str(e)
            }
    
    def summarize_project_status(
        self,
        db: Session,
        project_id: str
    ) -> Dict[str, Any]:
        """Generate AI summary of project status"""
        try:
            # Search for all content related to this project
            all_items = self.vector_service.semantic_search(
                query=f"project status overview progress blockers risks",
                project_ids=[project_id],
                n_results=20
            )
            
            context_str = self._build_context_string(all_items)
            
            prompt = f"""
Based on the following project data, provide a comprehensive status summary:

{context_str}

Please provide:
1. Overall project health (Green/Yellow/Red)
2. Key achievements and completed items
3. Current blockers and risks
4. Items needing attention
5. Recommendations

Format as a structured summary.
"""
            
            response = self.genai_client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "success": True,
                "project_id": project_id,
                "summary": response_text,
                "context_items_analyzed": len(all_items),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error summarizing project: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "summary": "Unable to generate summary"
            }


# Global instance
_chat_service: Optional[AIChatService] = None


def get_chat_service() -> AIChatService:
    """Get or create chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = AIChatService()
    return _chat_service
