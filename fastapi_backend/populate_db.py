"""
Populate Database with Seed Data
Run this script after initializing the database to add default users and projects
"""
import sys
import argparse
from datetime import datetime, date, timedelta
from database import SessionLocal, init_db
from models.database_models import (
    ProjectMetadata, EmployeeProfile, JiraTask, GitHubActivity,
    ResourceAllocation, TeamCommunicationLog, HistoricalProjectPerformance,
    TaskDependency
)
from utils.password import get_password_hash
from models.user import User, UserRole


def populate_employees(db):
    """Create employee profiles"""
    print("\n📋 Creating employees...")
    
    # Manager
    manager = EmployeeProfile(
        employee_id="EMP001",
        name="AdhivP",
        email="adhivp04@gmail.com",
        password_hash=get_password_hash("AutoPM2025!"),
        role="Project Manager / Product Owner",
        team="Management",
        skills=["Project Management", "Agile", "JIRA", "GitHub"],
        manager_id=None,
        github_username="Adhivp",
        jira_email="adhivp04@gmail.com",
        is_active=True
    )
    db.add(manager)
    
    # Team members
    team_members = [
        {
            "employee_id": "EMP002",
            "name": "Sarah Chen",
            "email": "sarahchen.autopm@gmail.com",
            "role": "Embedded Systems Engineer",
            "team": "Infotainment",
            "skills": ["AUTOSAR", "C++", "CANoe", "Embedded Systems"],
            "github_username": "sarahchen-autopm",
            "jira_email": "sarahchen.autopm@gmail.com"
        },
        {
            "employee_id": "EMP003",
            "name": "Marcus Weber",
            "email": "marcusweber.autopm@gmail.com",
            "role": "Vehicle Software Architect",
            "team": "Infotainment",
            "skills": ["AUTOSAR", "C++", "Android Automotive", "Kotlin"],
            "github_username": "marcusweber-autopm",
            "jira_email": "marcusweber.autopm@gmail.com"
        },
        {
            "employee_id": "EMP004",
            "name": "Priya Patel",
            "email": "priyapatel.autopm@gmail.com",
            "role": "ADAS Developer",
            "team": "Safety Systems",
            "skills": ["Python", "ROS2", "TensorFlow", "C++"],
            "github_username": "priyapatel-autopm",
            "jira_email": "priyapatel.autopm@gmail.com"
        },
        {
            "employee_id": "EMP005",
            "name": "Johan Schmidt",
            "email": "johanschmidt.autopm@gmail.com",
            "role": "Automotive QA Engineer",
            "team": "Testing",
            "skills": ["Jenkins", "Python", "Test Automation", "ISO 26262"],
            "github_username": "johanschmidt-autopm",
            "jira_email": "johanschmidt.autopm@gmail.com"
        },
        {
            "employee_id": "EMP006",
            "name": "Elena Rodriguez",
            "email": "elenarodriguez.autopm@gmail.com",
            "role": "ADAS Developer",
            "team": "Safety Systems",
            "skills": ["Python", "ROS2", "Computer Vision", "MATLAB"],
            "github_username": "elenarodriguez-autopm",
            "jira_email": "elenarodriguez.autopm@gmail.com"
        }
    ]
    
    for member_data in team_members:
        member = EmployeeProfile(
            **member_data,
            password_hash=get_password_hash("AutoPM2025!"),
            manager_id="EMP001",
            is_active=True
        )
        db.add(member)
    
    # Also create corresponding User records for authentication
    # Manager user
    try:
        db.flush()  # flush pending EmployeeProfile inserts so emails/ids are available
    except Exception:
        pass

    existing_manager_user = db.query(User).filter(User.email == "adhivp04@gmail.com").first()
    if not existing_manager_user:
        manager_user = User(
            email="adhivp04@gmail.com",
            hashed_password=get_password_hash("AutoPM2025!"),
            full_name="Adhiv P",
            role=UserRole.MANAGER,
            is_active=1
        )
        db.add(manager_user)

    # Team member users
    for member_data in team_members:
        email = member_data.get("email")
        name = member_data.get("name")
        existing = db.query(User).filter(User.email == email).first()
        if not existing:
            user = User(
                email=email,
                hashed_password=get_password_hash("AutoPM2025!"),
                full_name=name,
                role=UserRole.MEMBER,
                is_active=1
            )
            db.add(user)

    db.commit()
    print(f"✓ Created {len(team_members) + 1} employees and corresponding user accounts")


def populate_projects(db):
    """Create project metadata"""
    print("\n📦 Creating projects...")
    
    projects = [
        {
            "project_id": "AUTOSW-2025-IFS",
            "project_name": "Infotainment System",
            "start_date": date(2025, 1, 15),
            "target_end_date": date(2025, 12, 31),
            "compliance_standards": ["ISO 26262", "ASPICE Level 2"],
            "critical_modules": ["Voice Control", "Wireless Android Auto", "OTA Updates"],
            "team_lead_id": "EMP001",
            "status": "In Progress",
            "github_repo_name": "infotainment-system-autopmtestproject",
            "jira_project_key": "IFS"
        },
        {
            "project_id": "AUTOSW-2025-ADAS",
            "project_name": "ADAS Driver Assistance",
            "start_date": date(2025, 2, 1),
            "target_end_date": date(2026, 1, 31),
            "compliance_standards": ["ISO 26262 ASIL-D", "ASPICE Level 3"],
            "critical_modules": ["Adaptive Cruise Control", "Lane Keep Assist", "Emergency Braking"],
            "team_lead_id": "EMP001",
            "status": "In Progress",
            "github_repo_name": "adas-driver-assistance-autopmtestproject",
            "jira_project_key": "ADAS"
        },
        {
            "project_id": "AUTOSW-2025-VD",
            "project_name": "Vehicle Diagnostics",
            "start_date": date(2025, 3, 1),
            "target_end_date": date(2025, 11, 30),
            "compliance_standards": ["ISO 14229", "ISO 15765"],
            "critical_modules": ["OBD-II Data Collection", "Predictive Maintenance", "Remote Diagnostics"],
            "team_lead_id": "EMP001",
            "status": "Planning",
            "github_repo_name": "vehicle-diagnostics-autopmtestproject",
            "jira_project_key": "VD"
        }
    ]
    
    for proj_data in projects:
        project = ProjectMetadata(**proj_data)
        db.add(project)
    
    db.commit()
    print(f"✓ Created {len(projects)} projects")


def populate_jira_tasks(db):
    """Create sample Jira tasks"""
    print("\n📝 Creating Jira tasks...")
    
    tasks = [
        # Infotainment System Tasks
        {
            "issue_id": "IFS-1",
            "project_id": "AUTOSW-2025-IFS",
            "summary": "Implement CAN message parser for ECU communication",
            "description": "Develop a robust CAN message parser to handle ECU communication protocols",
            "issue_type": "Task",
            "assignee_id": "EMP002",
            "status": "In Progress",
            "priority": "High",
            "story_points": 8,
            "created_date": datetime(2025, 1, 20, 9, 0, 0),
            "updated_date": datetime(2025, 1, 25, 14, 30, 0),
            "labels": ["CAN-bus", "AUTOSAR"]
        },
        {
            "issue_id": "IFS-2",
            "project_id": "AUTOSW-2025-IFS",
            "summary": "Voice-activated navigation and controls",
            "description": "Implement voice recognition for navigation commands",
            "issue_type": "Story",
            "assignee_id": "EMP003",
            "status": "To Do",
            "priority": "Medium",
            "story_points": 13,
            "created_date": datetime(2025, 1, 22, 10, 0, 0),
            "updated_date": datetime(2025, 1, 22, 10, 0, 0),
            "depends_on": ["IFS-1"],
            "labels": ["enhancement", "voice-control"]
        },
        {
            "issue_id": "IFS-3",
            "project_id": "AUTOSW-2025-IFS",
            "summary": "CAN bus communication timeout in Gateway Module",
            "description": "Intermittent timeouts detected when communicating with gateway",
            "issue_type": "Bug",
            "assignee_id": "EMP002",
            "status": "In Progress",
            "priority": "Critical",
            "story_points": 5,
            "created_date": datetime(2025, 1, 23, 8, 30, 0),
            "updated_date": datetime(2025, 1, 24, 16, 0, 0),
            "labels": ["bug", "CAN-bus", "safety-critical"]
        },
        # ADAS Tasks
        {
            "issue_id": "ADAS-1",
            "project_id": "AUTOSW-2025-ADAS",
            "summary": "Develop complete ADAS Level 2+ automation system",
            "description": "Epic for implementing full Level 2+ autonomous driving features",
            "issue_type": "Epic",
            "assignee_id": "EMP004",
            "status": "In Progress",
            "priority": "Critical",
            "story_points": 0,
            "created_date": datetime(2025, 2, 1, 9, 0, 0),
            "updated_date": datetime(2025, 2, 5, 11, 0, 0),
            "labels": ["AUTOSAR", "ISO26262"]
        },
        {
            "issue_id": "ADAS-2",
            "project_id": "AUTOSW-2025-ADAS",
            "summary": "Implement Adaptive Cruise Control with stop-and-go",
            "description": "Develop ACC system with full stop-and-go capability",
            "issue_type": "Task",
            "assignee_id": "EMP004",
            "status": "In Progress",
            "priority": "High",
            "story_points": 13,
            "created_date": datetime(2025, 2, 2, 10, 0, 0),
            "updated_date": datetime(2025, 2, 6, 15, 30, 0),
            "parent_issue_id": "ADAS-1",
            "labels": ["enhancement", "safety-critical"]
        },
        {
            "issue_id": "ADAS-3",
            "project_id": "AUTOSW-2025-ADAS",
            "summary": "Radar sensor showing false positives in rain",
            "description": "Radar sensor detecting phantom objects during heavy rain",
            "issue_type": "Bug",
            "assignee_id": "EMP006",
            "status": "To Do",
            "priority": "High",
            "story_points": 8,
            "created_date": datetime(2025, 2, 3, 14, 0, 0),
            "updated_date": datetime(2025, 2, 3, 14, 0, 0),
            "labels": ["bug", "testing"]
        },
        # Vehicle Diagnostics Tasks
        {
            "issue_id": "VD-1",
            "project_id": "AUTOSW-2025-VD",
            "summary": "Setup real-time OBD-II data collection",
            "description": "Implement OBD-II data collection with CAN bus integration",
            "issue_type": "Task",
            "assignee_id": "EMP003",
            "status": "To Do",
            "priority": "High",
            "story_points": 8,
            "created_date": datetime(2025, 3, 1, 9, 0, 0),
            "updated_date": datetime(2025, 3, 1, 9, 0, 0),
            "labels": ["CAN-bus", "testing"]
        },
        {
            "issue_id": "VD-2",
            "project_id": "AUTOSW-2025-VD",
            "summary": "Develop predictive maintenance algorithms",
            "description": "Create ML models for predictive maintenance based on telemetry",
            "issue_type": "Story",
            "assignee_id": "EMP004",
            "status": "To Do",
            "priority": "Medium",
            "story_points": 13,
            "created_date": datetime(2025, 3, 2, 10, 0, 0),
            "updated_date": datetime(2025, 3, 2, 10, 0, 0),
            "depends_on": ["VD-1"],
            "labels": ["enhancement"]
        }
    ]
    
    for task_data in tasks:
        task = JiraTask(**task_data)
        db.add(task)
    
    db.commit()
    print(f"✓ Created {len(tasks)} Jira tasks")


def populate_github_activity(db):
    """Create sample GitHub pull requests"""
    print("\n🔀 Creating GitHub pull requests...")
    
    prs = [
        {
            "pr_id": "infotainment-system-autopmtestproject/PR#1",
            "project_id": "AUTOSW-2025-IFS",
            "title": "feat: Add CAN message parser implementation",
            "author_id": "EMP002",
            "reviewers": ["EMP003", "EMP005"],
            "created_at": datetime(2025, 1, 24, 10, 0, 0),
            "status": "Open",
            "associated_issue_id": "IFS-1",
            "changed_files": 5,
            "additions": 234,
            "deletions": 12,
            "comments_count": 3,
            "build_status": "Pending",
            "test_coverage_delta": 2.5
        },
        {
            "pr_id": "adas-driver-assistance-autopmtestproject/PR#1",
            "project_id": "AUTOSW-2025-ADAS",
            "title": "feat: Implement ACC stop-and-go logic",
            "author_id": "EMP004",
            "reviewers": ["EMP006", "EMP005"],
            "created_at": datetime(2025, 2, 5, 14, 0, 0),
            "status": "Open",
            "associated_issue_id": "ADAS-2",
            "changed_files": 8,
            "additions": 456,
            "deletions": 34,
            "comments_count": 5,
            "build_status": "Success",
            "test_coverage_delta": 3.2
        }
    ]
    
    for pr_data in prs:
        pr = GitHubActivity(**pr_data)
        db.add(pr)
    
    db.commit()
    print(f"✓ Created {len(prs)} GitHub PRs")


def populate_resource_allocation(db):
    """Create resource allocation records"""
    print("\n⏱ Creating resource allocations...")
    
    allocations = [
        {
            "allocation_id": "ALLOC-001",
            "employee_id": "EMP002",
            "project_id": "AUTOSW-2025-IFS",
            "week_start_date": date(2025, 1, 20),
            "overtime_hours": 5.0,
            "planned_hours": 40.0,
            "logged_hours": 42.0,
            "task_ids": ["IFS-1", "IFS-3"]
        },
        {
            "allocation_id": "ALLOC-002",
            "employee_id": "EMP003",
            "project_id": "AUTOSW-2025-IFS",
            "week_start_date": date(2025, 1, 20),
            "overtime_hours": 0.0,
            "planned_hours": 40.0,
            "logged_hours": 38.0,
            "task_ids": ["IFS-2"]
        },
        {
            "allocation_id": "ALLOC-003",
            "employee_id": "EMP004",
            "project_id": "AUTOSW-2025-ADAS",
            "week_start_date": date(2025, 2, 3),
            "overtime_hours": 3.0,
            "planned_hours": 40.0,
            "logged_hours": 43.0,
            "task_ids": ["ADAS-1", "ADAS-2"]
        },
        {
            "allocation_id": "ALLOC-004",
            "employee_id": "EMP006",
            "project_id": "AUTOSW-2025-ADAS",
            "week_start_date": date(2025, 2, 3),
            "overtime_hours": 0.0,
            "planned_hours": 40.0,
            "logged_hours": 35.0,
            "task_ids": ["ADAS-3"]
        }
    ]
    
    for alloc_data in allocations:
        allocation = ResourceAllocation(**alloc_data)
        db.add(allocation)
    
    db.commit()
    print(f"✓ Created {len(allocations)} resource allocations")


def populate_communication_logs(db):
    """Create communication logs"""
    print("\n💬 Creating communication logs...")
    
    messages = [
        {
            "message_id": "MSG-001",
            "project_id": "AUTOSW-2025-IFS",
            "sender_id": "EMP002",
            "timestamp": datetime(2025, 1, 24, 15, 30, 0),
            "message_text": "CAN parser blocked - waiting for ECU firmware specs from vendor",
            "is_blocker_signal": True
        },
        {
            "message_id": "MSG-002",
            "project_id": "AUTOSW-2025-ADAS",
            "sender_id": "EMP004",
            "timestamp": datetime(2025, 2, 5, 9, 0, 0),
            "message_text": "ACC implementation on track, code review needed",
            "is_blocker_signal": False
        },
        {
            "message_id": "MSG-003",
            "project_id": "AUTOSW-2025-ADAS",
            "sender_id": "EMP006",
            "timestamp": datetime(2025, 2, 6, 11, 0, 0),
            "message_text": "Radar calibration delayed due to weather testing equipment unavailable",
            "is_blocker_signal": True
        },
        {
            "message_id": "MSG-004",
            "project_id": "AUTOSW-2025-IFS",
            "sender_id": "EMP003",
            "timestamp": datetime(2025, 1, 25, 16, 0, 0),
            "message_text": "Voice control integration complete, ready for testing",
            "is_blocker_signal": False
        }
    ]
    
    for msg_data in messages:
        message = TeamCommunicationLog(**msg_data)
        db.add(message)
    
    db.commit()
    print(f"✓ Created {len(messages)} communication logs")


def populate_historical_performance(db):
    """Create historical project performance data"""
    print("\n📊 Creating historical performance data...")
    
    historical = [
        {
            "historical_project_id": "HIST-001",
            "project_name": "Powertrain Control Module 2024",
            "original_end_date": date(2024, 6, 30),
            "actual_end_date": date(2024, 8, 15),
            "delay_days": 46,
            "defect_density": 2.3,
            "integration_issues_count": 8,
            "root_causes": ["late_dependency", "resource_shortage"],
            "compliance_audit_result": "Minor NC"
        },
        {
            "historical_project_id": "HIST-002",
            "project_name": "Battery Management System 2024",
            "original_end_date": date(2024, 9, 30),
            "actual_end_date": date(2024, 9, 28),
            "delay_days": -2,
            "defect_density": 1.1,
            "integration_issues_count": 2,
            "root_causes": [],
            "compliance_audit_result": "Pass"
        },
        {
            "historical_project_id": "HIST-003",
            "project_name": "Vehicle Gateway Module 2024",
            "original_end_date": date(2024, 12, 15),
            "actual_end_date": date(2025, 1, 20),
            "delay_days": 36,
            "defect_density": 3.5,
            "integration_issues_count": 12,
            "root_causes": ["ambiguous_req", "late_dependency", "integration_complexity"],
            "compliance_audit_result": "Major NC"
        }
    ]
    
    for hist_data in historical:
        hist = HistoricalProjectPerformance(**hist_data)
        db.add(hist)
    
    db.commit()
    print(f"✓ Created {len(historical)} historical records")


def populate_task_dependencies(db):
    """Create task dependencies"""
    print("\n🔗 Creating task dependencies...")
    
    dependencies = [
        {
            "dependency_id": "DEP-001",
            "dependent_task_id": "IFS-2",
            "blocking_task_id": "IFS-1",
            "dependency_type": "Internal",
            "expected_ready_date": date(2025, 1, 28),
            "status": "At Risk"
        },
        {
            "dependency_id": "DEP-002",
            "dependent_task_id": "VD-2",
            "blocking_task_id": "VD-1",
            "dependency_type": "Internal",
            "expected_ready_date": date(2025, 3, 10),
            "status": "On Track"
        },
        {
            "dependency_id": "DEP-003",
            "dependent_task_id": "ADAS-2",
            "blocking_task_id": "ADAS-1",
            "dependency_type": "Internal",
            "expected_ready_date": date(2025, 2, 15),
            "status": "On Track"
        }
    ]
    
    for dep_data in dependencies:
        dep = TaskDependency(**dep_data)
        db.add(dep)
    
    db.commit()
    print(f"✓ Created {len(dependencies)} task dependencies")


def main(force: bool = False):
    """Main execution"""
    print("="*60)
    print("AutoPM Database Population Script")
    print("="*60)
    
    # Initialize database
    print("\n🔧 Initializing database...")
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_employees = db.query(EmployeeProfile).count()
        if existing_employees > 0:
            if not force:
                print("\n⚠️  Database already contains data!")
                response = input("Do you want to clear and repopulate? (yes/no): ")
                if response.lower() != 'yes':
                    print("❌ Aborted")
                    return
            else:
                print("\n⚠️  Database already contains data - proceeding because --force was supplied")

            # Clear existing data (in reverse order of dependencies)
            print("\n🗑️  Clearing existing data...")
            db.query(TaskDependency).delete()
            db.query(HistoricalProjectPerformance).delete()
            db.query(TeamCommunicationLog).delete()
            db.query(ResourceAllocation).delete()
            db.query(GitHubActivity).delete()
            db.query(JiraTask).delete()
            db.query(ProjectMetadata).delete()
            db.query(EmployeeProfile).delete()
            # Also clear users table to avoid duplicates
            try:
                from models.user import User
                db.query(User).delete()
            except Exception:
                pass
            db.commit()
            print("✓ Existing data cleared")
        
        # Populate all tables
        populate_employees(db)
        populate_projects(db)
        populate_jira_tasks(db)
        populate_github_activity(db)
        populate_resource_allocation(db)
        populate_communication_logs(db)
        populate_historical_performance(db)
        populate_task_dependencies(db)
        
        print("\n" + "="*60)
        print("✅ Database population completed successfully!")
        print("="*60)
        print("\n📝 Default Login Credentials:")
        print("   Email: adhivp04@gmail.com")
        print("   Password: AutoPM2025!")
        print("\n🚀 You can now start the FastAPI server:")
        print("   python main.py")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Populate AutoPM database with seed data')
    parser.add_argument('--force', action='store_true', help='Clear existing data and repopulate without prompt')
    args = parser.parse_args()
    main(force=args.force)
