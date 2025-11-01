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
