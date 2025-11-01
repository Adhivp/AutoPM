# Fake Data Generator Setup Guide

This guide will walk you through setting up and running the fake data generator script for GitHub and Jira.

## Prerequisites

1. **GitHub Account** with permissions to create repositories
2. **Jira Account** (Atlassian Cloud or Server)
3. **Python 3.8+** installed on your system

## Step 1: Install Required Python Packages

Activate your virtual environment and install the dependencies:

```bash
# Activate the virtual environment
source autopm_venv/bin/activate  # On macOS/Linux
# OR
autopm_venv\Scripts\activate     # On Windows

# Install required packages
pip install -r fake_data_requirements.txt
```

## Step 2: Generate GitHub Personal Access Token

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name: "AutoPM Fake Data Generator"
4. Set expiration (recommend 90 days for testing)
5. Select the following scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `user` (Read and write user data)
   - ✅ `project` (Read and write project data)
   - ✅ `delete_repo` (Delete repositories - optional, for cleanup)
6. Click "Generate token"
7. **IMPORTANT**: Copy the token immediately (you won't see it again!)

## Step 3: Generate Jira API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label: "AutoPM Fake Data Generator"
4. Click "Create"
5. **IMPORTANT**: Copy the token immediately!

## Step 4: Find Your Jira Project Information

### For Jira Cloud:
- **Jira URL**: `https://your-domain.atlassian.net`
  - Find it by looking at your Jira URL when logged in
- **Email**: The email you use to log into Jira
- **Project Key**: Will be auto-generated as AUTOPM1, AUTOPM2, AUTOPM3

### For Jira Server/Data Center:
- **Jira URL**: Your company's Jira URL (e.g., `https://jira.yourcompany.com`)
- **Credentials**: Check with your Jira admin

## Step 5: Configure the Script

You have two options to provide credentials:

### Option A: Environment Variables (Recommended - More Secure)

Create a `.env` file in the `fastapi_backend` directory:

```bash
# Create .env file
cat > .env << 'EOF'
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_USERNAME=your_github_username
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_api_token_here
EOF
```

Then modify the script to load from .env:

```python
from dotenv import load_dotenv
load_dotenv()  # Add this at the top of the main() function
```

### Option B: Direct Modification (Quick Testing)

Open `generate_fake_data.py` and modify these lines:

```python
GITHUB_TOKEN = 'ghp_your_actual_token_here'
GITHUB_USERNAME = 'your_github_username'
JIRA_URL = 'https://your-domain.atlassian.net'
JIRA_EMAIL = 'your-email@example.com'
JIRA_API_TOKEN = 'your_jira_token_here'
```

## Step 6: Customize Data Generation (Optional)

You can modify these variables in the script to control data generation:

```python
NUM_PROJECTS = 3              # Number of GitHub repos and Jira projects
ISSUES_PER_PROJECT = 20       # GitHub issues per repository
PRS_PER_PROJECT = 10          # GitHub pull requests per repository
JIRA_TASKS_PER_PROJECT = 40   # Jira issues per project (120 total)
```

To add more fake users for collaboration:

```python
FAKE_USERS = [
    {"name": "Your Name", "email": "your.email@example.com", "github": "yourusername"},
    {"name": "Teammate 1", "email": "teammate1@example.com", "github": "teammate1"},
    # Add more users as needed
]
```

## Step 7: Run the Script

```bash
# Make sure you're in the fastapi_backend directory
cd /path/to/AutoPM/fastapi_backend

# Activate virtual environment if not already active
source autopm_venv/bin/activate

# Run the script
python generate_fake_data.py
```

## What the Script Does

The script will:

1. ✅ Create 3 GitHub repositories named:
   - `project-1-autopmtestproject`
   - `project-2-autopmtestproject`
   - `project-3-autopmtestproject`

2. ✅ For each repository, create:
   - Initial files (README.md, .gitignore, LICENSE, source files)
   - 20 issues with various labels
   - Comments on issues from fake users
   - 10 pull requests with file changes
   - Some closed issues and merged PRs

3. ✅ Create 3 Jira projects:
   - AUTOPM1, AUTOPM2, AUTOPM3
   - 40 tasks per project (120+ total)
   - Different issue types (Task, Bug, Story, Epic)
   - Comments on issues
   - Various statuses (To Do, In Progress, Done)

## Expected Output

```
╔═══════════════════════════════════════════════════════════╗
║   GitHub & Jira Fake Data Generator for AutoPM Testing   ║
╚═══════════════════════════════════════════════════════════╝

============================================================
Creating GitHub Repository: project-1-autopmtestproject
============================================================
✓ Repository created: https://github.com/username/project-1-autopmtestproject
✓ README.md created
✓ Created src/main.py
...

============================================================
Creating 20 Issues for project-1-autopmtestproject
============================================================
✓ Issue #1: Implement user authentication system...
  → Added 3 comments
  → Closed issue
...
```

## Troubleshooting

### Error: "Bad credentials" (GitHub)
- Check your GitHub token is correct
- Ensure token hasn't expired
- Verify token has correct permissions

### Error: "Unauthorized" (Jira)
- Check Jira email is correct
- Verify Jira API token is valid
- Ensure Jira URL is correct (include https://)

### Error: "Project creation failed" (Jira)
- You may not have admin permissions to create projects
- **Solution**: Manually create projects in Jira with keys AUTOPM1, AUTOPM2, AUTOPM3
- Then run the script again - it will populate existing projects

### Rate Limiting
- GitHub: 5000 requests/hour for authenticated users
- If you hit rate limits, the script will show errors
- Add longer `time.sleep()` delays between operations

### Issues with Branches/PRs
- If PR creation fails, it might be due to protected branches
- Check repository settings and branch protection rules

## Cleanup (Optional)

To delete the test repositories later:

```bash
# Using GitHub CLI (if installed)
gh repo delete username/project-1-autopmtestproject
gh repo delete username/project-2-autopmtestproject
gh repo delete username/project-3-autopmtestproject

# Or delete manually through GitHub web interface
```

For Jira projects, delete through the Jira web interface:
Settings → Projects → Select project → Delete

## Advanced Usage

### Running Individual Functions

You can modify the `main()` function to run only specific parts:

```python
def main():
    # Only create GitHub repos (no Jira)
    github_gen = GitHubDataGenerator(GITHUB_TOKEN, GITHUB_USERNAME)
    for i in range(1, 4):
        repo = github_gen.create_project(i)
        github_gen.create_issues(repo, 20)
        github_gen.create_pull_requests(repo, 10)
```

### Testing with One Project First

Change `NUM_PROJECTS = 1` and run the script to test with just one project first.

## Security Best Practices

1. ✅ Never commit tokens to Git
2. ✅ Add `.env` to `.gitignore`
3. ✅ Use environment variables in production
4. ✅ Rotate tokens regularly
5. ✅ Delete tokens after testing

## Need Help?

If you encounter issues:
1. Check the error messages in the console
2. Verify all credentials are correct
3. Ensure you have proper permissions
4. Check GitHub/Jira API documentation
5. Try running with just 1 project first for testing

---

**Happy Testing! 🚀**
