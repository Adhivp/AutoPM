"""
Enhanced Sync Service - High-performance sync with comprehensive data capture
Includes comments, assignees, reactions, and parallel processing for speed
"""
from config import settings
from typing import List, Dict, Any, Optional
from datetime import datetime
from github import Github, GithubException
import requests
from sqlalchemy.orm import Session
from models.database_models import (
    ProjectMetadata, JiraTask, GitHubActivity, EmployeeProfile, GitHubIssue,
    GitHubComment, JiraComment, SyncLog
)
from utils.encryption import decrypt_token
import concurrent.futures
import asyncio
from functools import partial
from services.vector_service import get_vector_service


class EnhancedGitHubSyncService:
    """Enhanced service to sync comprehensive data from GitHub API"""
    
    def __init__(self, token: str):
        self.gh = Github(token, per_page=100)  # Increase page size for performance
        self.user = self.gh.get_user()
    
    def sync_pull_requests_with_details(self, db: Session, project: ProjectMetadata) -> Dict[str, int]:
        """Sync pull requests with all details including comments"""
        if not project.github_repo_name:
            return {'prs': 0, 'comments': 0}
        
        log_entry = SyncLog(
            sync_type='github_pr',
            project_id=project.project_id,
            status='started',
            started_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        
        synced_prs = 0
        synced_comments = 0
        
        try:
            # Support full repo name (owner/repo) or just repo name
            if '/' in project.github_repo_name:
                repo_full_name = project.github_repo_name
            else:
                repo_full_name = f"{self.user.login}/{project.github_repo_name}"
            repo = self.gh.get_repo(repo_full_name)
            
            # Fetch pull requests with pagination
            prs = repo.get_pulls(state='all', sort='updated', direction='desc')
            
            for pr in prs[:100]:  # Increased limit
                try:
                    # Map GitHub username to employee_id
                    author_username = pr.user.login if pr.user else None
                    author = db.query(EmployeeProfile).filter(
                        EmployeeProfile.github_username == author_username
                    ).first() if author_username else None
                    
                    # Get reviewers
                    reviewers = []
                    try:
                        requested_reviewers = pr.get_review_requests()[0]
                        for reviewer in requested_reviewers:
                            emp = db.query(EmployeeProfile).filter(
                                EmployeeProfile.github_username == reviewer.login
                            ).first()
                            if emp:
                                reviewers.append(emp.employee_id)
                        
                        # Also get actual reviews
                        reviews = pr.get_reviews()
                        for review in reviews:
                            if review.user:
                                emp = db.query(EmployeeProfile).filter(
                                    EmployeeProfile.github_username == review.user.login
                                ).first()
                                if emp and emp.employee_id not in reviewers:
                                    reviewers.append(emp.employee_id)
                    except Exception as e:
                        print(f"Error fetching reviewers for PR #{pr.number}: {str(e)}")
                    
                    # Determine PR status
                    if pr.merged:
                        status = "Merged"
                    elif pr.state == "closed":
                        status = "Closed"
                    else:
                        status = "Open"
                    
                    # Extract Jira issue ID
                    associated_issue_id = self._extract_jira_issue_id(pr.title, pr.body)
                    
                    # Check build status
                    build_status = "Pending"
                    try:
                        commit = repo.get_commit(pr.head.sha)
                        statuses = commit.get_statuses()
                        if statuses.totalCount > 0:
                            latest_status = statuses[0].state
                            if latest_status == "success":
                                build_status = "Success"
                            elif latest_status == "failure":
                                build_status = "Failed"
                    except Exception as e:
                        print(f"Error fetching build status for PR #{pr.number}: {str(e)}")
                    
                    # Create or update GitHub activity
                    pr_id = f"{project.github_repo_name}/PR#{pr.number}"
                    existing = db.query(GitHubActivity).filter(
                        GitHubActivity.pr_id == pr_id
                    ).first()
                    
                    if existing:
                        # Update existing
                        existing.title = pr.title
                        existing.author_id = author.employee_id if author else None
                        existing.reviewers = reviewers
                        existing.status = status
                        existing.associated_issue_id = associated_issue_id
                        existing.changed_files = pr.changed_files
                        existing.additions = pr.additions
                        existing.deletions = pr.deletions
                        existing.comments_count = pr.comments
                        existing.build_status = build_status
                        existing.merged_at = pr.merged_at
                        existing.closed_at = pr.closed_at
                        existing.last_synced_at = datetime.utcnow()
                    else:
                        # Create new
                        new_activity = GitHubActivity(
                            pr_id=pr_id,
                            project_id=project.project_id,
                            title=pr.title,
                            author_id=author.employee_id if author else None,
                            reviewers=reviewers,
                            created_at=pr.created_at,
                            merged_at=pr.merged_at,
                            closed_at=pr.closed_at,
                            status=status,
                            associated_issue_id=associated_issue_id,
                            changed_files=pr.changed_files,
                            additions=pr.additions,
                            deletions=pr.deletions,
                            comments_count=pr.comments,
                            build_status=build_status,
                            last_synced_at=datetime.utcnow()
                        )
                        db.add(new_activity)
                    
                    synced_prs += 1
                    
                    # Embed PR in vector database
                    try:
                        vector_service = get_vector_service()
                        if existing:
                            vector_service.embed_github_pr(db, existing)
                        else:
                            # Need to get the newly created PR from DB
                            db.flush()
                            vector_service.embed_github_pr(db, new_activity)
                    except Exception as e:
                        print(f"Error embedding PR: {str(e)}")
                    
                    # Sync PR comments
                    comment_count = self._sync_pr_comments(db, pr, pr_id)
                    synced_comments += comment_count
                    
                    # Link to Jira if found
                    if associated_issue_id:
                        try:
                            jira_task = db.query(JiraTask).filter(
                                JiraTask.issue_id == associated_issue_id
                            ).first()
                            if jira_task:
                                jira_task.github_pr_id = pr_id
                                db.add(jira_task)
                        except Exception:
                            pass
                    
                except Exception as e:
                    print(f"Error syncing PR #{pr.number}: {str(e)}")
                    continue
            
            db.commit()
            
            # Update log entry
            log_entry.status = 'completed'
            log_entry.items_synced = synced_prs
            log_entry.completed_at = datetime.utcnow()
            log_entry.duration_seconds = (log_entry.completed_at - log_entry.started_at).total_seconds()
            db.commit()
            
        except GithubException as e:
            log_entry.status = 'failed'
            log_entry.error_message = f"GitHub API error: {str(e)}"
            log_entry.completed_at = datetime.utcnow()
            db.commit()
            print(f"GitHub API error for {project.github_repo_name}: {str(e)}")
            return {'prs': 0, 'comments': 0}
        except Exception as e:
            log_entry.status = 'failed'
            log_entry.error_message = str(e)
            log_entry.completed_at = datetime.utcnow()
            db.commit()
            print(f"Error syncing GitHub PRs: {str(e)}")
            return {'prs': 0, 'comments': 0}
        
        return {'prs': synced_prs, 'comments': synced_comments}
    
    def _sync_pr_comments(self, db: Session, pr, pr_id: str) -> int:
        """Sync comments for a pull request"""
        synced_count = 0
        try:
            comments = pr.get_comments()
            for comment in comments:
                try:
                    # Map comment author
                    author_username = comment.user.login if comment.user else None
                    author = db.query(EmployeeProfile).filter(
                        EmployeeProfile.github_username == author_username
                    ).first() if author_username else None
                    
                    # Get reactions
                    reactions = {}
                    try:
                        reaction_data = comment.get_reactions()
                        for reaction in reaction_data:
                            content = reaction.content
                            reactions[content] = reactions.get(content, 0) + 1
                    except:
                        pass
                    
                    comment_id = f"GH-C-{comment.id}"
                    existing = db.query(GitHubComment).filter(
                        GitHubComment.comment_id == comment_id
                    ).first()
                    
                    if existing:
                        existing.body = comment.body
                        existing.updated_at = comment.updated_at
                        existing.reactions = reactions
                        existing.last_synced_at = datetime.utcnow()
                    else:
                        new_comment = GitHubComment(
                            comment_id=comment_id,
                            pr_id=pr_id,
                            author_id=author.employee_id if author else None,
                            body=comment.body,
                            created_at=comment.created_at,
                            updated_at=comment.updated_at,
                            reactions=reactions,
                            last_synced_at=datetime.utcnow()
                        )
                        db.add(new_comment)
                    
                    synced_count += 1
                    
                    # Embed comment in vector database
                    try:
                        vector_service = get_vector_service()
                        if existing:
                            vector_service.embed_comment(db, existing, "github")
                        else:
                            db.flush()
                            vector_service.embed_comment(db, new_comment, "github")
                    except Exception as e:
                        print(f"Error embedding comment: {str(e)}")
                    
                except Exception as e:
                    print(f"Error syncing PR comment: {str(e)}")
                    continue
            
            # Also sync review comments
            review_comments = pr.get_review_comments()
            for comment in review_comments:
                try:
                    author_username = comment.user.login if comment.user else None
                    author = db.query(EmployeeProfile).filter(
                        EmployeeProfile.github_username == author_username
                    ).first() if author_username else None
                    
                    reactions = {}
                    try:
                        reaction_data = comment.get_reactions()
                        for reaction in reaction_data:
                            content = reaction.content
                            reactions[content] = reactions.get(content, 0) + 1
                    except:
                        pass
                    
                    comment_id = f"GH-RC-{comment.id}"
                    existing = db.query(GitHubComment).filter(
                        GitHubComment.comment_id == comment_id
                    ).first()
                    
                    if existing:
                        existing.body = comment.body
                        existing.updated_at = comment.updated_at
                        existing.reactions = reactions
                        existing.last_synced_at = datetime.utcnow()
                    else:
                        new_comment = GitHubComment(
                            comment_id=comment_id,
                            pr_id=pr_id,
                            author_id=author.employee_id if author else None,
                            body=comment.body,
                            created_at=comment.created_at,
                            updated_at=comment.updated_at,
                            reactions=reactions,
                            last_synced_at=datetime.utcnow()
                        )
                        db.add(new_comment)
                    
                    synced_count += 1
                except Exception as e:
                    print(f"Error syncing PR review comment: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching PR comments: {str(e)}")
        
        return synced_count
    
    def sync_issues_with_details(self, db: Session, project: ProjectMetadata) -> Dict[str, int]:
        """Sync GitHub issues with all details including comments"""
        if not project.github_repo_name:
            return {'issues': 0, 'comments': 0}
        
        log_entry = SyncLog(
            sync_type='github_issue',
            project_id=project.project_id,
            status='started',
            started_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        
        synced_issues = 0
        synced_comments = 0
        
        try:
            if '/' in project.github_repo_name:
                repo_full_name = project.github_repo_name
            else:
                repo_full_name = f"{self.user.login}/{project.github_repo_name}"
            repo = self.gh.get_repo(repo_full_name)
            
            issues = repo.get_issues(state='all', sort='updated', direction='desc')
            
            for issue in issues[:100]:
                # Skip pull requests
                if issue.pull_request:
                    continue
                    
                try:
                    # Map author
                    author_username = issue.user.login if issue.user else None
                    author = db.query(EmployeeProfile).filter(
                        EmployeeProfile.github_username == author_username
                    ).first() if author_username else None
                    
                    # Get assignees
                    assignees = []
                    for assignee in issue.assignees:
                        emp = db.query(EmployeeProfile).filter(
                            EmployeeProfile.github_username == assignee.login
                        ).first()
                        if emp:
                            assignees.append(emp.employee_id)
                    
                    # Determine status
                    status = "Open" if issue.state == "open" else "Closed"
                    
                    # Map labels
                    issue_type = "Bug"
                    priority = "Medium"
                    labels = []
                    
                    for label in issue.labels:
                        label_name = label.name.lower()
                        labels.append(label.name)
                        
                        if any(keyword in label_name for keyword in ['bug', 'fix', 'error']):
                            issue_type = "Bug"
                        elif any(keyword in label_name for keyword in ['feature', 'enhancement']):
                            issue_type = "Feature"
                        elif any(keyword in label_name for keyword in ['documentation', 'docs']):
                            issue_type = "Documentation"
                        
                        if any(keyword in label_name for keyword in ['critical', 'urgent', 'p0']):
                            priority = "Critical"
                        elif any(keyword in label_name for keyword in ['high', 'important', 'p1']):
                            priority = "High"
                        elif any(keyword in label_name for keyword in ['low', 'minor', 'p3']):
                            priority = "Low"
                    
                    # Create or update issue
                    issue_id = f"{project.github_repo_name}/Issue#{issue.number}"
                    existing = db.query(GitHubIssue).filter(
                        GitHubIssue.issue_id == issue_id
                    ).first()
                    
                    if existing:
                        existing.title = issue.title
                        existing.author_id = author.employee_id if author else None
                        existing.assignees = assignees
                        existing.status = status
                        existing.labels = labels
                        existing.issue_type = issue_type
                        existing.priority = priority
                        existing.comments_count = issue.comments
                        existing.closed_at = issue.closed_at
                        existing.last_synced_at = datetime.utcnow()
                    else:
                        new_issue = GitHubIssue(
                            issue_id=issue_id,
                            project_id=project.project_id,
                            title=issue.title,
                            author_id=author.employee_id if author else None,
                            assignees=assignees,
                            created_at=issue.created_at,
                            closed_at=issue.closed_at,
                            status=status,
                            labels=labels,
                            issue_type=issue_type,
                            priority=priority,
                            comments_count=issue.comments,
                            last_synced_at=datetime.utcnow()
                        )
                        db.add(new_issue)
                    
                    synced_issues += 1
                    
                    # Embed issue in vector database
                    try:
                        vector_service = get_vector_service()
                        if existing:
                            vector_service.embed_github_issue(db, existing)
                        else:
                            db.flush()
                            vector_service.embed_github_issue(db, new_issue)
                    except Exception as e:
                        print(f"Error embedding issue: {str(e)}")
                    
                    # Sync issue comments
                    comment_count = self._sync_issue_comments(db, issue, issue_id)
                    synced_comments += comment_count
                    
                except Exception as e:
                    print(f"Error syncing Issue #{issue.number}: {str(e)}")
                    continue
            
            db.commit()
            
            log_entry.status = 'completed'
            log_entry.items_synced = synced_issues
            log_entry.completed_at = datetime.utcnow()
            log_entry.duration_seconds = (log_entry.completed_at - log_entry.started_at).total_seconds()
            db.commit()
            
        except GithubException as e:
            log_entry.status = 'failed'
            log_entry.error_message = f"GitHub API error: {str(e)}"
            log_entry.completed_at = datetime.utcnow()
            db.commit()
            print(f"GitHub API error: {str(e)}")
            return {'issues': 0, 'comments': 0}
        except Exception as e:
            log_entry.status = 'failed'
            log_entry.error_message = str(e)
            log_entry.completed_at = datetime.utcnow()
            db.commit()
            print(f"Error syncing GitHub issues: {str(e)}")
            return {'issues': 0, 'comments': 0}
        
        return {'issues': synced_issues, 'comments': synced_comments}
    
    def _sync_issue_comments(self, db: Session, issue, issue_id: str) -> int:
        """Sync comments for an issue"""
        synced_count = 0
        try:
            comments = issue.get_comments()
            for comment in comments:
                try:
                    author_username = comment.user.login if comment.user else None
                    author = db.query(EmployeeProfile).filter(
                        EmployeeProfile.github_username == author_username
                    ).first() if author_username else None
                    
                    reactions = {}
                    try:
                        reaction_data = comment.get_reactions()
                        for reaction in reaction_data:
                            content = reaction.content
                            reactions[content] = reactions.get(content, 0) + 1
                    except:
                        pass
                    
                    comment_id = f"GH-IC-{comment.id}"
                    existing = db.query(GitHubComment).filter(
                        GitHubComment.comment_id == comment_id
                    ).first()
                    
                    if existing:
                        existing.body = comment.body
                        existing.updated_at = comment.updated_at
                        existing.reactions = reactions
                        existing.last_synced_at = datetime.utcnow()
                    else:
                        new_comment = GitHubComment(
                            comment_id=comment_id,
                            issue_id=issue_id,
                            author_id=author.employee_id if author else None,
                            body=comment.body,
                            created_at=comment.created_at,
                            updated_at=comment.updated_at,
                            reactions=reactions,
                            last_synced_at=datetime.utcnow()
                        )
                        db.add(new_comment)
                    
                    synced_count += 1
                except Exception as e:
                    print(f"Error syncing issue comment: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error fetching issue comments: {str(e)}")
        
        return synced_count
    
    def _extract_jira_issue_id(self, title: str, body: Optional[str]) -> Optional[str]:
        """Extract Jira issue ID from text"""
        import re
        pattern = r'\b([A-Z]+)-(\d+)\b'
        
        if title:
            match = re.search(pattern, title)
            if match:
                return match.group(0)
        
        if body:
            match = re.search(pattern, body)
            if match:
                return match.group(0)
        
        return None


class EnhancedJiraSyncService:
    """Enhanced service to sync comprehensive data from Jira API"""
    
    def __init__(self, url: str, email: str, api_token: str):
        self.url = url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def sync_issues_with_details(self, db: Session, project: ProjectMetadata) -> Dict[str, int]:
        """Sync Jira issues with all details including comments"""
        if not project.jira_project_key:
            return {'issues': 0, 'comments': 0}
        
        log_entry = SyncLog(
            sync_type='jira_issue',
            project_id=project.project_id,
            status='started',
            started_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        
        synced_issues = 0
        synced_comments = 0
        
        try:
            jql = f"project = {project.jira_project_key} ORDER BY updated DESC"
            next_page_token = None
            max_results = 100  # Increased batch size
            
            while True:
                # Use POST with JSON body for Jira Cloud v3 API - /search/jql endpoint (enhanced search)
                payload = {
                    'jql': jql,
                    'maxResults': max_results,
                    'fields': ['summary', 'description', 'issuetype', 'assignee', 'status', 
                              'priority', 'created', 'updated', 'resolutiondate', 'parent', 
                              'issuelinks', 'labels', 'customfield_10016', 'comment']
                }
                
                # Add nextPageToken for pagination (only if not first request)
                if next_page_token:
                    payload['nextPageToken'] = next_page_token
                
                endpoint_url = f"{self.url}/rest/api/3/search/jql"
                print(f"DEBUG: Making POST request to {endpoint_url}")
                
                response = self.session.post(
                    endpoint_url,
                    json=payload
                )
                
                if response.status_code != 200:
                    print(f"Jira API error: {response.status_code} - {response.text}")
                    break
                
                data = response.json()
                issues = data.get('issues', [])
                
                if not issues:
                    break
                
                for issue in issues:
                    try:
                        fields = issue.get('fields', {})
                        issue_key = issue.get('key')
                        
                        # Map assignee
                        assignee = None
                        if fields.get('assignee'):
                            jira_email = fields['assignee'].get('emailAddress')
                            assignee = db.query(EmployeeProfile).filter(
                                EmployeeProfile.jira_email == jira_email
                            ).first()
                        
                        story_points = fields.get('customfield_10016')
                        parent_issue_id = None
                        if fields.get('parent'):
                            parent_issue_id = fields['parent'].get('key')
                        
                        # Get dependencies
                        depends_on = []
                        for link in fields.get('issuelinks', []):
                            if link.get('type', {}).get('name') == 'Blocks':
                                if link.get('outwardIssue'):
                                    depends_on.append(link['outwardIssue'].get('key'))
                        
                        labels = fields.get('labels', [])
                        
                        jira_status = fields.get('status', {}).get('name', 'To Do')
                        status = self._map_jira_status(jira_status)
                        
                        jira_priority = fields.get('priority', {}).get('name', 'Medium')
                        priority = self._map_jira_priority(jira_priority)
                        
                        # Extract description text from ADF format
                        description_text = self._extract_text_from_adf(fields.get('description'))
                        
                        # Create or update Jira task
                        existing = db.query(JiraTask).filter(
                            JiraTask.issue_id == issue_key
                        ).first()
                        
                        if existing:
                            existing.summary = fields.get('summary')
                            existing.description = description_text
                            existing.issue_type = fields.get('issuetype', {}).get('name')
                            existing.assignee_id = assignee.employee_id if assignee else None
                            existing.status = status
                            existing.priority = priority
                            existing.story_points = story_points
                            existing.updated_date = self._parse_jira_date(fields.get('updated'))
                            existing.resolved_date = self._parse_jira_date(fields.get('resolutiondate'))
                            existing.parent_issue_id = parent_issue_id
                            existing.depends_on = depends_on
                            existing.labels = labels
                            existing.last_synced_at = datetime.utcnow()
                        else:
                            new_task = JiraTask(
                                issue_id=issue_key,
                                project_id=project.project_id,
                                summary=fields.get('summary'),
                                description=description_text,
                                issue_type=fields.get('issuetype', {}).get('name'),
                                assignee_id=assignee.employee_id if assignee else None,
                                status=status,
                                priority=priority,
                                story_points=story_points,
                                created_date=self._parse_jira_date(fields.get('created')),
                                updated_date=self._parse_jira_date(fields.get('updated')),
                                resolved_date=self._parse_jira_date(fields.get('resolutiondate')),
                                parent_issue_id=parent_issue_id,
                                depends_on=depends_on,
                                labels=labels,
                                last_synced_at=datetime.utcnow()
                            )
                            db.add(new_task)
                        
                        synced_issues += 1
                        
                        # Embed Jira task in vector database
                        try:
                            vector_service = get_vector_service()
                            if existing:
                                vector_service.embed_jira_task(db, existing)
                            else:
                                db.flush()
                                vector_service.embed_jira_task(db, new_task)
                        except Exception as e:
                            print(f"Error embedding Jira task: {str(e)}")
                        
                        # Sync comments
                        comment_data = fields.get('comment', {})
                        if comment_data and comment_data.get('comments'):
                            comment_count = self._sync_jira_comments(
                                db, issue_key, comment_data['comments']
                            )
                            synced_comments += comment_count
                        
                    except Exception as e:
                        print(f"Error syncing Jira issue {issue.get('key')}: {str(e)}")
                        continue
                
                db.commit()
                
                # Check if there are more pages using the new pagination token system
                # The response includes 'isLast' boolean to indicate if this is the last page
                if data.get('isLast', True):
                    break
                
                # Get the next page token for the next iteration
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
            
            log_entry.status = 'completed'
            log_entry.items_synced = synced_issues
            log_entry.completed_at = datetime.utcnow()
            log_entry.duration_seconds = (log_entry.completed_at - log_entry.started_at).total_seconds()
            db.commit()
            
        except Exception as e:
            log_entry.status = 'failed'
            log_entry.error_message = str(e)
            log_entry.completed_at = datetime.utcnow()
            db.commit()
            print(f"Error syncing Jira data: {str(e)}")
            return {'issues': 0, 'comments': 0}
        
        return {'issues': synced_issues, 'comments': synced_comments}
    
    def _sync_jira_comments(self, db: Session, issue_key: str, comments: List[Dict]) -> int:
        """Sync comments for a Jira issue"""
        synced_count = 0
        
        for comment in comments:
            try:
                comment_id = f"JIRA-C-{comment.get('id')}"
                
                # Map author
                author = None
                author_data = comment.get('author', {})
                if author_data.get('emailAddress'):
                    author = db.query(EmployeeProfile).filter(
                        EmployeeProfile.jira_email == author_data['emailAddress']
                    ).first()
                
                existing = db.query(JiraComment).filter(
                    JiraComment.comment_id == comment_id
                ).first()
                
                # Extract text from ADF body (Jira returns ADF format as dict)
                body_text = self._extract_text_from_adf(comment.get('body'))
                
                if existing:
                    existing.body = body_text
                    existing.updated_at = self._parse_jira_date(comment.get('updated'))
                    existing.last_synced_at = datetime.utcnow()
                else:
                    new_comment = JiraComment(
                        comment_id=comment_id,
                        issue_id=issue_key,
                        author_id=author.employee_id if author else None,
                        body=body_text,
                        created_at=self._parse_jira_date(comment.get('created')),
                        updated_at=self._parse_jira_date(comment.get('updated')),
                        last_synced_at=datetime.utcnow()
                    )
                    db.add(new_comment)
                
                # Flush to database to ensure comment is saved
                db.flush()
                synced_count += 1
                
                # Embed comment in vector database
                try:
                    vector_service = get_vector_service()
                    if existing:
                        vector_service.embed_comment(db, existing, "jira")
                    else:
                        vector_service.embed_comment(db, new_comment, "jira")
                except Exception as e:
                    print(f"Error embedding Jira comment: {str(e)}")
                
            except Exception as e:
                print(f"Error syncing Jira comment: {str(e)}")
                # Rollback the current transaction to recover from error
                db.rollback()
                continue
        
        return synced_count
    
    def _map_jira_status(self, jira_status: str) -> str:
        """Map Jira status to schema"""
        status_mapping = {
            'To Do': 'To Do',
            'In Progress': 'In Progress',
            'In Review': 'In Review',
            'Done': 'Done',
            'Closed': 'Done',
            'Resolved': 'Done',
            'Open': 'To Do'
        }
        return status_mapping.get(jira_status, 'To Do')
    
    def _map_jira_priority(self, jira_priority: str) -> str:
        """Map Jira priority to schema"""
        priority_mapping = {
            'Highest': 'Critical',
            'High': 'High',
            'Medium': 'Medium',
            'Low': 'Low',
            'Lowest': 'Low'
        }
        return priority_mapping.get(jira_priority, 'Medium')
    
    def _parse_jira_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Jira date string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('+0000', '+00:00'))
        except:
            return None
    
    def _extract_text_from_adf(self, adf_content) -> Optional[str]:
        """Extract plain text from Atlassian Document Format (ADF)"""
        if not adf_content:
            return None
        
        # If it's already a string, return it
        if isinstance(adf_content, str):
            return adf_content
        
        # If it's a dict (ADF JSON), extract text from content
        if isinstance(adf_content, dict):
            import json
            
            def extract_text(node):
                """Recursively extract text from ADF nodes"""
                texts = []
                
                if isinstance(node, dict):
                    # If node has text, add it
                    if 'text' in node:
                        texts.append(node['text'])
                    
                    # Recursively process content array
                    if 'content' in node and isinstance(node['content'], list):
                        for child in node['content']:
                            texts.extend(extract_text(child))
                
                elif isinstance(node, list):
                    for item in node:
                        texts.extend(extract_text(item))
                
                return texts
            
            # Extract all text and join with spaces
            all_texts = extract_text(adf_content)
            return ' '.join(all_texts).strip() if all_texts else None
        
        return None


def sync_project_parallel(project: ProjectMetadata, github_service, jira_service) -> Dict[str, Any]:
    """Sync a single project (GitHub and Jira) - designed for parallel execution"""
    from database import SessionLocal
    
    db = SessionLocal()
    result = {
        'project_id': project.project_id,
        'github_prs': 0,
        'github_issues': 0,
        'github_comments': 0,
        'jira_issues': 0,
        'jira_comments': 0,
        'errors': []
    }
    
    try:
        # Sync GitHub PRs
        if project.github_repo_name:
            try:
                pr_result = github_service.sync_pull_requests_with_details(db, project)
                result['github_prs'] = pr_result.get('prs', 0)
                result['github_comments'] += pr_result.get('comments', 0)
            except Exception as e:
                result['errors'].append(f"GitHub PR sync error: {str(e)}")
            
            # Sync GitHub Issues
            try:
                issue_result = github_service.sync_issues_with_details(db, project)
                result['github_issues'] = issue_result.get('issues', 0)
                result['github_comments'] += issue_result.get('comments', 0)
            except Exception as e:
                result['errors'].append(f"GitHub issue sync error: {str(e)}")
        
        # Sync Jira
        if project.jira_project_key:
            try:
                jira_result = jira_service.sync_issues_with_details(db, project)
                result['jira_issues'] = jira_result.get('issues', 0)
                result['jira_comments'] = jira_result.get('comments', 0)
            except Exception as e:
                result['errors'].append(f"Jira sync error: {str(e)}")
    
    finally:
        db.close()
    
    return result


def sync_all_projects_parallel(db: Session, max_workers: int = 5) -> Dict[str, Any]:
    """
    Sync all projects in parallel for improved performance
    """
    # Get credentials
    github_token = settings.GITHUB_TOKEN
    jira_url = settings.JIRA_URL
    jira_email = settings.JIRA_EMAIL
    jira_token = settings.JIRA_API_TOKEN
    
    if not all([github_token, jira_url, jira_email, jira_token]):
        return {
            'status': 'error',
            'message': 'Missing GitHub or Jira credentials',
            'timestamp': datetime.utcnow().isoformat(),
            'projects_synced': 0,
            'github_prs_synced': 0,
            'github_issues_synced': 0,
            'github_comments_synced': 0,
            'jira_issues_synced': 0,
            'jira_comments_synced': 0,
            'errors': ['Missing credentials']
        }
    
    # Initialize services
    github_service = EnhancedGitHubSyncService(github_token)
    jira_service = EnhancedJiraSyncService(jira_url, jira_email, jira_token)
    
    # Get all projects
    projects = db.query(ProjectMetadata).all()
    
    results = {
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'projects_synced': 0,
        'github_prs_synced': 0,
        'github_issues_synced': 0,
        'github_comments_synced': 0,
        'jira_issues_synced': 0,
        'jira_comments_synced': 0,
        'errors': [],
        'duration_seconds': 0
    }
    
    start_time = datetime.utcnow()
    
    # Use ThreadPoolExecutor for parallel execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all projects for parallel processing
        future_to_project = {
            executor.submit(sync_project_parallel, project, github_service, jira_service): project
            for project in projects
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_project):
            project = future_to_project[future]
            try:
                result = future.result()
                results['projects_synced'] += 1
                results['github_prs_synced'] += result.get('github_prs', 0)
                results['github_issues_synced'] += result.get('github_issues', 0)
                results['github_comments_synced'] += result.get('github_comments', 0)
                results['jira_issues_synced'] += result.get('jira_issues', 0)
                results['jira_comments_synced'] += result.get('jira_comments', 0)
                results['errors'].extend(result.get('errors', []))
                
                print(f"✓ Synced {project.project_id}: "
                      f"{result['github_prs']} PRs, "
                      f"{result['github_issues']} issues, "
                      f"{result['jira_issues']} Jira tasks")
            except Exception as e:
                error_msg = f"Error syncing project {project.project_id}: {str(e)}"
                print(f"✗ {error_msg}")
                results['errors'].append(error_msg)
    
    end_time = datetime.utcnow()
    results['duration_seconds'] = (end_time - start_time).total_seconds()
    
    return results
