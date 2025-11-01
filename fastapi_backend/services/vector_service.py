"""
Vector Database Service - Embeddings and Semantic Search
Uses Google Gemini for embeddings and ChromaDB for vector storage
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from google import genai
from sqlalchemy.orm import Session
from models.database_models import (
    VectorEmbedding, GitHubActivity, GitHubIssue, JiraTask,
    GitHubComment, JiraComment, ProjectMetadata
)
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VectorDatabaseService:
    """Service for vector embeddings and semantic search"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize vector database and Gemini client"""
        # Initialize Gemini client with API key
        api_key_value = api_key or os.getenv('GEMINI_API_KEY')
        if api_key_value:
            self.genai_client = genai.Client(api_key=api_key_value)
        else:
            print("Warning: GEMINI_API_KEY not found. Embeddings will not be generated.")
            self.genai_client = None
        
        # Initialize ChromaDB with persistent storage
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collections for different content types
        self.pr_collection = self.chroma_client.get_or_create_collection(
            name="github_prs",
            metadata={"description": "GitHub Pull Requests"}
        )
        
        self.issue_collection = self.chroma_client.get_or_create_collection(
            name="github_issues",
            metadata={"description": "GitHub Issues"}
        )
        
        self.jira_collection = self.chroma_client.get_or_create_collection(
            name="jira_tasks",
            metadata={"description": "Jira Tasks and Issues"}
        )
        
        self.comment_collection = self.chroma_client.get_or_create_collection(
            name="comments",
            metadata={"description": "All comments from GitHub and Jira"}
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini"""
        try:
            if not self.genai_client:
                print("Warning: Gemini client not initialized. Returning zero vector.")
                return [0.0] * 768
            
            # Use the correct Gemini API format - embed_content expects 'contents' parameter
            result = self.genai_client.models.embed_content(
                model="models/text-embedding-004",
                contents=text  # Changed from 'content' to 'contents'
            )
            
            # Extract embedding values
            if hasattr(result, 'embedding') and hasattr(result.embedding, 'values'):
                return result.embedding.values
            elif hasattr(result, 'embeddings') and len(result.embeddings) > 0:
                return result.embeddings[0].values
            else:
                print("Warning: Unexpected embedding result format")
                return [0.0] * 768
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * 768
    
    def embed_github_pr(self, db: Session, pr: GitHubActivity) -> bool:
        """Create and store embedding for a GitHub PR"""
        try:
            # Create text representation
            text_content = f"""
            Title: {pr.title}
            PR ID: {pr.pr_id}
            Author: {pr.author_id or 'Unknown'}
            Status: {pr.status}
            Build Status: {pr.build_status}
            Changed Files: {pr.changed_files}
            Additions: {pr.additions}
            Deletions: {pr.deletions}
            Comments: {pr.comments_count}
            Created: {pr.created_at}
            Associated Issue: {pr.associated_issue_id or 'None'}
            """
            
            # Generate embedding
            embedding = self.generate_embedding(text_content)
            
            # Store in ChromaDB
            self.pr_collection.upsert(
                ids=[pr.pr_id],
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[{
                    "pr_id": pr.pr_id,
                    "project_id": pr.project_id,
                    "author_id": pr.author_id or "",
                    "status": pr.status,
                    "created_at": pr.created_at.isoformat() if pr.created_at else "",
                    "type": "pr"
                }]
            )
            
            # Store metadata in database
            embedding_id = f"EMB-PR-{pr.pr_id}"
            existing = db.query(VectorEmbedding).filter(
                VectorEmbedding.embedding_id == embedding_id
            ).first()
            
            metadata = {
                "pr_id": pr.pr_id,
                "author_id": pr.author_id,
                "status": pr.status,
                "build_status": pr.build_status,
                "reviewers": pr.reviewers,
                "associated_issue": pr.associated_issue_id
            }
            
            if existing:
                existing.title = pr.title
                existing.content_text = text_content
                existing.metadata = metadata
                existing.updated_at = datetime.utcnow()
            else:
                new_embedding = VectorEmbedding(
                    embedding_id=embedding_id,
                    content_type="pr",
                    content_id=pr.pr_id,
                    project_id=pr.project_id,
                    title=pr.title,
                    content_text=text_content,
                    metadata=metadata
                )
                db.add(new_embedding)
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error embedding PR {pr.pr_id}: {str(e)}")
            return False
    
    def embed_github_issue(self, db: Session, issue: GitHubIssue) -> bool:
        """Create and store embedding for a GitHub Issue"""
        try:
            text_content = f"""
            Title: {issue.title}
            Issue ID: {issue.issue_id}
            Author: {issue.author_id or 'Unknown'}
            Status: {issue.status}
            Type: {issue.issue_type}
            Priority: {issue.priority}
            Labels: {', '.join(issue.labels) if issue.labels else 'None'}
            Assignees: {', '.join(issue.assignees) if issue.assignees else 'None'}
            Comments: {issue.comments_count}
            Created: {issue.created_at}
            Associated PR: {issue.associated_pr_id or 'None'}
            """
            
            embedding = self.generate_embedding(text_content)
            
            self.issue_collection.upsert(
                ids=[issue.issue_id],
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[{
                    "issue_id": issue.issue_id,
                    "project_id": issue.project_id,
                    "author_id": issue.author_id or "",
                    "status": issue.status,
                    "priority": issue.priority,
                    "type": "issue"
                }]
            )
            
            embedding_id = f"EMB-ISS-{issue.issue_id}"
            existing = db.query(VectorEmbedding).filter(
                VectorEmbedding.embedding_id == embedding_id
            ).first()
            
            metadata = {
                "issue_id": issue.issue_id,
                "author_id": issue.author_id,
                "status": issue.status,
                "issue_type": issue.issue_type,
                "priority": issue.priority,
                "labels": issue.labels,
                "assignees": issue.assignees
            }
            
            if existing:
                existing.title = issue.title
                existing.content_text = text_content
                existing.metadata = metadata
                existing.updated_at = datetime.utcnow()
            else:
                new_embedding = VectorEmbedding(
                    embedding_id=embedding_id,
                    content_type="issue",
                    content_id=issue.issue_id,
                    project_id=issue.project_id,
                    title=issue.title,
                    content_text=text_content,
                    metadata=metadata
                )
                db.add(new_embedding)
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error embedding issue {issue.issue_id}: {str(e)}")
            return False
    
    def embed_jira_task(self, db: Session, task: JiraTask) -> bool:
        """Create and store embedding for a Jira Task"""
        try:
            text_content = f"""
            Summary: {task.summary}
            Issue ID: {task.issue_id}
            Description: {task.description or 'No description'}
            Type: {task.issue_type}
            Assignee: {task.assignee_id or 'Unassigned'}
            Status: {task.status}
            Priority: {task.priority}
            Story Points: {task.story_points or 'Not set'}
            Labels: {', '.join(task.labels) if task.labels else 'None'}
            Parent: {task.parent_issue_id or 'None'}
            Dependencies: {', '.join(task.depends_on) if task.depends_on else 'None'}
            Created: {task.created_date}
            Associated PR: {task.github_pr_id or 'None'}
            """
            
            embedding = self.generate_embedding(text_content)
            
            self.jira_collection.upsert(
                ids=[task.issue_id],
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[{
                    "issue_id": task.issue_id,
                    "project_id": task.project_id,
                    "assignee_id": task.assignee_id or "",
                    "status": task.status,
                    "priority": task.priority,
                    "type": "jira_task"
                }]
            )
            
            embedding_id = f"EMB-JIRA-{task.issue_id}"
            existing = db.query(VectorEmbedding).filter(
                VectorEmbedding.embedding_id == embedding_id
            ).first()
            
            metadata = {
                "issue_id": task.issue_id,
                "assignee_id": task.assignee_id,
                "status": task.status,
                "issue_type": task.issue_type,
                "priority": task.priority,
                "story_points": task.story_points,
                "labels": task.labels,
                "parent": task.parent_issue_id,
                "dependencies": task.depends_on
            }
            
            if existing:
                existing.title = task.summary
                existing.content_text = text_content
                existing.metadata = metadata
                existing.updated_at = datetime.utcnow()
            else:
                new_embedding = VectorEmbedding(
                    embedding_id=embedding_id,
                    content_type="jira_task",
                    content_id=task.issue_id,
                    project_id=task.project_id,
                    title=task.summary,
                    content_text=text_content,
                    metadata=metadata
                )
                db.add(new_embedding)
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error embedding Jira task {task.issue_id}: {str(e)}")
            return False
    
    def embed_comment(self, db: Session, comment, content_type: str) -> bool:
        """Create and store embedding for a comment (GitHub or Jira)"""
        try:
            # Handle both GitHub and Jira comments
            if content_type == "github":
                comment_id = comment.comment_id
                author_id = comment.author_id
                body = comment.body
                parent_id = comment.pr_id or comment.issue_id
                parent_type = "PR" if comment.pr_id else "Issue"
            else:  # jira
                comment_id = comment.comment_id
                author_id = comment.author_id
                body = comment.body
                parent_id = comment.issue_id
                parent_type = "Jira Task"
            
            text_content = f"""
            Comment ID: {comment_id}
            Parent: {parent_type} - {parent_id}
            Author: {author_id or 'Unknown'}
            Content: {body}
            Created: {comment.created_at}
            """
            
            embedding = self.generate_embedding(text_content)
            
            self.comment_collection.upsert(
                ids=[comment_id],
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[{
                    "comment_id": comment_id,
                    "author_id": author_id or "",
                    "parent_id": parent_id or "",
                    "parent_type": parent_type,
                    "type": "comment"
                }]
            )
            
            embedding_id = f"EMB-COMM-{comment_id}"
            existing = db.query(VectorEmbedding).filter(
                VectorEmbedding.embedding_id == embedding_id
            ).first()
            
            metadata = {
                "comment_id": comment_id,
                "author_id": author_id,
                "parent_id": parent_id,
                "parent_type": parent_type,
                "content_type": content_type
            }
            
            if existing:
                existing.content_text = text_content
                existing.metadata = metadata
                existing.updated_at = datetime.utcnow()
            else:
                new_embedding = VectorEmbedding(
                    embedding_id=embedding_id,
                    content_type="comment",
                    content_id=comment_id,
                    project_id=None,  # Comments don't have direct project association
                    title=f"Comment on {parent_type}",
                    content_text=text_content,
                    metadata=metadata
                )
                db.add(new_embedding)
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"Error embedding comment: {str(e)}")
            return False
    
    def semantic_search(
        self,
        query: str,
        content_types: List[str] = None,
        project_ids: List[str] = None,
        n_results: int = 10,
        min_similarity_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Perform semantic search across all content
        
        Args:
            query: Search query text
            content_types: Types of content to search (pr, issue, jira_task, comment)
            project_ids: Filter by specific project IDs
            n_results: Maximum number of results to return
            min_similarity_score: Minimum similarity score threshold (0.0 to 1.0).
                                 Default is 0.3 (30%) to filter out less relevant items.
        
        Returns:
            List of relevant items with similarity scores above threshold
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            results = []
            collections = []
            
            # Determine which collections to search
            if not content_types:
                content_types = ["pr", "issue", "jira_task", "comment"]
            
            if "pr" in content_types:
                collections.append(("pr", self.pr_collection))
            if "issue" in content_types:
                collections.append(("issue", self.issue_collection))
            if "jira_task" in content_types:
                collections.append(("jira_task", self.jira_collection))
            if "comment" in content_types:
                collections.append(("comment", self.comment_collection))
            
            # Search each collection
            for content_type, collection in collections:
                try:
                    search_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    # Process results
                    if search_results and search_results['ids']:
                        for i, doc_id in enumerate(search_results['ids'][0]):
                            # Convert distance to similarity score (1 - normalized_distance)
                            # ChromaDB uses L2 distance, smaller is better
                            distance = search_results['distances'][0][i]
                            similarity_score = 1.0 / (1.0 + distance)  # Convert to similarity
                            
                            # Filter by minimum similarity score
                            if similarity_score < min_similarity_score:
                                continue
                            
                            result = {
                                "id": doc_id,
                                "content_type": content_type,
                                "document": search_results['documents'][0][i],
                                "metadata": search_results['metadatas'][0][i],
                                "similarity_score": similarity_score
                            }
                            
                            # Filter by project if specified
                            if project_ids:
                                if result['metadata'].get('project_id') in project_ids:
                                    results.append(result)
                            else:
                                results.append(result)
                                
                except Exception as e:
                    print(f"Error searching {content_type} collection: {str(e)}")
            
            # Sort by similarity score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return results[:n_results]
            
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return []
    
    def embed_all_data(self, db: Session) -> Dict[str, int]:
        """Embed all existing data in the database"""
        stats = {
            "prs": 0,
            "issues": 0,
            "jira_tasks": 0,
            "github_comments": 0,
            "jira_comments": 0,
            "errors": 0
        }
        
        try:
            # Embed all GitHub PRs
            prs = db.query(GitHubActivity).all()
            for pr in prs:
                if self.embed_github_pr(db, pr):
                    stats["prs"] += 1
                else:
                    stats["errors"] += 1
            
            # Embed all GitHub Issues
            issues = db.query(GitHubIssue).all()
            for issue in issues:
                if self.embed_github_issue(db, issue):
                    stats["issues"] += 1
                else:
                    stats["errors"] += 1
            
            # Embed all Jira Tasks
            tasks = db.query(JiraTask).all()
            for task in tasks:
                if self.embed_jira_task(db, task):
                    stats["jira_tasks"] += 1
                else:
                    stats["errors"] += 1
            
            # Embed all GitHub Comments
            gh_comments = db.query(GitHubComment).all()
            for comment in gh_comments:
                if self.embed_comment(db, comment, "github"):
                    stats["github_comments"] += 1
                else:
                    stats["errors"] += 1
            
            # Embed all Jira Comments
            jira_comments = db.query(JiraComment).all()
            for comment in jira_comments:
                if self.embed_comment(db, comment, "jira"):
                    stats["jira_comments"] += 1
                else:
                    stats["errors"] += 1
            
            print(f"✓ Embedded all data: {stats}")
            
        except Exception as e:
            print(f"Error embedding all data: {str(e)}")
        
        return stats


# Global instance
_vector_service: Optional[VectorDatabaseService] = None


def get_vector_service() -> VectorDatabaseService:
    """Get or create vector service instance"""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorDatabaseService()
    return _vector_service
