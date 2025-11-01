"""
AI Insights Service - Generate intelligent insights using Gemini and semantic search
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from google import genai
from sqlalchemy.orm import Session
from services.vector_service import get_vector_service
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIInsightsService:
    """Service for generating AI-powered insights"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client"""
        api_key_value = api_key or os.getenv('GEMINI_API_KEY')
        if api_key_value:
            self.genai_client = genai.Client(api_key=api_key_value)
        else:
            print("Warning: GEMINI_API_KEY not found. AI insights will not be available.")
            self.genai_client = None
        self.vector_service = get_vector_service()
        self.model = "gemini-2.0-flash-exp"
    
    def generate_search_terms(self, insight_type: str) -> List[str]:
        """Generate search terms for a specific insight type using Gemini"""
        if not self.genai_client:
            return self._get_fallback_search_terms(insight_type)
        
        try:
            prompt = f"""Generate 3-5 specific search terms to find relevant information about: {insight_type}
            
Return only the search terms, one per line, without numbering or explanations.
Focus on technical and project management keywords.

Example for "project risks":
- blocked tasks
- overdue deadlines
- failed builds
- critical issues"""

            response = self.genai_client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Extract search terms from response
            text = response.text.strip()
            terms = [term.strip('- ').strip() for term in text.split('\n') if term.strip()]
            return terms[:5]  # Limit to 5 terms
        
        except Exception as e:
            print(f"Error generating search terms: {str(e)}")
            return self._get_fallback_search_terms(insight_type)
    
    def _get_fallback_search_terms(self, insight_type: str) -> List[str]:
        """Fallback search terms if Gemini is unavailable"""
        fallback_terms = {
            "project_health": ["project status", "task completion", "deadline progress"],
            "team_performance": ["team velocity", "completed tasks", "active contributors"],
            "code_quality": ["code review", "failed builds", "merge conflicts"],
            "blockers": ["blocked tasks", "dependencies", "waiting status"],
            "upcoming_risks": ["overdue", "critical priority", "approaching deadline"],
            "recent_achievements": ["completed", "merged PR", "resolved issues"]
        }
        return fallback_terms.get(insight_type, ["project status", "team activity"])
    
    def generate_insight(
        self,
        db: Session,
        insight_type: str,
        project_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a specific type of insight"""
        
        try:
            # Step 1: Generate search terms
            search_terms = self.generate_search_terms(insight_type)
            
            # Step 2: Perform semantic search for each term
            all_context_items = []
            for term in search_terms:
                items = self.vector_service.semantic_search(
                    query=term,
                    content_types=None,  # Search all types
                    project_ids=project_ids,
                    n_results=5,
                    min_similarity_score=0.3
                )
                all_context_items.extend(items)
            
            # Remove duplicates based on ID
            unique_items = {item['id']: item for item in all_context_items}
            context_items = list(unique_items.values())
            
            # Step 3: Build context string
            context_str = self._build_context_string(context_items[:10])
            
            # Step 4: Generate insight using Gemini
            if not self.genai_client:
                return self._generate_fallback_insight(insight_type, context_items)
            
            insight_text = self._generate_gemini_insight(insight_type, context_str)
            
            return {
                "success": True,
                "insight_type": insight_type,
                "insight": insight_text,
                "context_count": len(context_items),
                "search_terms": search_terms,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            print(f"Error generating insight: {str(e)}")
            return {
                "success": False,
                "insight_type": insight_type,
                "insight": f"Unable to generate insight: {str(e)}",
                "context_count": 0,
                "search_terms": [],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_context_string(self, items: List[Dict[str, Any]]) -> str:
        """Build a context string from retrieved items"""
        if not items:
            return "No relevant data found."
        
        context_parts = []
        for item in items:
            content_type = item.get('content_type', 'unknown')
            document = item.get('document', '')
            similarity = item.get('similarity_score', 0.0)
            
            context_parts.append(
                f"[{content_type.upper()}] (Relevance: {similarity:.2f})\n{document}\n"
            )
        
        return "\n".join(context_parts)
    
    def _generate_gemini_insight(self, insight_type: str, context: str) -> str:
        """Generate insight using Gemini"""
        
        insight_prompts = {
            "project_health": """Based on the project data below, provide a brief insight about overall project health.
Focus on: task completion rates, status distribution, and any concerning patterns.
Keep it concise (2-3 sentences) and actionable.""",
            
            "team_performance": """Based on the team activity data below, provide a brief insight about team performance.
Focus on: velocity, collaboration patterns, and workload distribution.
Keep it concise (2-3 sentences) and actionable.""",
            
            "code_quality": """Based on the code activity data below, provide a brief insight about code quality.
Focus on: PR review status, build failures, and code review patterns.
Keep it concise (2-3 sentences) and actionable.""",
            
            "blockers": """Based on the project data below, identify any blockers or impediments.
Focus on: blocked tasks, dependencies, and stuck work items.
Keep it concise (2-3 sentences) and actionable.""",
            
            "upcoming_risks": """Based on the project data below, identify upcoming risks or potential issues.
Focus on: approaching deadlines, overdue items, and critical priorities.
Keep it concise (2-3 sentences) and actionable.""",
            
            "recent_achievements": """Based on the project data below, highlight recent achievements and wins.
Focus on: completed tasks, merged PRs, and resolved issues.
Keep it concise (2-3 sentences) and positive."""
        }
        
        prompt = insight_prompts.get(
            insight_type,
            "Provide a brief, actionable insight based on the project data below."
        )
        
        full_prompt = f"""{prompt}

PROJECT DATA:
{context}

INSIGHT:"""
        
        try:
            response = self.genai_client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating Gemini insight: {str(e)}")
            return f"Unable to generate insight for {insight_type}"
    
    def _generate_fallback_insight(
        self,
        insight_type: str,
        context_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate basic insight without Gemini"""
        
        item_count = len(context_items)
        fallback_insights = {
            "project_health": f"Found {item_count} relevant items across projects. AI analysis unavailable.",
            "team_performance": f"Tracking {item_count} team activities. AI analysis unavailable.",
            "code_quality": f"Monitoring {item_count} code-related items. AI analysis unavailable.",
            "blockers": f"Identified {item_count} potential blockers. AI analysis unavailable.",
            "upcoming_risks": f"Found {item_count} items requiring attention. AI analysis unavailable.",
            "recent_achievements": f"Tracking {item_count} recent activities. AI analysis unavailable."
        }
        
        return {
            "success": False,
            "insight_type": insight_type,
            "insight": fallback_insights.get(insight_type, "AI service unavailable"),
            "context_count": item_count,
            "search_terms": [],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_multiple_insights(
        self,
        db: Session,
        insight_types: List[str],
        project_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple insights at once"""
        
        insights = []
        for insight_type in insight_types:
            insight = self.generate_insight(db, insight_type, project_ids, user_id)
            insights.append(insight)
        
        return insights


# Global instance
_insights_service: Optional[AIInsightsService] = None


def get_insights_service() -> AIInsightsService:
    """Get or create insights service instance"""
    global _insights_service
    if _insights_service is None:
        _insights_service = AIInsightsService()
    return _insights_service
