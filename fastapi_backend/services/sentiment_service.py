"""
Sentiment Analysis Service
Analyzes sentiment of comments from GitHub and Jira to provide insights
about team morale and project sentiment by person and project
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models.database_models import (
    GitHubComment, JiraComment, EmployeeProfile, 
    ProjectMetadata, GitHubActivity, GitHubIssue, JiraTask
)
import re


class SentimentAnalyzer:
    """Simple rule-based sentiment analyzer"""
    
    # Sentiment keywords
    POSITIVE_WORDS = {
        'good', 'great', 'excellent', 'awesome', 'fantastic', 'perfect', 'nice',
        'helpful', 'thanks', 'thank', 'appreciate', 'love', 'amazing', 'brilliant',
        'wonderful', 'impressive', 'outstanding', 'superb', 'well done', 'congrats',
        'congratulations', 'lgtm', 'approved', 'agree', 'solid', 'clean', 'elegant',
        'efficient', 'optimized', 'improved', 'better', 'fixed', 'resolved', 'success',
        'working', 'done', 'complete', '👍', '🎉', '✅', '💯', '🚀', '⭐'
    }
    
    NEGATIVE_WORDS = {
        'bad', 'poor', 'terrible', 'awful', 'horrible', 'wrong', 'error', 'issue',
        'problem', 'bug', 'broken', 'failed', 'failure', 'crash', 'stuck', 'blocked',
        'blocker', 'delay', 'delayed', 'late', 'concern', 'worried', 'confusing',
        'confused', 'unclear', 'difficult', 'hard', 'complicated', 'mess', 'messy',
        'ugly', 'inefficient', 'slow', 'performance', 'critical', 'urgent', 'asap',
        'help', 'please fix', 'not working', 'doesnt work', "doesn't work", 
        '❌', '⚠️', '🚨', '😞', '😢', '💔'
    }
    
    NEUTRAL_WORDS = {
        'question', 'clarification', 'suggestion', 'consider', 'maybe', 'could',
        'would', 'should', 'might', 'wondering', 'think', 'thought', 'note',
        'comment', 'update', 'change', 'changed', 'modified', 'review', 'check'
    }
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a text
        Returns: {'score': float, 'label': str, 'confidence': float}
        score: -1.0 (very negative) to 1.0 (very positive)
        label: 'positive', 'negative', or 'neutral'
        """
        if not text:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        text_lower = text.lower()
        
        # Count sentiment words
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)
        neutral_count = sum(1 for word in self.NEUTRAL_WORDS if word in text_lower)
        
        # Calculate score
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.1}
        
        # Weight: positive=1, neutral=0, negative=-1
        raw_score = (positive_count - negative_count) / len(text.split())
        
        # Normalize to -1 to 1
        score = max(-1.0, min(1.0, raw_score * 10))
        
        # Determine label
        if score > 0.15:
            label = 'positive'
        elif score < -0.15:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Confidence based on number of sentiment words found
        confidence = min(1.0, total_sentiment_words / 5)
        
        return {
            'score': round(score, 3),
            'label': label,
            'confidence': round(confidence, 2)
        }


class SentimentService:
    """Service for analyzing sentiment across projects and team members"""
    
    def __init__(self):
        self.analyzer = SentimentAnalyzer()
    
    def analyze_project_sentiment(
        self, 
        db: Session, 
        project_id: Optional[str] = None,
        days_back: int = 90
    ) -> List[Dict]:
        """
        Analyze sentiment for all projects or a specific project
        Returns sentiment analysis per project
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get all projects or specific project
        if project_id:
            projects = db.query(ProjectMetadata).filter(
                ProjectMetadata.project_id == project_id
            ).all()
        else:
            projects = db.query(ProjectMetadata).all()
        
        results = []
        
        for project in projects:
            # Get GitHub comments for this project
            github_comments = db.query(GitHubComment).join(
                GitHubActivity, 
                or_(
                    GitHubComment.pr_id == GitHubActivity.pr_id,
                    False
                )
            ).filter(
                GitHubActivity.project_id == project.project_id,
                GitHubComment.created_at >= cutoff_date
            ).all()
            
            github_issue_comments = db.query(GitHubComment).join(
                GitHubIssue,
                or_(
                    GitHubComment.issue_id == GitHubIssue.issue_id,
                    False
                )
            ).filter(
                GitHubIssue.project_id == project.project_id,
                GitHubComment.created_at >= cutoff_date
            ).all()
            
            # Get Jira comments for this project
            jira_comments = db.query(JiraComment).join(
                JiraTask,
                JiraComment.issue_id == JiraTask.issue_id
            ).filter(
                JiraTask.project_id == project.project_id,
                JiraComment.created_at >= cutoff_date
            ).all()
            
            all_comments = list(github_comments) + list(github_issue_comments) + list(jira_comments)
            
            if not all_comments:
                results.append({
                    'project_id': project.project_id,
                    'project_name': project.project_name,
                    'total_comments': 0,
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'average_confidence': 0.0,
                    'comment_breakdown': []
                })
                continue
            
            # Analyze all comments
            sentiments = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for comment in all_comments:
                sentiment = self.analyzer.analyze_text(comment.body)
                sentiments.append(sentiment)
                
                if sentiment['label'] == 'positive':
                    positive_count += 1
                elif sentiment['label'] == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
            
            # Calculate averages
            avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
            avg_confidence = sum(s['confidence'] for s in sentiments) / len(sentiments)
            
            # Overall label
            if avg_score > 0.15:
                overall_label = 'positive'
            elif avg_score < -0.15:
                overall_label = 'negative'
            else:
                overall_label = 'neutral'
            
            results.append({
                'project_id': project.project_id,
                'project_name': project.project_name,
                'total_comments': len(all_comments),
                'sentiment_score': round(avg_score, 3),
                'sentiment_label': overall_label,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'positive_percentage': round((positive_count / len(all_comments)) * 100, 1),
                'negative_percentage': round((negative_count / len(all_comments)) * 100, 1),
                'neutral_percentage': round((neutral_count / len(all_comments)) * 100, 1),
                'average_confidence': round(avg_confidence, 2),
                'analysis_period_days': days_back
            })
        
        return results
    
    def analyze_employee_sentiment(
        self,
        db: Session,
        project_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        days_back: int = 90
    ) -> List[Dict]:
        """
        Analyze sentiment by employee across projects
        Returns sentiment analysis per employee
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Build query for comments
        github_comment_query = db.query(
            GitHubComment.author_id,
            GitHubComment.body,
            GitHubComment.created_at,
            GitHubActivity.project_id
        ).join(
            GitHubActivity,
            or_(
                GitHubComment.pr_id == GitHubActivity.pr_id,
                False
            )
        ).filter(GitHubComment.created_at >= cutoff_date)
        
        github_issue_comment_query = db.query(
            GitHubComment.author_id,
            GitHubComment.body,
            GitHubComment.created_at,
            GitHubIssue.project_id
        ).join(
            GitHubIssue,
            or_(
                GitHubComment.issue_id == GitHubIssue.issue_id,
                False
            )
        ).filter(GitHubComment.created_at >= cutoff_date)
        
        jira_comment_query = db.query(
            JiraComment.author_id,
            JiraComment.body,
            JiraComment.created_at,
            JiraTask.project_id
        ).join(
            JiraTask,
            JiraComment.issue_id == JiraTask.issue_id
        ).filter(JiraComment.created_at >= cutoff_date)
        
        # Apply filters
        if project_id:
            github_comment_query = github_comment_query.filter(
                GitHubActivity.project_id == project_id
            )
            github_issue_comment_query = github_issue_comment_query.filter(
                GitHubIssue.project_id == project_id
            )
            jira_comment_query = jira_comment_query.filter(
                JiraTask.project_id == project_id
            )
        
        if employee_id:
            github_comment_query = github_comment_query.filter(
                GitHubComment.author_id == employee_id
            )
            github_issue_comment_query = github_issue_comment_query.filter(
                GitHubComment.author_id == employee_id
            )
            jira_comment_query = jira_comment_query.filter(
                JiraComment.author_id == employee_id
            )
        
        # Fetch all comments
        all_comments_data = (
            github_comment_query.all() + 
            github_issue_comment_query.all() + 
            jira_comment_query.all()
        )
        
        # Group by employee
        employee_comments = {}
        for author_id, body, created_at, proj_id in all_comments_data:
            if not author_id:
                continue
            
            if author_id not in employee_comments:
                employee_comments[author_id] = []
            
            employee_comments[author_id].append({
                'body': body,
                'created_at': created_at,
                'project_id': proj_id
            })
        
        # Analyze sentiment for each employee
        results = []
        
        for emp_id, comments in employee_comments.items():
            # Get employee info
            employee = db.query(EmployeeProfile).filter(
                EmployeeProfile.employee_id == emp_id
            ).first()
            
            if not employee:
                continue
            
            # Analyze sentiments
            sentiments = []
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            project_sentiments = {}
            
            for comment in comments:
                sentiment = self.analyzer.analyze_text(comment['body'])
                sentiments.append(sentiment)
                
                if sentiment['label'] == 'positive':
                    positive_count += 1
                elif sentiment['label'] == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
                
                # Track by project
                proj = comment['project_id']
                if proj not in project_sentiments:
                    project_sentiments[proj] = []
                project_sentiments[proj].append(sentiment['score'])
            
            if not sentiments:
                continue
            
            # Calculate averages
            avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
            avg_confidence = sum(s['confidence'] for s in sentiments) / len(sentiments)
            
            # Overall label
            if avg_score > 0.15:
                overall_label = 'positive'
            elif avg_score < -0.15:
                overall_label = 'negative'
            else:
                overall_label = 'neutral'
            
            # Project breakdown
            project_breakdown = []
            for proj_id, scores in project_sentiments.items():
                proj = db.query(ProjectMetadata).filter(
                    ProjectMetadata.project_id == proj_id
                ).first()
                
                if proj:
                    project_breakdown.append({
                        'project_id': proj_id,
                        'project_name': proj.project_name,
                        'comment_count': len(scores),
                        'avg_sentiment': round(sum(scores) / len(scores), 3)
                    })
            
            results.append({
                'employee_id': emp_id,
                'employee_name': employee.name,
                'email': employee.email,
                'role': employee.role,
                'team': employee.team,
                'total_comments': len(comments),
                'sentiment_score': round(avg_score, 3),
                'sentiment_label': overall_label,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'positive_percentage': round((positive_count / len(comments)) * 100, 1),
                'negative_percentage': round((negative_count / len(comments)) * 100, 1),
                'neutral_percentage': round((neutral_count / len(comments)) * 100, 1),
                'average_confidence': round(avg_confidence, 2),
                'project_breakdown': project_breakdown,
                'analysis_period_days': days_back
            })
        
        # Sort by sentiment score (most positive first)
        results.sort(key=lambda x: x['sentiment_score'], reverse=True)
        
        return results
    
    def get_sentiment_trends(
        self,
        db: Session,
        project_id: str,
        days_back: int = 90
    ) -> Dict:
        """
        Get sentiment trends over time for a project
        Returns weekly sentiment data
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get all comments for the project
        github_comments = db.query(GitHubComment).join(
            GitHubActivity,
            or_(
                GitHubComment.pr_id == GitHubActivity.pr_id,
                False
            )
        ).filter(
            GitHubActivity.project_id == project_id,
            GitHubComment.created_at >= cutoff_date
        ).all()
        
        github_issue_comments = db.query(GitHubComment).join(
            GitHubIssue,
            or_(
                GitHubComment.issue_id == GitHubIssue.issue_id,
                False
            )
        ).filter(
            GitHubIssue.project_id == project_id,
            GitHubComment.created_at >= cutoff_date
        ).all()
        
        jira_comments = db.query(JiraComment).join(
            JiraTask,
            JiraComment.issue_id == JiraTask.issue_id
        ).filter(
            JiraTask.project_id == project_id,
            JiraComment.created_at >= cutoff_date
        ).all()
        
        all_comments = list(github_comments) + list(github_issue_comments) + list(jira_comments)
        
        # Group by week
        weekly_data = {}
        
        for comment in all_comments:
            # Get week start date (Monday)
            week_start = comment.created_at - timedelta(days=comment.created_at.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weekly_data:
                weekly_data[week_key] = []
            
            sentiment = self.analyzer.analyze_text(comment.body)
            weekly_data[week_key].append(sentiment)
        
        # Calculate weekly averages
        trend_data = []
        for week, sentiments in sorted(weekly_data.items()):
            if sentiments:
                avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
                positive = sum(1 for s in sentiments if s['label'] == 'positive')
                negative = sum(1 for s in sentiments if s['label'] == 'negative')
                neutral = sum(1 for s in sentiments if s['label'] == 'neutral')
                
                trend_data.append({
                    'week_start': week,
                    'avg_sentiment': round(avg_score, 3),
                    'comment_count': len(sentiments),
                    'positive_count': positive,
                    'negative_count': negative,
                    'neutral_count': neutral
                })
        
        return {
            'project_id': project_id,
            'trends': trend_data,
            'period_days': days_back
        }


# Singleton instance
_sentiment_service = None

def get_sentiment_service() -> SentimentService:
    """Get or create the sentiment service singleton"""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SentimentService()
    return _sentiment_service
