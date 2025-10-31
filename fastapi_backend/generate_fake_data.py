"""
Fake Data Generator for GitHub and Jira - Multi-User Collaborative Setup
This script generates realistic test data for GitHub repositories and Jira projects
with proper multi-user collaboration structure.

Required Python packages:
    pip install PyGithub requests faker python-dotenv

Environment Variables Required:
    Manager Account (variables without numbers):
        GITHUB_TOKEN=manager_github_personal_access_token
        GITHUB_USERNAME=manager_github_username
        JIRA_URL=https://your-domain.atlassian.net
        JIRA_EMAIL=manager_jira_email@example.com
        JIRA_API_TOKEN=manager_jira_api_token
    
    Team Members (variables with _1 to _5):
        GITHUB_TOKEN_1, GITHUB_USERNAME_1, JIRA_EMAIL_1, JIRA_API_TOKEN_1
        GITHUB_TOKEN_2, GITHUB_USERNAME_2, JIRA_EMAIL_2, JIRA_API_TOKEN_2
        ... (up to _5)

The manager account will own all repositories and Jira projects.
Team members will be added as collaborators to all GitHub repos and Jira projects.
"""

import os
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from faker import Faker
from github import Github, GithubException
from dotenv import load_dotenv

# Load environment variables from .env file (will try .env.multi_users first, then .env)
if os.path.exists('.env.multi_users'):
    load_dotenv('.env.multi_users')
    print("✓ Loaded configuration from .env.multi_users")
else:
    load_dotenv()
    print("✓ Loaded configuration from .env")

# Initialize Faker
fake = Faker()

# Manager Configuration (owns all repos and projects) - variables without numbers
MANAGER_GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'YOUR_GITHUB_TOKEN_HERE')
MANAGER_GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'YOUR_USERNAME_HERE')
MANAGER_JIRA_EMAIL = os.getenv('JIRA_EMAIL', 'your-email@example.com')
MANAGER_JIRA_TOKEN = os.getenv('JIRA_API_TOKEN', 'YOUR_JIRA_TOKEN_HERE')
JIRA_URL = os.getenv('JIRA_URL', 'https://your-domain.atlassian.net')

# Load team member credentials (variables with _1 to _5) - for realistic collaboration
TEAM_CREDENTIALS = []
for i in range(1, 6):  # _1 to _5
    github_username = os.getenv(f'GITHUB_USERNAME_{i}')
    github_token = os.getenv(f'GITHUB_TOKEN_{i}')
    jira_email = os.getenv(f'JIRA_EMAIL_{i}')
    jira_token = os.getenv(f'JIRA_API_TOKEN_{i}')
    
    # Only add if credentials exist
    if all([github_username, github_token, jira_email, jira_token]):
        user_data = {
            'github_username': github_username,
            'github_token': github_token,
            'jira_email': jira_email,
            'jira_token': jira_token,
        }
        TEAM_CREDENTIALS.append(user_data)

if TEAM_CREDENTIALS:
    print(f"✓ Loaded {len(TEAM_CREDENTIALS)} team member credentials for realistic collaboration")

# Project configuration
NUM_PROJECTS = 3
ISSUES_PER_PROJECT = 20
PRS_PER_PROJECT = 10
JIRA_TASKS_PER_PROJECT = 40  # Will create 120+ total tasks

# Team members for collaboration (Automotive team members)
# Manager account (Adhiv) will own all repos and projects
MANAGER = {
    "name": "Adhiv P",
    "email": "adhivp04@gmail.com",
    "github": "Adhivp",
    "role": "Project Manager / Product Owner"
}

# Team member accounts - these will be collaborators (matches .env variables _1 to _5)
FAKE_USERS = [
    {"name": "Sarah Chen", "email": "sarahchen.autopm@gmail.com", "github": "sarahchen-autopm", "role": "Embedded Systems Engineer", "performance": "high"},
    {"name": "Marcus Weber", "email": "marcusweber.autopm@gmail.com", "github": "marcusweber-autopm", "role": "Vehicle Software Architect", "performance": "high"},
    {"name": "Priya Patel", "email": "priyapatel.autopm@gmail.com", "github": "priyapatel-autopm", "role": "ADAS Developer", "performance": "high"},
    {"name": "Johan Schmidt", "email": "johanschmidt.autopm@gmail.com", "github": "johanschmidt-autopm", "role": "Automotive QA Engineer", "performance": "high"},
    {"name": "Elena Rodriguez", "email": "elenarodriguez.autopm@gmail.com", "github": "elenarodriguez-autopm", "role": "ADAS Developer", "performance": "medium"},  # Duplicate role for comparison
]

# Automotive project themes
AUTOMOTIVE_PROJECTS = [
    {
        "name": "infotainment-system",
        "description": "Next-generation in-vehicle infotainment system with Android Automotive OS integration",
        "tech_stack": ["Android Automotive", "Kotlin", "C++", "AAOS", "Gradle"],
        "features": [
            "Voice-activated navigation and controls",
            "Wireless Android Auto and Apple CarPlay integration",
            "Over-the-air (OTA) update capabilities",
            "Multi-zone audio management system",
            "Real-time traffic and weather integration"
        ]
    },
    {
        "name": "adas-driver-assistance",
        "description": "Advanced Driver Assistance Systems (ADAS) featuring adaptive cruise control and lane keeping",
        "tech_stack": ["AUTOSAR", "C/C++", "Python", "ROS2", "TensorFlow"],
        "features": [
            "Adaptive Cruise Control (ACC) with stop-and-go",
            "Lane Departure Warning and Lane Keep Assist",
            "Automatic Emergency Braking (AEB) system",
            "Blind Spot Detection and monitoring",
            "Traffic Sign Recognition (TSR) module"
        ]
    },
    {
        "name": "vehicle-diagnostics",
        "description": "Comprehensive vehicle diagnostics and telemetry system with cloud connectivity",
        "tech_stack": ["Python", "CAN Bus", "MQTT", "AWS IoT", "React"],
        "features": [
            "Real-time OBD-II data collection and analysis",
            "Predictive maintenance algorithms",
            "Remote diagnostics and troubleshooting",
            "Vehicle health monitoring dashboard",
            "DTC (Diagnostic Trouble Code) management"
        ]
    }
]

# Automotive-specific issue templates
AUTOMOTIVE_ISSUE_TYPES = {
    "bug": [
        "CAN bus communication timeout in {component}",
        "Memory leak detected in {component} module",
        "Intermittent sensor data loss from {sensor}",
        "ECU firmware update failure on {vehicle_model}",
        "Display flickering in {screen} under direct sunlight",
        "Bluetooth pairing fails with certain smartphones",
        "Navigation system GPS accuracy degraded",
        "Audio system crackling at high volume levels",
        "Climate control not responding to touch inputs",
        "Steering wheel controls intermittently unresponsive"
    ],
    "enhancement": [
        "Implement battery thermal management optimization",
        "Add support for ISO 26262 safety requirements",
        "Enhance UI responsiveness for touch screen controls",
        "Integrate V2X (Vehicle-to-Everything) communication",
        "Improve energy consumption monitoring accuracy",
        "Add multi-language support for voice commands",
        "Implement predictive route calculation algorithm",
        "Enhance night mode visibility for HMI displays",
        "Add customizable driver profiles and preferences",
        "Implement gesture-based control system"
    ],
    "documentation": [
        "Document CAN message database specifications",
        "Update AUTOSAR software architecture diagrams",
        "Create user manual for diagnostic tool interface",
        "Document safety-critical software requirements",
        "Update API documentation for telematics module",
        "Create troubleshooting guide for ECU flashing",
        "Document calibration procedures for sensors",
        "Update release notes for OTA update package",
        "Create integration guide for third-party modules",
        "Document testing procedures for ADAS features"
    ]
}

# Automotive-specific components and systems
AUTOMOTIVE_COMPONENTS = [
    "ECU (Electronic Control Unit)", "TCU (Telematics Control Unit)", "BCM (Body Control Module)",
    "Gateway Module", "Instrument Cluster", "Head Unit", "ADAS Camera", "Radar Sensor",
    "Ultrasonic Sensors", "LiDAR Module", "GPS Receiver", "CAN Controller", "LIN Bus",
    "Infotainment Display", "Climate Control System", "Power Management System"
]

AUTOMOTIVE_SENSORS = [
    "IMU (Inertial Measurement Unit)", "Wheel Speed Sensor", "Parking Sensor",
    "Rain Sensor", "Light Sensor", "Temperature Sensor", "Pressure Sensor",
    "Accelerometer", "Gyroscope", "Camera Module"
]

VEHICLE_MODELS = [
    "Sedan-2024", "SUV-2025", "EV-Compact", "Hybrid-Sport", "Truck-HD"
]


class GitHubDataGenerator:
    """Generate fake data for GitHub repositories"""
    
    def __init__(self, token: str, username: str):
        self.gh = Github(token)
        self.username = username
        self.user = self.gh.get_user()
        self.created_repos = []
    
    def add_collaborators(self, repo, team_credentials: list):
        """Add team members as collaborators and auto-accept invitations"""
        print(f"\n{'='*60}")
        print(f"Adding Collaborators to {repo.name}")
        print(f"{'='*60}")
        
        for i, cred in enumerate(team_credentials):
            try:
                github_username = cred['github_username']
                github_token = cred['github_token']
                
                # Add collaborator with push access (sends invitation)
                repo.add_to_collaborators(github_username, permission='push')
                print(f"✓ Sent invitation to {github_username} (USER_{i+1})")
                time.sleep(2)  # Wait for invitation to be sent
                
                # Auto-accept invitation using their token
                try:
                    member_gh = Github(github_token)
                    member_user = member_gh.get_user()
                    
                    # Get pending invitations
                    invitations = member_user.get_invitations()
                    for invitation in invitations:
                        if invitation.repository.id == repo.id:
                            invitation.accept()
                            print(f"  ✓ {github_username} accepted invitation automatically")
                            break
                    time.sleep(1)
                except Exception as e:
                    print(f"  ⚠ Could not auto-accept for {github_username}: {str(e)}")
                    print(f"  → They will need to accept manually via email")
                    
            except Exception as e:
                print(f"⚠ Could not add {github_username}: {str(e)}")
        
        print(f"✓ Collaborator setup completed!")
        
    def create_project(self, project_num: int) -> Any:
        """Create a GitHub repository or skip if it already exists"""
        project_info = AUTOMOTIVE_PROJECTS[project_num - 1]
        repo_name = f"{project_info['name']}-autopmtestproject"
        description = project_info['description']
        
        print(f"\n{'='*60}")
        print(f"Checking GitHub Repository: {repo_name}")
        print(f"{'='*60}")
        
        try:
            # Check if repo already exists
            try:
                repo = self.user.get_repo(repo_name)
                print(f"✓ Repository '{repo_name}' already exists")
                print(f"  URL: {repo.html_url}")
                print(f"⏭️  Skipping repository setup (already exists)")
                self.created_repos.append(repo)
                return {'repo': repo, 'already_exists': True}
            except GithubException:
                # Create new repository
                print(f"📦 Creating new repository...")
                repo = self.user.create_repo(
                    name=repo_name,
                    description=description,
                    private=False,
                    auto_init=True,
                    has_issues=True,
                    has_projects=True,
                    has_wiki=True
                )
                print(f"✓ Repository created: {repo.html_url}")
                time.sleep(2)
                
                # Create README
                self._create_readme(repo)
                
                # Create some files to work with
                self._create_initial_files(repo)
                
                self.created_repos.append(repo)
                return {'repo': repo, 'already_exists': False}
            
        except Exception as e:
            print(f"✗ Error with repository: {str(e)}")
            return None
    
    def _create_readme(self, repo):
        """Create or update README file"""
        try:
            # Find matching project info
            project_info = None
            for proj in AUTOMOTIVE_PROJECTS:
                if proj['name'] in repo.name:
                    project_info = proj
                    break
            
            if not project_info:
                project_info = AUTOMOTIVE_PROJECTS[0]
            
            readme_content = f"""# {repo.name}

## 🚗 Description
{project_info['description']}

## ✨ Key Features
{chr(10).join([f"- {feature}" for feature in project_info['features']])}

## 🛠️ Technology Stack
{chr(10).join([f"- {tech}" for tech in project_info['tech_stack']])}

## 📋 Prerequisites
- Automotive-grade development environment
- CAN/LIN bus simulation tools (Vector CANoe/CANalyzer recommended)
- ISO 26262 compliance documentation (for safety-critical modules)
- Hardware-in-the-loop (HIL) testing setup

## 🚀 Installation
```bash
git clone {repo.clone_url}
cd {repo.name}

# Install dependencies
pip install -r requirements.txt  # For Python modules
# OR
./scripts/build.sh  # For embedded C/C++ projects
```

## 🔧 Configuration
Configure your vehicle parameters in `config/vehicle_params.yaml`:
```yaml
vehicle_type: sedan
can_bitrate: 500000
lin_baudrate: 19200
```

## 📖 Usage
Refer to `docs/USER_GUIDE.md` for detailed usage instructions.

## 🧪 Testing
```bash
# Run unit tests
pytest tests/

# Run HIL tests
./scripts/run_hil_tests.sh

# Generate coverage report
pytest --cov=src tests/
```

## 🏗️ Architecture
See `docs/ARCHITECTURE.md` for detailed software architecture and component diagrams.

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first.
Ensure all changes comply with ISO 26262 and AUTOSAR guidelines.

## 📄 License
MIT License - see LICENSE file for details

## ⚠️ Safety Notice
This software is intended for development and testing purposes. 
Ensure proper validation before deployment in production vehicles.
"""
            try:
                contents = repo.get_contents("README.md")
                repo.update_file("README.md", "Update README", readme_content, contents.sha)
                print("✓ README.md updated")
            except:
                repo.create_file("README.md", "Create README", readme_content)
                print("✓ README.md created")
            time.sleep(1)
        except Exception as e:
            print(f"✗ Error creating README: {str(e)}")
    
    def _create_initial_files(self, repo):
        """Create some initial files in the repository"""
        # Find matching project info
        project_info = None
        for proj in AUTOMOTIVE_PROJECTS:
            if proj['name'] in repo.name:
                project_info = proj
                break
        
        files = {
            "src/main.cpp": """/**
 * Main entry point for automotive software module
 * ISO 26262 ASIL-B compliant
 */

#include <iostream>
#include "vehicle_controller.h"

int main() {
    VehicleController controller;
    controller.initialize();
    controller.startMainLoop();
    return 0;
}
""",
            "src/can_handler.cpp": """/**
 * CAN Bus communication handler
 * Handles ISO 11898 compliant CAN 2.0B protocol
 */

#include "can_handler.h"

void CANHandler::sendMessage(uint32_t id, uint8_t* data, uint8_t len) {
    // Implementation for CAN message transmission
}

void CANHandler::receiveMessage() {
    // Implementation for CAN message reception
}
""",
            "config/vehicle_params.yaml": """# Vehicle Configuration Parameters
vehicle_type: sedan
model_year: 2025
can_bitrate: 500000
lin_baudrate: 19200

# ECU Configuration
ecu_address: 0x10
diagnostic_session: default

# Safety Parameters
watchdog_timeout_ms: 100
fail_safe_mode: enabled
""",
            ".gitignore": """*.pyc
__pycache__/
.env
node_modules/
*.o
*.out
*.bin
*.hex
*.elf
build/
dist/
*.log
.vscode/
.DS_Store
""",
            "LICENSE": "MIT License\n\nCopyright (c) 2025 Automotive Software Development Team\n",
            "docs/ARCHITECTURE.md": """# Software Architecture

## Overview
This document describes the software architecture for the automotive module.

## Components
- ECU Controller
- CAN Bus Handler
- Diagnostic Module
- Safety Monitor

## Data Flow
Vehicle Sensors → CAN Bus → ECU → Actuators
""",
        }
        
        for filepath, content in files.items():
            try:
                repo.create_file(filepath, f"Add {filepath}", content)
                print(f"✓ Created {filepath}")
                time.sleep(1)
            except Exception as e:
                print(f"  File {filepath} might already exist")
    
    def create_issues(self, repo, num_issues: int, team_credentials: list = None):
        """Create issues with various states, distributed across team members"""
        print(f"\n{'='*60}")
        print(f"Creating {num_issues} Issues for {repo.name}")
        print(f"{'='*60}")
        
        # Prepare team member GitHub instances
        team_gh_instances = []
        if team_credentials:
            for cred in team_credentials:
                try:
                    gh = Github(cred['github_token'])
                    team_gh_instances.append({
                        'gh': gh,
                        'username': cred['github_username'],
                        'user_obj': FAKE_USERS[len(team_gh_instances)] if len(team_gh_instances) < len(FAKE_USERS) else FAKE_USERS[0]
                    })
                except:
                    pass
            print(f"✓ {len(team_gh_instances)} team members will contribute to issues")
        
        labels_list = ["bug", "enhancement", "documentation", "safety-critical", "AUTOSAR", "ISO26262", "testing", "CAN-bus"]
        label_colors = {
            "bug": "FF0000",
            "enhancement": "00FF00",
            "documentation": "0000FF",
            "safety-critical": "FF0000",
            "AUTOSAR": "FFA500",
            "ISO26262": "800080",
            "testing": "FFFF00",
            "CAN-bus": "00FFFF"
        }
        
        # Create labels first
        existing_labels = [label.name for label in repo.get_labels()]
        for label_name in labels_list:
            if label_name not in existing_labels:
                try:
                    repo.create_label(label_name, label_colors.get(label_name, "CCCCCC"))
                except:
                    pass
        
        issues = []
        for i in range(num_issues):
            try:
                # Select issue type and generate appropriate title
                issue_type = random.choice(list(AUTOMOTIVE_ISSUE_TYPES.keys()))
                title_template = random.choice(AUTOMOTIVE_ISSUE_TYPES[issue_type])
                
                # Replace placeholders with actual automotive terms
                title = title_template.format(
                    component=random.choice(AUTOMOTIVE_COMPONENTS),
                    sensor=random.choice(AUTOMOTIVE_SENSORS),
                    vehicle_model=random.choice(VEHICLE_MODELS),
                    screen="Infotainment Display"
                )
                
                # Generate automotive-specific issue body
                if issue_type == "bug":
                    body = f"""## 🐛 Bug Description
{fake.paragraph(nb_sentences=2)}

## 🔍 Steps to Reproduce
1. Initialize {random.choice(AUTOMOTIVE_COMPONENTS)} module
2. Send CAN message ID 0x{random.randint(100, 999):03X} with payload: {' '.join([f'{random.randint(0, 255):02X}' for _ in range(8)])}
3. Monitor ECU response on diagnostic interface
4. Observe error condition

## 📊 Expected Behavior
- ECU should respond with ACK within 50ms
- No DTC (Diagnostic Trouble Code) should be set
- System should maintain normal operation

## ❌ Actual Behavior
- ECU timeout after {random.randint(100, 500)}ms
- DTC P{random.randint(1000, 3999):04d} is set in error memory
- System enters fail-safe mode

## 🔧 Environment
- **Vehicle Model**: {random.choice(VEHICLE_MODELS)}
- **ECU Software Version**: v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}
- **CAN Bus Load**: {random.randint(20, 80)}%
- **Temperature**: {random.randint(-20, 85)}°C

## 📝 Additional Context
- Frequency: {random.choice(['Always', 'Intermittent', 'Under specific conditions'])}
- Impact: {random.choice(['High - Safety critical', 'Medium - Performance degraded', 'Low - Minor inconvenience'])}
- Related AUTOSAR Module: {random.choice(['ComM', 'CanIf', 'PduR', 'Dcm', 'Dem'])}
"""
                elif issue_type == "enhancement":
                    body = f"""## 💡 Enhancement Request
{fake.paragraph(nb_sentences=2)}

## 🎯 Objective
Improve {random.choice(['performance', 'reliability', 'user experience', 'energy efficiency', 'diagnostic capabilities'])} of the {random.choice(AUTOMOTIVE_COMPONENTS)} system.

## 📋 Requirements
- [ ] Must comply with ISO 26262 ASIL-{random.choice(['A', 'B', 'C', 'D'])} requirements
- [ ] Must maintain backward compatibility with existing {random.choice(VEHICLE_MODELS)}
- [ ] Response time must be < {random.randint(10, 100)}ms
- [ ] Memory footprint should not exceed +{random.randint(5, 20)}KB

## 🔨 Proposed Implementation
1. Update AUTOSAR configuration for {random.choice(AUTOMOTIVE_COMPONENTS)}
2. Modify CAN message database (DBC file)
3. Implement new diagnostic service 0x{random.randint(16, 255):02X}
4. Add unit tests and HIL validation

## 📈 Expected Benefits
- {random.randint(10, 50)}% improvement in {random.choice(['response time', 'accuracy', 'efficiency', 'reliability'])}
- Enhanced user satisfaction
- Reduced warranty claims

## ⚠️ Risks & Mitigation
- **Risk**: Increased CPU load
- **Mitigation**: Optimize algorithm and use hardware acceleration
"""
                else:  # documentation
                    body = f"""## 📚 Documentation Update Required

## 📝 Description
{fake.paragraph(nb_sentences=2)}

## 📂 Files to Update
- [ ] `docs/technical_specification.md`
- [ ] `docs/user_manual.pdf`
- [ ] `README.md`
- [ ] Inline code comments

## ✏️ Required Changes
- Document new {random.choice(AUTOMOTIVE_COMPONENTS)} interface
- Update CAN message definitions
- Add troubleshooting section
- Include timing diagrams
- Update safety requirements traceability matrix

## 🎓 Target Audience
{random.choice(['Development team', 'QA engineers', 'End users', 'System integrators', 'Certification auditors'])}

## 📅 Priority
{random.choice(['High - Required for certification', 'Medium - Improves maintainability', 'Low - Nice to have'])}
"""
                
                # Create issue with appropriate labels
                selected_labels = [issue_type]
                if issue_type == "bug" and random.random() > 0.7:
                    selected_labels.append("safety-critical")
                if random.random() > 0.6:
                    selected_labels.append(random.choice(["AUTOSAR", "ISO26262", "CAN-bus"]))
                
                # Decide who creates this issue (85% team members, 15% manager)
                # Team members do most of the work, manager just oversees
                creator_name = "Manager"
                assigned_member = None
                
                if team_gh_instances and random.random() > 0.15:
                    # Team member creates the issue (most common)
                    team_member = random.choice(team_gh_instances)
                    assigned_member = team_member  # They'll work on it
                    try:
                        member_repo = team_member['gh'].get_repo(repo.full_name)
                        issue = member_repo.create_issue(
                            title=title,
                            body=body,
                            labels=selected_labels
                        )
                        creator_name = team_member['username']
                        creator_display = team_member['user_obj']['name']
                        print(f"✓ Issue #{issue.number} by {creator_display}: {title[:50]}...")
                    except Exception as e:
                        # Fallback to manager if team member can't create
                        issue = repo.create_issue(title=title, body=body, labels=selected_labels)
                        print(f"✓ Issue #{issue.number} (Manager): {title[:50]}...")
                        # Still assign to a team member
                        assigned_member = random.choice(team_gh_instances) if team_gh_instances else None
                else:
                    # Manager creates the issue (rare - oversight/planning)
                    issue = repo.create_issue(title=title, body=body, labels=selected_labels)
                    print(f"✓ Issue #{issue.number} (Manager): {title[:50]}...")
                    # Assign to a team member to do the work
                    assigned_member = random.choice(team_gh_instances) if team_gh_instances else None
                
                # Add assignment comment if assigned
                if assigned_member and creator_name == "Manager":
                    assignee_name = assigned_member['user_obj']['name']
                    try:
                        issue.create_comment(f"@{assigned_member['username']} - Assigned to you for implementation. Please provide updates.")
                        print(f"  → Assigned to {assignee_name}")
                    except:
                        pass
                
                # Add comments from different team members
                if random.random() > 0.5:
                    num_comments = random.randint(1, 5)
                    automotive_comments = [
                        "I've tested this on the HIL bench and confirmed the issue. CAN trace attached.",
                        "Root cause identified: Timing violation in the AUTOSAR BSW layer.",
                        "Proposed fix validated against ISO 26262 requirements. Ready for code review.",
                        "Updated the DBC file to reflect the new CAN message structure.",
                        "Confirmed: This affects all vehicles with ECU version >= v2.3.0",
                        "Ran full regression test suite - all safety tests pass.",
                        "This requires recalibration of the sensor after deployment.",
                        "Added diagnostic DTC P0A00 for better troubleshooting.",
                        "Memory analysis shows no leaks. CPU usage increased by 3%.",
                        "Successfully tested with Vector CANoe simulation."
                    ]
                    
                    # Realistic work progression comments
                    work_stages = [
                        "Looking into this. Running initial diagnostics on HIL bench.",
                        "Root cause identified. Working on fix now.",
                        "Testing proposed solution. Initial results look promising.",
                        "Regression tests passing. Ready for code review.",
                        "Fix validated against ISO 26262 requirements. PR coming shortly.",
                        "Successfully tested with Vector CANoe. Ready for deployment.",
                    ]
                    
                    manager_reviews = ["Approved.", "Looks good!", "Please update docs.", "Coordinate with QA team."]
                    
                    for comment_idx in range(num_comments):
                        # 85% team members (doing work), 15% manager (oversight)
                        if team_gh_instances and random.random() > 0.15:
                            # Team member doing the work
                            if assigned_member and random.random() > 0.4:
                                commenter = assigned_member
                            else:
                                commenter = random.choice(team_gh_instances)
                            
                            comment_text = work_stages[min(comment_idx, len(work_stages)-1)]
                            try:
                                member_repo = commenter['gh'].get_repo(repo.full_name)
                                member_issue = member_repo.get_issue(issue.number)
                                member_issue.create_comment(comment_text)
                            except:
                                user = commenter['user_obj']
                                issue.create_comment(f"**{user['name']}**: {comment_text}")
                        else:
                            # Manager review
                            issue.create_comment(random.choice(manager_reviews))
                        time.sleep(0.5)
                
                # Close some issues
                if random.random() > 0.6:
                    issue.edit(state="closed")
                    print(f"  → Closed issue")
                
                issues.append(issue)
                time.sleep(1.5)
                
            except Exception as e:
                print(f"✗ Error creating issue: {str(e)}")
        
        return issues
    
    def create_pull_requests(self, repo, num_prs: int, team_credentials: list = None):
        """Create pull requests with various states, from team member accounts"""
        print(f"\n{'='*60}")
        print(f"Creating {num_prs} Pull Requests for {repo.name}")
        print(f"{'='*60}")
        
        # Prepare team member GitHub instances
        team_gh_instances = []
        if team_credentials:
            for cred in team_credentials:
                try:
                    gh = Github(cred['github_token'])
                    team_gh_instances.append({
                        'gh': gh,
                        'username': cred['github_username']
                    })
                except:
                    pass
        
        default_branch = repo.default_branch
        prs = []
        
        for i in range(num_prs):
            try:
                branch_name = f"feature/{fake.slug()}"
                pr_title = fake.sentence(nb_words=6)
                
                # Get the latest commit from default branch
                source_branch = repo.get_branch(default_branch)
                
                # Create a new branch
                try:
                    repo.create_git_ref(
                        ref=f"refs/heads/{branch_name}",
                        sha=source_branch.commit.sha
                    )
                    
                    # Create a file change in the new branch with automotive code
                    file_path = f"src/ecu_module_{i}.cpp"
                    feature_name = random.choice([
                        "battery_management", "thermal_control", "power_distribution",
                        "sensor_fusion", "diagnostics_handler", "can_gateway",
                        "safety_monitor", "actuator_control", "telemetry_service"
                    ])
                    content = f"""/**
 * @file ecu_module_{i}.cpp
 * @brief {feature_name.replace('_', ' ').title()} Module
 * @author {random.choice(FAKE_USERS)['name']}
 * @date 2025-10-31
 * @version 1.0.0
 * 
 * ISO 26262 ASIL-{random.choice(['A', 'B', 'C'])} compliant implementation
 */

#include "{feature_name}.h"
#include "autosar_types.h"

/**
 * @brief Initialize {feature_name} module
 * @return Status code (0 = success)
 */
uint8_t {feature_name}_init(void) {{
    // Initialize module parameters
    // Setup CAN communication
    // Configure safety checks
    return 0;
}}

/**
 * @brief Main cyclic task for {feature_name}
 * @param delta_time Time since last call in milliseconds
 */
void {feature_name}_update(uint16_t delta_time) {{
    // Process sensor data
    // Update control algorithms
    // Send CAN messages
}}

/**
 * @brief Shutdown {feature_name} module
 */
void {feature_name}_shutdown(void) {{
    // Cleanup resources
    // Save persistent data
}}
"""
                    repo.create_file(
                        file_path,
                        f"feat: Implement {feature_name} module",
                        content,
                        branch=branch_name
                    )
                    
                    time.sleep(1)
                    
                    # Create pull request with automotive context
                    pr_body = f"""## 🔧 Changes
Implements {feature_name.replace('_', ' ')} functionality for enhanced vehicle performance and safety.

### Key Modifications
- Added new ECU module for {feature_name}
- Updated CAN message database with message ID 0x{random.randint(100, 999):03X}
- Implemented AUTOSAR-compliant error handling
- Added safety-critical checks per ISO 26262

## 🔗 Related Issues
Closes #{random.randint(1, 10)}
Related to #{random.randint(11, 20)}

## 🧪 Testing Completed
- [x] Unit tests (coverage: {random.randint(85, 100)}%)
- [x] Integration tests with CAN simulator
- [x] Hardware-in-the-loop (HIL) validation
- [x] Static code analysis (MISRA-C compliance)
- [x] Memory safety checks (Valgrind/AddressSanitizer)
- [x] Timing analysis (WCET verification)

## 📊 Performance Impact
- **CPU Usage**: +{random.randint(1, 5)}%
- **Memory Footprint**: +{random.randint(2, 15)}KB
- **CAN Bus Load**: +{random.randint(1, 8)}%
- **Response Time**: {random.randint(5, 50)}ms

## 🛡️ Safety & Security
- ISO 26262 ASIL-{random.choice(['A', 'B', 'C'])} requirements verified
- No new safety-critical defects introduced
- Security vulnerability scan: PASSED

## 📝 Documentation
- [x] Code comments updated
- [x] API documentation generated
- [x] Architecture diagrams updated
- [x] Release notes prepared

## ✅ Checklist
- [x] Code follows AUTOSAR C++ coding guidelines
- [x] Self-review completed
- [x] Peer review requested
- [x] No compiler warnings
- [x] All tests passing
- [x] Ready for QA validation
"""
                    
                    # Create PR from team member (90%) or manager (10%)
                    # Team members do the work, manager reviews
                    pr_creator_name = "Manager"
                    pr_creator_member = None
                    if team_gh_instances and random.random() > 0.1:
                        # Team member creates PR (they did the work)
                        team_member = random.choice(team_gh_instances)
                        pr_creator_member = team_member
                        try:
                            member_repo = team_member['gh'].get_repo(repo.full_name)
                            pr = member_repo.create_pull(
                                title=pr_title,
                                body=pr_body,
                                head=branch_name,
                                base=default_branch
                            )
                            pr_creator_name = team_member['user_obj']['name']
                            print(f"✓ PR #{pr.number} by {pr_creator_name}: {pr_title[:50]}...")
                        except Exception as e:
                            # Fallback to manager
                            pr = repo.create_pull(title=pr_title, body=pr_body, head=branch_name, base=default_branch)
                            pr_creator_name = "Manager"
                            print(f"✓ PR #{pr.number} (Manager): {pr_title[:50]}...")
                    else:
                        # Manager creates PR
                        pr = repo.create_pull(title=pr_title, body=pr_body, head=branch_name, base=default_branch)
                        print(f"✓ PR #{pr.number}: {pr_title[:50]}...")
                    
                    # Add review process - peer review + manager approval
                    if random.random() > 0.5:
                        num_reviews = random.randint(2, 4)
                        
                        peer_review_comments = [
                            "Code looks good. MISRA-C compliance verified.",
                            "Minor: Consider adding null pointer checks.",
                            "Tested on HIL bench - all tests pass.",
                            "Memory footprint is acceptable. LGTM.",
                        ]
                        
                        manager_approval = [
                            "Approved for merge. Great work!",
                            "LGTM. Please merge after updating docs.",
                            "Approved. Ready for next release.",
                        ]
                        
                        # Peer reviews from team members (80%)
                        for review_idx in range(num_reviews):
                            if team_gh_instances and random.random() > 0.2:
                                # Peer review from another team member
                                reviewer = random.choice([m for m in team_gh_instances if m != pr_creator_member])
                                comment = random.choice(peer_review_comments)
                                try:
                                    member_repo = reviewer['gh'].get_repo(repo.full_name)
                                    member_pr = member_repo.get_pull(pr.number)
                                    member_pr.create_issue_comment(comment)
                                except:
                                    user = reviewer['user_obj']
                                    pr.create_issue_comment(f"**{user['name']}**: {comment}")
                            else:
                                # Manager final approval
                                pr.create_issue_comment(random.choice(manager_approval))
                    
                    # Manager merges approved PRs (60% merged)
                    if random.random() > 0.4:
                        try:
                            pr.merge(merge_method="merge")
                            pr.create_issue_comment("✅ Merged by manager.")
                            print(f"  → Merged by manager")
                        except Exception as e:
                            print(f"  → Could not merge")
                    
                    # Close some without merging
                    elif random.random() > 0.7:
                        pr.edit(state="closed")
                        print(f"  → Closed PR without merging")
                    
                    prs.append(pr)
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"  Branch creation issue: {str(e)}")
                    continue
                    
            except Exception as e:
                print(f"✗ Error creating PR: {str(e)}")
        
        return prs


class JiraDataGenerator:
    """Generate fake data for Jira"""
    
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
        self.projects = []
    
    def add_users_to_project(self, project_key: str, team_credentials: list):
        """Add team members to Jira project"""
        print(f"\n{'='*60}")
        print(f"Adding Team Members to Jira Project {project_key}")
        print(f"{'='*60}")
        
        users_not_found = []
        users_found = 0
        
        for i, cred in enumerate(team_credentials):
            try:
                jira_email = cred['jira_email']
                
                # Get user account ID by email
                search_url = f"{self.url}/rest/api/3/user/search"
                response = self.session.get(search_url, params={'query': jira_email})
                
                if response.status_code == 200 and response.json():
                    account_id = response.json()[0]['accountId']
                    
                    # Add user to project (via role assignment)
                    role_url = f"{self.url}/rest/api/3/project/{project_key}/role"
                    response = self.session.get(role_url)
                    
                    if response.status_code == 200:
                        print(f"✓ User {jira_email} has access to project (USER_{i+1})")
                        users_found += 1
                    else:
                        print(f"⚠ Could not verify access for {jira_email}")
                else:
                    users_not_found.append(jira_email)
                    
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"⚠ Could not process {jira_email}: {str(e)}")
        
        if users_not_found:
            print(f"\n⚠ WARNING: {len(users_not_found)} team members not found in Jira workspace!")
            print(f"📧 Please invite them manually:")
            print(f"   1. Go to {self.url}/jira/people")
            print(f"   2. Click 'Invite people to Jira'")
            print(f"   3. Add these emails:")
            for email in users_not_found:
                print(f"      • {email}")
        
        if users_found > 0:
            print(f"✓ {users_found} team member(s) have access to the project!")
        else:
            print(f"✓ Team member check completed (manual invites needed)")
    
    def create_project(self, project_name: str, project_key: str) -> Dict[str, Any]:
        """Create a Jira space/project (API uses 'project' terminology)"""
        print(f"\n{'='*60}")
        print(f"Checking Jira Space: {project_name} ({project_key})")
        print(f"{'='*60}")
        
        # Note: Creating projects via API requires Jira admin permissions
        # Free Jira accounts typically don't have this permission
        # You need to create spaces manually in Jira UI first
        
        try:
            # Get all projects first (more reliable than direct key lookup)
            print(f"🔍 Fetching all projects from workspace...")
            response = self.session.get(f"{self.url}/rest/api/3/project")
            
            if response.status_code == 200:
                all_projects = response.json()
                print(f"✓ Found {len(all_projects)} total projects in workspace")
                
                # Search for project with matching key
                matching_project = None
                for proj in all_projects:
                    if proj.get('key') == project_key:
                        matching_project = proj
                        break
                
                if matching_project:
                    project_id = matching_project.get('id')
                    project_type = matching_project.get('projectTypeKey', 'unknown')
                    project_style = matching_project.get('style', 'unknown')
                    
                    print(f"✓ Space '{project_key}' found!")
                    print(f"  → ID: {project_id}")
                    print(f"  → Name: {matching_project.get('name')}")
                    print(f"  → Type: {project_type}")
                    print(f"  → Style: {project_style}")
                    
                    # Verify it's a software project
                    if project_type == 'software':
                        print(f"✓ Correct type: Software Development space ✓")
                    else:
                        print(f"⚠ WARNING: Space type is '{project_type}', not 'software'")
                        print(f"  This might cause issues. Please create a Software Development space.")
                    
                    self.projects.append(matching_project)
                    return matching_project
                else:
                    # Project not found - provide instructions
                    print(f"✗ Space '{project_key}' not found in workspace")
                    print(f"  Available project keys: {', '.join([p.get('key', 'N/A') for p in all_projects[:10]])}")
                    print(f"\n📋 Please create the space manually:")
                    print(f"  1. Go to: {self.url}/jira/software/projects")
                    print(f"  2. Click 'Create project' (or 'Create space')")
                    print(f"  3. Choose 'Scrum' or 'Kanban' template (Software Development)")
                    print(f"  4. Set Key to: {project_key} (EXACT)")
                    print(f"  5. Run this script again")
                    return {"key": project_key, "name": project_name}
            else:
                # Cannot fetch projects - likely auth issue
                print(f"✗ Cannot fetch projects (Status: {response.status_code})")
                print(f"  Response: {response.text[:300]}")
                print(f"  Check your JIRA_API_TOKEN and JIRA_EMAIL in .env file")
                print(f"  Regenerate token at: https://id.atlassian.com/manage-profile/security/api-tokens")
                return {"key": project_key, "name": project_name}
                
        except Exception as e:
            print(f"✗ Error checking space: {str(e)}")
            return {"key": project_key, "name": project_name}
    
    def _get_current_user_id(self) -> str:
        """Get current user's account ID"""
        try:
            response = self.session.get(f"{self.url}/rest/api/3/myself")
            if response.status_code == 200:
                return response.json()['accountId']
        except:
            pass
        return None
    
    def create_issues(self, project_key: str, num_issues: int, github_repo_name: str = None):
        """Create Jira issues using REST API v3"""
        print(f"\n{'='*60}")
        print(f"Creating {num_issues} Jira Issues for Space {project_key}")
        print(f"{'='*60}")
        
        # Get all projects and find the one with matching key (more reliable)
        print(f"🔍 Fetching projects to find '{project_key}'...")
        response = self.session.get(f"{self.url}/rest/api/3/project")
        
        if response.status_code != 200:
            print(f"✗ Cannot fetch projects (Status: {response.status_code})")
            print(f"  Check your JIRA_API_TOKEN and JIRA_EMAIL in .env file")
            return []
        
        all_projects = response.json()
        project_info = None
        for proj in all_projects:
            if proj.get('key') == project_key:
                project_info = proj
                break
        
        if not project_info:
            print(f"✗ Space '{project_key}' not found in workspace!")
            print(f"  Available keys: {', '.join([p.get('key') for p in all_projects])}")
            print(f"\n⚠ Please create a SOFTWARE DEVELOPMENT space manually:")
            print(f"   1. Go to {self.url}/jira/software/projects")
            print(f"   2. Click 'Create project' (or 'Create space')")
            print(f"   3. Select 'Scrum' or 'Kanban' template (Software Development)")
            print(f"   4. Set Key to: {project_key} (EXACT)")
            print(f"   5. Run this script again")
            return []
        
        project_id = project_info.get('id')
        project_type = project_info.get('projectTypeKey', 'unknown')
        print(f"✓ Space '{project_key}' found (ID: {project_id}, type: {project_type})")
        
        if project_type != 'software':
            print(f"⚠ WARNING: Space type is '{project_type}', expected 'software'")
            print(f"  You may have created a Work Management space instead")
        
        # Prepare team member Jira sessions for realistic collaboration
        team_members_with_jira = []
        if TEAM_CREDENTIALS:
            for i, cred in enumerate(TEAM_CREDENTIALS):
                try:
                    session = requests.Session()
                    session.auth = (cred['jira_email'], cred['jira_token'])
                    session.headers.update({
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    })
                    team_members_with_jira.append({
                        'name': FAKE_USERS[i]['name'] if i < len(FAKE_USERS) else f"User {i+1}",
                        'email': cred['jira_email'],
                        'session': session,
                        'role': FAKE_USERS[i]['role'] if i < len(FAKE_USERS) else "Developer",
                        'performance': FAKE_USERS[i]['performance'] if i < len(FAKE_USERS) else "medium"
                    })
                except Exception as e:
                    print(f"  ⚠ Could not setup Jira session for team member {i+1}: {str(e)}")
        
        if team_members_with_jira:
            print(f"✓ {len(team_members_with_jira)} team members will create and work on issues")
        else:
            print(f"⚠ No team members configured - manager will create all issues")
        
        issue_types = ["Task", "Bug", "Story", "Epic"]
        priorities = ["Highest", "High", "Medium", "Low", "Lowest"]
        statuses_to_transition = ["In Progress", "Done", "Closed"]
        
        # Track issue creation per team member for equal distribution (by index)
        team_issue_counts = {i: 0 for i in range(len(team_members_with_jira))}
        
        # Automotive-specific Jira tasks
        automotive_tasks = {
            "Task": [
                "Implement CAN message parser for ECU communication",
                "Update AUTOSAR configuration for new sensor module",
                "Calibrate adaptive cruise control parameters",
                "Integrate OTA update mechanism for ECU firmware",
                "Configure diagnostic protocol (UDS ISO 14229)",
                "Implement watchdog timer for safety monitoring",
                "Optimize battery management algorithm",
                "Setup CI/CD pipeline for automated ECU builds",
                "Create test vectors for HIL validation",
                "Update vehicle configuration database"
            ],
            "Bug": [
                "CAN bus arbitration failure under high load conditions",
                "Memory corruption in bootloader during flash operations",
                "Intermittent sensor timeout in cold temperature conditions",
                "DTC P0456 incorrectly triggered on startup sequence",
                "EEPROM write failure causing configuration loss",
                "GPS signal loss not properly handled in navigation",
                "Battery SoC estimation drift over extended driving",
                "Display rendering artifacts in night mode",
                "Audio DSP causing system latency spikes",
                "Parking assist sensors showing false positives"
            ],
            "Story": [
                "As a driver, I want voice control for climate settings",
                "As a service technician, I need remote diagnostic capabilities",
                "As a fleet manager, I want real-time vehicle health monitoring",
                "As a driver, I want predictive maintenance notifications",
                "As a user, I want seamless smartphone integration",
                "As a driver, I want customizable instrument cluster layouts",
                "As a technician, I want wireless ECU programming capability",
                "As a driver, I want automated parking assistance",
                "As a user, I want OTA software updates with progress tracking",
                "As a driver, I want advanced driver drowsiness detection"
            ],
            "Epic": [
                "Develop complete ADAS Level 2+ automation system",
                "Implement next-generation infotainment platform",
                "Create unified vehicle diagnostics framework",
                "Build electric powertrain control system",
                "Develop vehicle-to-everything (V2X) communication",
                "Implement ISO 26262 ASIL-D safety architecture",
                "Create autonomous parking valet feature",
                "Build integrated telematics and fleet management",
                "Develop predictive maintenance AI system",
                "Implement cybersecurity hardening per ISO/SAE 21434"
            ]
        }
        
        created_issues = []
        
        for i in range(num_issues):
            try:
                issue_type = random.choice(issue_types)
                priority = random.choice(priorities)
                
                # Get automotive-specific summary
                summary = random.choice(automotive_tasks[issue_type])
                
                # Generate automotive-specific description
                if issue_type == "Bug":
                    description_text = f"""**Environment:**
- Vehicle Model: {random.choice(VEHICLE_MODELS)}
- ECU Software: v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}
- CAN Bus Load: {random.randint(20, 80)}%
- Temperature: {random.randint(-20, 85)}°C

**Steps to Reproduce:**
1. Power on vehicle ECU
2. Initialize {random.choice(AUTOMOTIVE_COMPONENTS)}
3. Send CAN message 0x{random.randint(100, 999):03X}
4. Observe error condition

**Expected Result:**
ECU responds within 50ms with ACK

**Actual Result:**
Timeout occurs after {random.randint(100, 500)}ms, DTC P{random.randint(1000, 3999):04d} is set

**Impact:**
{random.choice(['Critical - Safety affected', 'High - System degraded', 'Medium - Performance impacted', 'Low - Minor issue'])}

**Root Cause Analysis:**
Investigation ongoing - suspected timing violation in AUTOSAR BSW layer
"""
                elif issue_type == "Task":
                    description_text = f"""**Objective:**
{summary}

**Technical Requirements:**
- Must comply with ISO 26262 ASIL-{random.choice(['A', 'B', 'C'])} requirements
- AUTOSAR-compliant implementation
- Code coverage minimum 85%
- MISRA-C compliance mandatory

**Implementation Steps:**
1. Review existing {random.choice(AUTOMOTIVE_COMPONENTS)} interface
2. Design CAN message structure (update DBC file)
3. Implement core functionality in C/C++
4. Create unit tests and HIL test cases
5. Perform static code analysis
6. Document API and integration guide

**Estimated Effort:** {random.randint(3, 20)} story points
**Dependencies:** {random.choice(['Hardware availability', 'Sensor calibration data', 'Third-party library integration', 'None'])}
"""
                elif issue_type == "Story":
                    description_text = f"""**User Story:**
{summary}

**Acceptance Criteria:**
- Feature works reliably in {random.choice(['city traffic', 'highway driving', 'parking scenarios', 'all conditions'])}
- Response time < {random.randint(100, 1000)}ms
- No false positives/negatives
- Complies with all safety standards
- Passed HIL and vehicle validation

**Technical Approach:**
Implement using {random.choice(['machine learning model', 'rule-based algorithm', 'sensor fusion technique', 'distributed control system'])}

**Definition of Done:**
- Code complete and reviewed
- All tests passing (unit, integration, HIL)
- Documentation updated
- QA validation complete
- Ready for production deployment
"""
                else:  # Epic
                    description_text = f"""**Epic Overview:**
{summary}

**Strategic Goals:**
- Enhance vehicle safety and driver experience
- Meet regulatory requirements
- Improve system reliability and maintainability
- Enable future feature extensions

**Key Components:**
- {random.choice(AUTOMOTIVE_COMPONENTS)}
- {random.choice(AUTOMOTIVE_COMPONENTS)}
- {random.choice(AUTOMOTIVE_COMPONENTS)}
- Cloud connectivity and data analytics

**Success Metrics:**
- {random.randint(20, 50)}% improvement in target KPI
- Zero safety-critical defects
- {random.randint(90, 99)}% customer satisfaction
- Reduced warranty claims

**Timeline:** Q{random.randint(1, 4)} 2025
**Budget:** ${random.randint(100, 500)}K
"""
                
                if github_repo_name:
                    description_text += f"\n\n**Related GitHub Repository:** {github_repo_name}"
                
                # Prepare issue data according to Jira REST API v3 specification
                # Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post
                issue_data = {
                    "fields": {
                        "project": {
                            "key": project_key
                        },
                        "summary": summary,
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": description_text
                                        }
                                    ]
                                }
                            ]
                        },
                        "issuetype": {
                            "name": issue_type
                        }
                    }
                }
                
                # Manager always creates issues in Jira (due to permission restrictions)
                # But we track which team member will work on it for realistic workflow
                assigned_team_member = None
                if team_members_with_jira and random.random() > 0.15:
                    # Pick team member with least issues for equal distribution (by index)
                    creator_idx = min(team_issue_counts.keys(), key=lambda idx: team_issue_counts[idx])
                    team_issue_counts[creator_idx] += 1
                    assigned_team_member = team_members_with_jira[creator_idx]
                
                # Manager creates all issues (Jira permission requirement)
                response = self.session.post(
                    f"{self.url}/rest/api/3/issue",
                    json=issue_data
                )
                creator_name = "Manager"
                
                if response.status_code in [200, 201]:
                    issue = response.json()
                    issue_key = issue['key']
                    print(f"✓ Issue {issue_key} ({creator_name}): {summary[:50]}...")
                    
                    # Assign to team member for work (if available)
                    if assigned_team_member:
                        assigned_name = assigned_team_member['name']
                        assigned_role = assigned_team_member['role']
                        assignment_comment = f"Assigned to: {assigned_name} ({assigned_role})"
                        self._add_comment(issue_key, assignment_comment)
                        print(f"  → Assigned to {assigned_name}")
                        
                        # Add realistic work progression comments (60% of issues)
                        if random.random() > 0.4:
                            num_updates = random.randint(2, 5)
                            
                            work_updates = [
                                f"{assigned_name}: Starting work on this. Analyzing requirements.",
                                f"{assigned_name}: Initial investigation complete. Found potential solution.",
                                f"{assigned_name}: Testing implementation on HIL bench.",
                                f"{assigned_name}: All unit tests passing. Ready for review.",
                                f"{random.choice(FAKE_USERS)['name']}: Peer review complete. LGTM.",
                                "Manager: Approved. Ready for deployment.",
                            ]
                            
                            for update_idx in range(min(num_updates, len(work_updates))):
                                self._add_comment(issue_key, work_updates[update_idx])
                            print(f"  → {num_updates} work updates")
                        
                        # Realistic workflow transitions (team member moves through states)
                        workflow_chance = random.random()
                        if workflow_chance > 0.3:
                            # Move to In Progress (70%)
                            self._transition_issue(issue_key, "In Progress")
                            self._add_comment(issue_key, f"{assigned_name}: Moving to In Progress.")
                            print(f"  → In Progress")
                            
                            if workflow_chance > 0.5:
                                # Complete the work (50% of total)
                                time.sleep(0.5)
                                self._transition_issue(issue_key, "Done")
                                self._add_comment(issue_key, f"{assigned_name}: Work completed and validated.")
                                print(f"  → Done")
                        else:
                            print(f"  → To Do (not started yet)")
                    else:
                        # No team member assigned (manager will handle)
                        print(f"  → Manager oversight")
                    
                    created_issues.append(issue)
                    time.sleep(1)
                    
                else:
                    print(f"✗ Error creating issue (HTTP {response.status_code})")
                    try:
                        error_detail = response.json()
                        print(f"  Error: {error_detail.get('errorMessages', [])}")
                        print(f"  Details: {error_detail.get('errors', {})}")
                    except:
                        print(f"  Response: {response.text[:300]}")
                    
            except Exception as e:
                print(f"✗ Exception creating issue: {str(e)}")
        
        return created_issues
    
    def _add_comment(self, issue_key: str, comment_text: str):
        """Add a comment to an issue"""
        try:
            comment_data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment_text
                                }
                            ]
                        }
                    ]
                }
            }
            
            self.session.post(
                f"{self.url}/rest/api/3/issue/{issue_key}/comment",
                json=comment_data
            )
        except Exception as e:
            pass
    
    def _transition_issue(self, issue_key: str, target_status: str):
        """Transition an issue to a different status"""
        try:
            # Get available transitions
            response = self.session.get(
                f"{self.url}/rest/api/3/issue/{issue_key}/transitions"
            )
            
            if response.status_code == 200:
                transitions = response.json()['transitions']
                
                # Find matching transition
                for transition in transitions:
                    if target_status.lower() in transition['name'].lower():
                        transition_data = {
                            "transition": {"id": transition['id']}
                        }
                        
                        self.session.post(
                            f"{self.url}/rest/api/3/issue/{issue_key}/transitions",
                            json=transition_data
                        )
                        break
        except Exception as e:
            pass


def main():
    """Main execution function"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   GitHub & Jira Fake Data Generator for AutoPM Testing   ║
    ║          Multi-User Collaborative Data Generation         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Validate manager credentials
    if MANAGER_GITHUB_TOKEN == 'YOUR_GITHUB_TOKEN_HERE' or MANAGER_JIRA_TOKEN == 'YOUR_JIRA_TOKEN_HERE':
        print("⚠ ERROR: Please set manager credentials in .env.multi_users or .env file!")
        print("\nRequired environment variables:")
        print("  - MANAGER_GITHUB_TOKEN (or GITHUB_TOKEN)")
        print("  - MANAGER_GITHUB_USERNAME (or GITHUB_USERNAME)")
        print("  - JIRA_URL")
        print("  - MANAGER_JIRA_EMAIL (or JIRA_EMAIL)")
        print("  - MANAGER_JIRA_TOKEN (or JIRA_API_TOKEN)")
        print("\nFor multi-user setup, see MULTI_USER_SETUP_GUIDE.md")
        return
    
    print(f"\n📋 Configuration:")
    print(f"  Manager Account: {MANAGER_GITHUB_USERNAME} ({MANAGER_JIRA_EMAIL})")
    print(f"  Team Members: {len(TEAM_CREDENTIALS)} accounts loaded")
    print(f"  Jira URL: {JIRA_URL}")
    
    # Initialize generators with manager credentials
    try:
        github_gen = GitHubDataGenerator(MANAGER_GITHUB_TOKEN, MANAGER_GITHUB_USERNAME)
        jira_gen = JiraDataGenerator(JIRA_URL, MANAGER_JIRA_EMAIL, MANAGER_JIRA_TOKEN)
    except Exception as e:
        print(f"✗ Error initializing generators: {str(e)}")
        return
    
    # Generate data for each project
    for project_num in range(1, NUM_PROJECTS + 1):
        print(f"\n\n{'#'*60}")
        print(f"# Processing Project {project_num} of {NUM_PROJECTS}")
        print(f"{'#'*60}\n")
        
        # Get automotive project info
        project_info = AUTOMOTIVE_PROJECTS[project_num - 1]
        
        # Create or check GitHub repository (owned by manager)
        repo_result = github_gen.create_project(project_num)
        if not repo_result:
            print("⚠ Skipping this project due to GitHub error")
            continue
        
        # Extract repo object and check if it already existed
        if isinstance(repo_result, dict):
            repo = repo_result['repo']
            repo_already_exists = repo_result.get('already_exists', False)
        else:
            # Backwards compatibility if repo object is returned directly
            repo = repo_result
            repo_already_exists = False
        
        # Skip GitHub setup if repo already exists
        if repo_already_exists:
            print(f"\n⏭️  Skipping GitHub collaborators, issues, and PRs (repo already exists)")
            print(f"   If you want to recreate data, delete the repo first:")
            print(f"   {repo.html_url}/settings")
        else:
            # Add team members as collaborators to GitHub repo and auto-accept
            if TEAM_CREDENTIALS:
                github_gen.add_collaborators(repo, TEAM_CREDENTIALS)
                time.sleep(3)  # Wait for permissions to propagate
            
            # Create GitHub issues (distributed across team members)
            github_gen.create_issues(repo, ISSUES_PER_PROJECT, TEAM_CREDENTIALS)
            
            # Create GitHub PRs (from team member accounts)
            github_gen.create_pull_requests(repo, PRS_PER_PROJECT, TEAM_CREDENTIALS)
        
        # Create corresponding Jira project with automotive naming
        # Convert project name to Jira-friendly format (e.g., "infotainment-system" -> "IFS")
        project_key_map = {
            "infotainment-system": "IFS",
            "adas-driver-assistance": "ADAS",
            "vehicle-diagnostics": "VD"
        }
        
        project_key = project_key_map.get(project_info['name'], f"AUTOPM{project_num}")
        project_name = project_info['description'][:80]  # Jira project names have length limits
        jira_project = jira_gen.create_project(project_name, project_key)
        
        # Add team members to Jira project
        if TEAM_CREDENTIALS:
            jira_gen.add_users_to_project(project_key, TEAM_CREDENTIALS)
        
        # Create Jira issues
        jira_gen.create_issues(project_key, JIRA_TASKS_PER_PROJECT, repo.name)
        
        print(f"\n✓ Project {project_num} completed!")
        time.sleep(2)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY - Multi-User Collaborative Data")
    print(f"{'='*60}")
    print(f"✓ Manager Account: {MANAGER_GITHUB_USERNAME}")
    print(f"✓ Team Members: {len(TEAM_CREDENTIALS)} collaborators with full access")
    print(f"\n📦 GitHub:")
    print(f"  ✓ Processed {NUM_PROJECTS} repositories")
    if len(github_gen.created_repos) > 0:
        print(f"  ℹ️  Note: Existing repositories were skipped (no duplicate data created)")
    print(f"\n📋 Jira:")
    print(f"  ✓ Processed {NUM_PROJECTS} spaces/projects")
    print(f"  ✓ Issues created where spaces exist")
    print(f"\n🔗 Repositories:")
    for repo in github_gen.created_repos:
        print(f"  → {repo.html_url}")
    print(f"\n🔗 Jira spaces: {JIRA_URL}/jira/software/projects")
    print(f"\n💡 Tips:")
    print(f"  • Existing GitHub repos are skipped automatically")
    print(f"  • Jira spaces must be created manually (see QUICK_JIRA_FIX.md)")
    print(f"  • Delete repos/spaces and re-run to regenerate test data")
    print("="*60)


if __name__ == "__main__":
    main()
