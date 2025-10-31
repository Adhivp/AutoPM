-- ============================================================================
-- AutoPM Database Schema
-- Comprehensive schema for Project Management with GitHub & Jira Integration
-- ============================================================================

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS task_dependencies CASCADE;
DROP TABLE IF EXISTS historical_project_performance CASCADE;
DROP TABLE IF EXISTS team_communication_logs CASCADE;
DROP TABLE IF EXISTS resource_allocation CASCADE;
DROP TABLE IF EXISTS github_activity CASCADE;
DROP TABLE IF EXISTS jira_tasks CASCADE;
DROP TABLE IF EXISTS employee_profile CASCADE;
DROP TABLE IF EXISTS project_metadata CASCADE;

-- ============================================================================
-- 1. PROJECT METADATA
-- ============================================================================
CREATE TABLE project_metadata (
    project_id VARCHAR(100) PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    start_date DATE,
    target_end_date DATE,
    actual_end_date DATE,
    compliance_standards JSON,  -- Array of standards like ["ISO 26262", "ASPICE Level 2"]
    critical_modules JSON,  -- Array of critical components
    team_lead_id VARCHAR(100),
    status VARCHAR(50) CHECK (status IN ('Planning', 'In Progress', 'On Hold', 'Completed')),
    github_repo_name VARCHAR(255),
    jira_project_key VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_project_status ON project_metadata(status);
CREATE INDEX idx_project_team_lead ON project_metadata(team_lead_id);

-- ============================================================================
-- 2. EMPLOYEE PROFILE (Team Members)
-- ============================================================================
CREATE TABLE employee_profile (
    employee_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- For login authentication
    role VARCHAR(100),  -- e.g., "Embedded SW Engineer", "Test Lead"
    team VARCHAR(100),  -- e.g., "Powertrain", "Infotainment"
    skills JSON,  -- Array of skills like ["AUTOSAR", "C++", "CANoe"]
    manager_id VARCHAR(100),
    github_username VARCHAR(100),
    jira_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES employee_profile(employee_id) ON DELETE SET NULL
);

CREATE INDEX idx_employee_role ON employee_profile(role);
CREATE INDEX idx_employee_team ON employee_profile(team);
CREATE INDEX idx_employee_manager ON employee_profile(manager_id);
CREATE INDEX idx_employee_github ON employee_profile(github_username);

-- ============================================================================
-- 3. JIRA TASKS & ISSUES
-- ============================================================================
CREATE TABLE jira_tasks (
    issue_id VARCHAR(100) PRIMARY KEY,  -- Jira key like "ECU-123"
    project_id VARCHAR(100) NOT NULL,
    summary VARCHAR(500),
    description TEXT,
    issue_type VARCHAR(50) CHECK (issue_type IN ('Story', 'Bug', 'Task', 'Epic')),
    assignee_id VARCHAR(100),
    status VARCHAR(50) CHECK (status IN ('To Do', 'In Progress', 'In Review', 'Done')),
    priority VARCHAR(50) CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    story_points INT,
    created_date TIMESTAMP,
    updated_date TIMESTAMP,
    resolved_date TIMESTAMP,
    parent_issue_id VARCHAR(100),
    depends_on JSON,  -- Array of issue_ids
    labels JSON,  -- Array of labels
    github_pr_id VARCHAR(100),  -- Link to associated GitHub PR
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project_metadata(project_id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES employee_profile(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (parent_issue_id) REFERENCES jira_tasks(issue_id) ON DELETE SET NULL
);

CREATE INDEX idx_jira_project ON jira_tasks(project_id);
CREATE INDEX idx_jira_assignee ON jira_tasks(assignee_id);
CREATE INDEX idx_jira_status ON jira_tasks(status);
CREATE INDEX idx_jira_type ON jira_tasks(issue_type);
CREATE INDEX idx_jira_parent ON jira_tasks(parent_issue_id);

-- ============================================================================
-- 4. GITHUB ACTIVITY
-- ============================================================================
CREATE TABLE github_activity (
    pr_id VARCHAR(100) PRIMARY KEY,  -- Format: "repo/PR#456"
    project_id VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    author_id VARCHAR(100),
    reviewers JSON,  -- Array of employee_ids
    created_at TIMESTAMP,
    merged_at TIMESTAMP,
    closed_at TIMESTAMP,
    status VARCHAR(50) CHECK (status IN ('Open', 'Merged', 'Closed')),
    associated_issue_id VARCHAR(100),  -- Links to Jira issue
    changed_files INT DEFAULT 0,
    additions INT DEFAULT 0,
    deletions INT DEFAULT 0,
    comments_count INT DEFAULT 0,
    build_status VARCHAR(50) CHECK (build_status IN ('Success', 'Failed', 'Pending')),
    test_coverage_delta DECIMAL(5,2),
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project_metadata(project_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES employee_profile(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (associated_issue_id) REFERENCES jira_tasks(issue_id) ON DELETE SET NULL
);

CREATE INDEX idx_github_project ON github_activity(project_id);
CREATE INDEX idx_github_author ON github_activity(author_id);
CREATE INDEX idx_github_status ON github_activity(status);
CREATE INDEX idx_github_issue ON github_activity(associated_issue_id);

-- ============================================================================
-- 5. RESOURCE ALLOCATION & TIME TRACKING
-- ============================================================================
CREATE TABLE resource_allocation (
    allocation_id VARCHAR(100) PRIMARY KEY,
    employee_id VARCHAR(100) NOT NULL,
    project_id VARCHAR(100) NOT NULL,
    week_start_date DATE NOT NULL,
    overtime_hours DECIMAL(5,2) DEFAULT 0,
    planned_hours DECIMAL(5,2) DEFAULT 0,
    logged_hours DECIMAL(5,2) DEFAULT 0,
    task_ids JSON,  -- Array of Jira issue_ids worked on
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employee_profile(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES project_metadata(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_allocation_employee ON resource_allocation(employee_id);
CREATE INDEX idx_allocation_project ON resource_allocation(project_id);
CREATE INDEX idx_allocation_week ON resource_allocation(week_start_date);

-- ============================================================================
-- 6. TEAM COMMUNICATION LOGS
-- ============================================================================
CREATE TABLE team_communication_logs (
    message_id VARCHAR(100) PRIMARY KEY,
    project_id VARCHAR(100) NOT NULL,
    sender_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    message_text TEXT,  -- Short text, ≤200 chars
    is_blocker_signal BOOLEAN DEFAULT FALSE,  -- Keywords: "blocked", "waiting", "delay", "urgent"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project_metadata(project_id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES employee_profile(employee_id) ON DELETE CASCADE
);

CREATE INDEX idx_comm_project ON team_communication_logs(project_id);
CREATE INDEX idx_comm_sender ON team_communication_logs(sender_id);
CREATE INDEX idx_comm_timestamp ON team_communication_logs(timestamp);
CREATE INDEX idx_comm_blocker ON team_communication_logs(is_blocker_signal);

-- ============================================================================
-- 7. HISTORICAL PROJECT PERFORMANCE
-- ============================================================================
CREATE TABLE historical_project_performance (
    historical_project_id VARCHAR(100) PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    original_end_date DATE,
    actual_end_date DATE,
    delay_days INT,  -- Calculated: actual - original
    defect_density DECIMAL(10,2),  -- Bugs per KLOC or per module
    integration_issues_count INT DEFAULT 0,
    root_causes JSON,  -- Array like ["late_dependency", "resource_shortage"]
    compliance_audit_result VARCHAR(50) CHECK (compliance_audit_result IN ('Pass', 'Minor NC', 'Major NC')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_historical_delay ON historical_project_performance(delay_days);
CREATE INDEX idx_historical_audit ON historical_project_performance(compliance_audit_result);

-- ============================================================================
-- 8. TASK DEPENDENCIES
-- ============================================================================
CREATE TABLE task_dependencies (
    dependency_id VARCHAR(100) PRIMARY KEY,
    dependent_task_id VARCHAR(100) NOT NULL,  -- Task that is waiting
    blocking_task_id VARCHAR(100) NOT NULL,  -- Task that must finish first
    dependency_type VARCHAR(50) CHECK (dependency_type IN ('Internal', 'External')),
    expected_ready_date DATE,
    status VARCHAR(50) CHECK (status IN ('On Track', 'At Risk', 'Delayed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dependent_task_id) REFERENCES jira_tasks(issue_id) ON DELETE CASCADE,
    FOREIGN KEY (blocking_task_id) REFERENCES jira_tasks(issue_id) ON DELETE CASCADE
);

CREATE INDEX idx_dependency_dependent ON task_dependencies(dependent_task_id);
CREATE INDEX idx_dependency_blocking ON task_dependencies(blocking_task_id);
CREATE INDEX idx_dependency_status ON task_dependencies(status);

-- ============================================================================
-- CREATE VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Active Projects with Team Lead Info
CREATE VIEW v_active_projects AS
SELECT 
    p.project_id,
    p.project_name,
    p.status,
    p.start_date,
    p.target_end_date,
    e.name as team_lead_name,
    e.email as team_lead_email,
    p.github_repo_name,
    p.jira_project_key
FROM project_metadata p
LEFT JOIN employee_profile e ON p.team_lead_id = e.employee_id
WHERE p.status IN ('Planning', 'In Progress');

-- View: Employee Workload Summary
CREATE VIEW v_employee_workload AS
SELECT 
    e.employee_id,
    e.name,
    e.role,
    e.team,
    COUNT(DISTINCT j.issue_id) as assigned_tasks,
    COUNT(DISTINCT g.pr_id) as open_prs,
    SUM(r.logged_hours) as total_hours_logged
FROM employee_profile e
LEFT JOIN jira_tasks j ON e.employee_id = j.assignee_id AND j.status != 'Done'
LEFT JOIN github_activity g ON e.employee_id = g.author_id AND g.status = 'Open'
LEFT JOIN resource_allocation r ON e.employee_id = r.employee_id
GROUP BY e.employee_id, e.name, e.role, e.team;

-- View: Task Status Summary by Project
CREATE VIEW v_project_task_summary AS
SELECT 
    p.project_id,
    p.project_name,
    COUNT(j.issue_id) as total_tasks,
    SUM(CASE WHEN j.status = 'Done' THEN 1 ELSE 0 END) as completed_tasks,
    SUM(CASE WHEN j.status = 'In Progress' THEN 1 ELSE 0 END) as in_progress_tasks,
    SUM(CASE WHEN j.status = 'To Do' THEN 1 ELSE 0 END) as todo_tasks,
    SUM(CASE WHEN j.priority = 'Critical' THEN 1 ELSE 0 END) as critical_tasks
FROM project_metadata p
LEFT JOIN jira_tasks j ON p.project_id = j.project_id
GROUP BY p.project_id, p.project_name;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
