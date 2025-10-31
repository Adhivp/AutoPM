"""
Sync Service - Fetch data from GitHub and Jira APIs
Background task to sync every 1 minute
"""
from config import settings
from typing import List, Dict, Any, Optional
from datetime import datetime
from github import Github, GithubException
import requests
from sqlalchemy.orm import Session
from models.database_models import (
    ProjectMetadata, JiraTask, GitHubActivity, EmployeeProfile, GitHubIssue
)
from utils.encryption import decrypt_token


class GitHubSyncService:
    """Service to sync data from GitHub API"""
    
    def __init__(self, token: str):
        self.gh = Github(token)
        self.user = self.gh.get_user()
    
    def sync_pull_requests(self, db: Session, project: ProjectMetadata) -> int:
        """Sync pull requests for a given project"""
        if not project.github_repo_name:
            return 0
        
        synced_count = 0
        try:
            # Support full repo name (owner/repo) or just repo name (assume current user)
            if '/' in project.github_repo_name:
                repo_full_name = project.github_repo_name
            else:
                repo_full_name = f"{self.user.login}/{project.github_repo_name}"
            repo = self.gh.get_repo(repo_full_name)
            
            # Fetch all pull requests (open, closed, merged)
            prs = repo.get_pulls(state='all', sort='updated', direction='desc')
            
            for pr in prs[:50]:  # Limit to last 50 PRs for performance
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
                    except:
                        pass
                    
                    # Determine PR status
                    if pr.merged:
                        status = "Merged"
                    elif pr.state == "closed":
                        status = "Closed"
                    else:
                        status = "Open"
                    
                    # Extract Jira issue ID from PR title or body
                    associated_issue_id = self._extract_jira_issue_id(pr.title, pr.body)
                    # If no explicit issue id found, attempt a heuristic match against Jira tasks
                    if not associated_issue_id:
                        try:
                            candidate = self._find_similar_jira_task(db, project, pr.title, pr.body)
                            if candidate:
                                associated_issue_id = candidate
                        except Exception:
                            associated_issue_id = None
                    
                    # Check build status from status checks
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
                    except:
                        pass
                    
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
                    # If we found an associated Jira issue, link it back to the JiraTask record
                    if associated_issue_id:
                        try:
                            jira_task = db.query(JiraTask).filter(JiraTask.issue_id == associated_issue_id).first()
                            if jira_task:
                                jira_task.github_pr_id = pr_id
                                db.add(jira_task)
                        except Exception:
                            pass
                    
                    synced_count += 1
                    
                except Exception as e:
                    print(f"Error syncing PR #{pr.number}: {str(e)}")
                    continue
            
            db.commit()
            
        except GithubException as e:
            print(f"GitHub API error for {project.github_repo_name}: {str(e)}")
            return 0
        except Exception as e:
            print(f"Error syncing GitHub data: {str(e)}")
            return 0
        
        return synced_count
    
    def sync_issues(self, db: Session, project: ProjectMetadata) -> int:
        """Sync GitHub issues for a given project"""
        if not project.github_repo_name:
            return 0
        
        synced_count = 0
        try:
            # Support full repo name (owner/repo) or just repo name (assume current user)
            if '/' in project.github_repo_name:
                repo_full_name = project.github_repo_name
            else:
                repo_full_name = f"{self.user.login}/{project.github_repo_name}"
            repo = self.gh.get_repo(repo_full_name)
            
            # Fetch all issues (open and closed, excluding PRs)
            issues = repo.get_issues(state='all', sort='updated', direction='desc')
            
            for issue in issues[:50]:  # Limit to last 50 issues for performance
                # Skip if it's a pull request
                if issue.pull_request:
                    continue
                    
                try:
                    # Map GitHub username to employee_id
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
                    
                    # Determine issue status
                    status = "Open" if issue.state == "open" else "Closed"
                    
                    # Map GitHub labels to issue type and priority
                    issue_type = "Bug"  # Default
                    priority = "Medium"  # Default
                    labels = []
                    
                    for label in issue.labels:
                        label_name = label.name.lower()
                        labels.append(label.name)
                        
                        # Map common label patterns to types
                        if any(keyword in label_name for keyword in ['bug', 'fix', 'error']):
                            issue_type = "Bug"
                        elif any(keyword in label_name for keyword in ['feature', 'enhancement']):
                            issue_type = "Feature"
                        elif any(keyword in label_name for keyword in ['documentation', 'docs']):
                            issue_type = "Documentation"
                        elif any(keyword in label_name for keyword in ['question', 'help']):
                            issue_type = "Question"
                        
                        # Map priority labels
                        if any(keyword in label_name for keyword in ['critical', 'urgent', 'p0']):
                            priority = "Critical"
                        elif any(keyword in label_name for keyword in ['high', 'important', 'p1']):
                            priority = "High"
                        elif any(keyword in label_name for keyword in ['low', 'minor', 'p3']):
                            priority = "Low"
                    
                    # Check if this issue is associated with a PR
                    associated_pr_id = None
                    try:
                        # Look for PRs that reference this issue
                        prs = repo.get_pulls(state='all')
                        for pr in prs:
                            if pr.body and f"#{issue.number}" in pr.body:
                                associated_pr_id = f"{project.github_repo_name}/PR#{pr.number}"
                                break
                            elif pr.title and f"#{issue.number}" in pr.title:
                                associated_pr_id = f"{project.github_repo_name}/PR#{pr.number}"
                                break
                    except:
                        pass
                    
                    # Create or update GitHub issue
                    issue_id = f"{project.github_repo_name}/Issue#{issue.number}"
                    existing = db.query(GitHubIssue).filter(
                        GitHubIssue.issue_id == issue_id
                    ).first()
                    
                    if existing:
                        # Update existing
                        existing.title = issue.title
                        existing.author_id = author.employee_id if author else None
                        existing.assignees = assignees
                        existing.status = status
                        existing.labels = labels
                        existing.issue_type = issue_type
                        existing.priority = priority
                        existing.associated_pr_id = associated_pr_id
                        existing.comments_count = issue.comments
                        existing.closed_at = issue.closed_at
                        existing.last_synced_at = datetime.utcnow()
                    else:
                        # Create new
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
                            associated_pr_id=associated_pr_id,
                            comments_count=issue.comments,
                            last_synced_at=datetime.utcnow()
                        )
                        db.add(new_issue)
                    
                    synced_count += 1
                    
                except Exception as e:
                    print(f"Error syncing Issue #{issue.number}: {str(e)}")
                    continue
            
            db.commit()
            
        except GithubException as e:
            print(f"GitHub API error for {project.github_repo_name}: {str(e)}")
            return 0
        except Exception as e:
            print(f"Error syncing GitHub issues: {str(e)}")
            return 0
        
        return synced_count
    
    def _extract_jira_issue_id(self, title: str, body: Optional[str]) -> Optional[str]:
        """Extract Jira issue ID from PR title or body"""
        import re
        
        # Common patterns: IFS-123, ADAS-456, VD-789
        pattern = r'\b([A-Z]+)-(\d+)\b'
        
        # Try title first
        if title:
            match = re.search(pattern, title)
            if match:
                return match.group(0)
        
        # Try body
        if body:
            match = re.search(pattern, body)
            if match:
                return match.group(0)
        
        return None

    def _find_similar_jira_task(self, db: Session, project: ProjectMetadata, title: str, body: Optional[str]) -> Optional[str]:
        """Attempt to find a Jira task in the project that likely matches the PR by text matching.

        Returns the Jira issue_id if a likely match is found, otherwise None.
        This is a heuristic and only used to avoid creating duplicate logical tasks across systems.
        """
        if not title and not body:
            return None

        text = (title or "") + "\n" + (body or "")
        text = text.lower()

        try:
            candidates = db.query(JiraTask).filter(JiraTask.project_id == project.project_id).all()
            for t in candidates:
                if not t.summary:
                    continue
                s = t.summary.lower()
                # If the PR title/body contains the Jira summary, consider it a match
                if s in text or any(word in text for word in s.split()[:5]):
                    return t.issue_id
        except Exception:
            return None

        return None


class JiraSyncService:
    """Service to sync data from Jira API"""
    
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
    
    def sync_issues(self, db: Session, project: ProjectMetadata) -> int:
        """Sync Jira issues for a given project"""
        if not project.jira_project_key:
            return 0
        
        synced_count = 0
        try:
            # Fetch all issues for the project using JQL
            jql = f"project = {project.jira_project_key} ORDER BY updated DESC"
            
            start_at = 0
            max_results = 50
            
            while True:
                response = self.session.get(
                    f"{self.url}/rest/api/3/search/jql",
                    params={
                        'jql': jql,
                        'startAt': start_at,
                        'maxResults': max_results,
                        'fields': 'summary,description,issuetype,assignee,status,priority,created,updated,resolutiondate,parent,issuelinks,labels,customfield_10016'
                    }
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
                        
                        # Map Jira assignee to employee_id
                        assignee = None
                        if fields.get('assignee'):
                            jira_email = fields['assignee'].get('emailAddress')
                            assignee = db.query(EmployeeProfile).filter(
                                EmployeeProfile.jira_email == jira_email
                            ).first()
                        
                        # Extract story points (customfield_10016 is typical for story points)
                        story_points = fields.get('customfield_10016')
                        
                        # Get parent issue
                        parent_issue_id = None
                        if fields.get('parent'):
                            parent_issue_id = fields['parent'].get('key')
                        
                        # Get dependencies from issue links
                        depends_on = []
                        for link in fields.get('issuelinks', []):
                            if link.get('type', {}).get('name') == 'Blocks':
                                if link.get('outwardIssue'):
                                    depends_on.append(link['outwardIssue'].get('key'))
                        
                        # Get labels
                        labels = fields.get('labels', [])
                        
                        # Map Jira status to our schema
                        jira_status = fields.get('status', {}).get('name', 'To Do')
                        status = self._map_jira_status(jira_status)
                        
                        # Map Jira priority
                        jira_priority = fields.get('priority', {}).get('name', 'Medium')
                        priority = self._map_jira_priority(jira_priority)
                        
                        # Create or update Jira task
                        existing = db.query(JiraTask).filter(
                            JiraTask.issue_id == issue_key
                        ).first()
                        
                        if existing:
                            # Update existing
                            existing.summary = fields.get('summary')
                            existing.description = fields.get('description')
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
                        # Try to find a matching GitHub PR and link it
                        try:
                            gh_match = db.query(GitHubActivity).filter(GitHubActivity.associated_issue_id == issue_key).first()
                            if gh_match:
                                existing.github_pr_id = gh_match.pr_id
                                db.add(existing)
                        except Exception:
                            pass
                        else:
                            # Create new
                            new_task = JiraTask(
                                issue_id=issue_key,
                                project_id=project.project_id,
                                summary=fields.get('summary'),
                                description=fields.get('description'),
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
                            # Try to find an existing GitHubActivity that references this issue and link it
                            try:
                                gh_match = db.query(GitHubActivity).filter(GitHubActivity.associated_issue_id == issue_key).first()
                                if gh_match:
                                    new_task.github_pr_id = gh_match.pr_id
                                    db.add(new_task)
                            except Exception:
                                pass
                        
                        synced_count += 1
                        
                    except Exception as e:
                        print(f"Error syncing Jira issue {issue.get('key')}: {str(e)}")
                        continue
                
                db.commit()
                
                # Check if there are more issues
                if start_at + max_results >= data.get('total', 0):
                    break
                
                start_at += max_results
            
        except Exception as e:
            print(f"Error syncing Jira data: {str(e)}")
            return 0
        
        return synced_count
    
    def _map_jira_status(self, jira_status: str) -> str:
        """Map Jira status to our schema"""
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
        """Map Jira priority to our schema"""
        priority_mapping = {
            'Highest': 'Critical',
            'High': 'High',
            'Medium': 'Medium',
            'Low': 'Low',
            'Lowest': 'Low'
        }
        return priority_mapping.get(jira_priority, 'Medium')
    
    def _parse_jira_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Jira date string to datetime"""
        if not date_str:
            return None
        try:
            # Jira returns ISO format: 2025-01-20T09:00:00.000+0000
            return datetime.fromisoformat(date_str.replace('+0000', '+00:00'))
        except:
            return None


def sync_all_projects(db: Session) -> Dict[str, Any]:
    """
    Sync all projects from GitHub and Jira
    Returns sync statistics
    """
    # Get credentials from config (reads .env via pydantic settings)
    github_token = settings.GITHUB_TOKEN
    jira_url = settings.JIRA_URL
    jira_email = settings.JIRA_EMAIL
    jira_token = settings.JIRA_API_TOKEN
    
    if not all([github_token, jira_url, jira_email, jira_token]):
        # Return a consistent result shape even on error so callers don't KeyError
        return {
            'status': 'error',
            'message': 'Missing GitHub or Jira credentials in environment',
            'timestamp': datetime.utcnow().isoformat(),
            'projects_synced': 0,
            'github_prs_synced': 0,
            'jira_issues_synced': 0,
            'errors': ['Missing GitHub or Jira credentials in environment']
        }
    
    # Initialize services
    github_service = GitHubSyncService(github_token)
    jira_service = JiraSyncService(jira_url, jira_email, jira_token)
    
    # Get all projects
    projects = db.query(ProjectMetadata).all()
    
    results = {
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'projects_synced': 0,
        'github_prs_synced': 0,
        'github_issues_synced': 0,
        'jira_issues_synced': 0,
        'errors': []
    }
    
    for project in projects:
        try:
            # Sync GitHub PRs
            if project.github_repo_name:
                github_pr_count = github_service.sync_pull_requests(db, project)
                results['github_prs_synced'] += github_pr_count
            
            # Sync GitHub issues
            if project.github_repo_name:
                github_issue_count = github_service.sync_issues(db, project)
                results['github_issues_synced'] += github_issue_count
            
            # Sync Jira issues
            if project.jira_project_key:
                jira_count = jira_service.sync_issues(db, project)
                results['jira_issues_synced'] += jira_count
            
            results['projects_synced'] += 1
            
        except Exception as e:
            error_msg = f"Error syncing project {project.project_id}: {str(e)}"
            print(error_msg)
            results['errors'].append(error_msg)
    
    return results
