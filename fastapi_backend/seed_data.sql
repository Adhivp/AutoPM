-- ============================================================================
-- AutoPM Seed Data
-- Based on generate_fake_data.py - Automotive Team Members & Projects
-- ============================================================================

-- ============================================================================
-- 1. EMPLOYEE PROFILE - Team Members
-- Password: "AutoPM2025!" for all users (hashed with bcrypt)
-- ============================================================================

-- Manager (Adhiv P)
INSERT INTO employee_profile (employee_id, name, email, password_hash, role, team, skills, manager_id, github_username, jira_email, is_active) VALUES
('EMP001', 'Adhiv P', 'adhivp04@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aqaLRt.5JI0K', 'Project Manager / Product Owner', 'Management', '["Project Management", "Agile", "JIRA", "GitHub"]', NULL, 'Adhivp', 'adhivp04@gmail.com', TRUE);

-- Team Members (collaborators)
INSERT INTO employee_profile (employee_id, name, email, password_hash, role, team, skills, manager_id, github_username, jira_email, is_active) VALUES
('EMP002', 'Sarah Chen', 'sarahchen.autopm@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aqaLRt.5JI0K', 'Embedded Systems Engineer', 'Infotainment', '["AUTOSAR", "C++", "CANoe", "Embedded Systems"]', 'EMP001', 'sarahchen-autopm', 'sarahchen.autopm@gmail.com', TRUE),
('EMP003', 'Marcus Weber', 'marcusweber.autopm@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aqaLRt.5JI0K', 'Vehicle Software Architect', 'Infotainment', '["AUTOSAR", "C++", "Android Automotive", "Kotlin"]', 'EMP001', 'marcusweber-autopm', 'marcusweber.autopm@gmail.com', TRUE),
('EMP004', 'Priya Patel', 'priyapatel.autopm@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aqaLRt.5JI0K', 'ADAS Developer', 'Safety Systems', '["Python", "ROS2", "TensorFlow", "C++"]', 'EMP001', 'priyapatel-autopm', 'priyapatel.autopm@gmail.com', TRUE),
('EMP005', 'Johan Schmidt', 'johanschmidt.autopm@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aqaLRt.5JI0K', 'Automotive QA Engineer', 'Testing', '["Jenkins", "Python", "Test Automation", "ISO 26262"]', 'EMP001', 'johanschmidt-autopm', 'johanschmidt.autopm@gmail.com', TRUE),
('EMP006', 'Elena Rodriguez', 'elenarodriguez.autopm@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5aqaLRt.5JI0K', 'ADAS Developer', 'Safety Systems', '["Python", "ROS2", "Computer Vision", "MATLAB"]', 'EMP001', 'elenarodriguez-autopm', 'elenarodriguez.autopm@gmail.com', TRUE);

-- ============================================================================
-- 2. PROJECT METADATA - Automotive Projects
-- ============================================================================

INSERT INTO project_metadata (project_id, project_name, start_date, target_end_date, actual_end_date, compliance_standards, critical_modules, team_lead_id, status, github_repo_name, jira_project_key) VALUES
('AUTOSW-2025-IFS', 'Infotainment System', '2025-01-15', '2025-12-31', NULL, '["ISO 26262", "ASPICE Level 2"]', '["Voice Control", "Wireless Android Auto", "OTA Updates"]', 'EMP001', 'In Progress', 'infotainment-system-autopmtestproject', 'IFS'),
('AUTOSW-2025-ADAS', 'ADAS Driver Assistance', '2025-02-01', '2026-01-31', NULL, '["ISO 26262 ASIL-D", "ASPICE Level 3"]', '["Adaptive Cruise Control", "Lane Keep Assist", "Emergency Braking"]', 'EMP001', 'In Progress', 'adas-driver-assistance-autopmtestproject', 'ADAS'),
('AUTOSW-2025-VD', 'Vehicle Diagnostics', '2025-03-01', '2025-11-30', NULL, '["ISO 14229", "ISO 15765"]', '["OBD-II Data Collection", "Predictive Maintenance", "Remote Diagnostics"]', 'EMP001', 'Planning', 'vehicle-diagnostics-autopmtestproject', 'VD');

-- ============================================================================
-- 3. JIRA TASKS - Sample Tasks (to be populated by sync)
-- Note: Real data will be synced from Jira API
-- ============================================================================

INSERT INTO jira_tasks (issue_id, project_id, summary, description, issue_type, assignee_id, status, priority, story_points, created_date, updated_date, resolved_date, parent_issue_id, depends_on, labels, github_pr_id) VALUES
-- Infotainment System Tasks
('IFS-1', 'AUTOSW-2025-IFS', 'Implement CAN message parser for ECU communication', 'Develop a robust CAN message parser to handle ECU communication protocols', 'Task', 'EMP002', 'In Progress', 'High', 8, '2025-01-20 09:00:00', '2025-01-25 14:30:00', NULL, NULL, NULL, '["CAN-bus", "AUTOSAR"]', NULL),
('IFS-2', 'AUTOSW-2025-IFS', 'Voice-activated navigation and controls', 'Implement voice recognition for navigation commands', 'Story', 'EMP003', 'To Do', 'Medium', 13, '2025-01-22 10:00:00', '2025-01-22 10:00:00', NULL, NULL, '["IFS-1"]', '["enhancement", "voice-control"]', NULL),
('IFS-3', 'AUTOSW-2025-IFS', 'CAN bus communication timeout in Gateway Module', 'Intermittent timeouts detected when communicating with gateway', 'Bug', 'EMP002', 'In Progress', 'Critical', 5, '2025-01-23 08:30:00', '2025-01-24 16:00:00', NULL, NULL, NULL, '["bug", "CAN-bus", "safety-critical"]', NULL),

-- ADAS Tasks
('ADAS-1', 'AUTOSW-2025-ADAS', 'Develop complete ADAS Level 2+ automation system', 'Epic for implementing full Level 2+ autonomous driving features', 'Epic', 'EMP004', 'In Progress', 'Critical', 0, '2025-02-01 09:00:00', '2025-02-05 11:00:00', NULL, NULL, NULL, '["AUTOSAR", "ISO26262"]', NULL),
('ADAS-2', 'AUTOSW-2025-ADAS', 'Implement Adaptive Cruise Control with stop-and-go', 'Develop ACC system with full stop-and-go capability', 'Task', 'EMP004', 'In Progress', 'High', 13, '2025-02-02 10:00:00', '2025-02-06 15:30:00', NULL, 'ADAS-1', NULL, '["enhancement", "safety-critical"]', NULL),
('ADAS-3', 'AUTOSW-2025-ADAS', 'Radar sensor showing false positives in rain', 'Radar sensor detecting phantom objects during heavy rain', 'Bug', 'EMP006', 'To Do', 'High', 8, '2025-02-03 14:00:00', '2025-02-03 14:00:00', NULL, NULL, NULL, '["bug", "testing"]', NULL),

-- Vehicle Diagnostics Tasks
('VD-1', 'AUTOSW-2025-VD', 'Setup real-time OBD-II data collection', 'Implement OBD-II data collection with CAN bus integration', 'Task', 'EMP003', 'To Do', 'High', 8, '2025-03-01 09:00:00', '2025-03-01 09:00:00', NULL, NULL, NULL, '["CAN-bus", "testing"]', NULL),
('VD-2', 'AUTOSW-2025-VD', 'Develop predictive maintenance algorithms', 'Create ML models for predictive maintenance based on telemetry', 'Story', 'EMP004', 'To Do', 'Medium', 13, '2025-03-02 10:00:00', '2025-03-02 10:00:00', NULL, NULL, '["VD-1"]', '["enhancement"]', NULL);

-- ============================================================================
-- 4. GITHUB ACTIVITY - Sample PRs (to be populated by sync)
-- ============================================================================

INSERT INTO github_activity (pr_id, project_id, title, author_id, reviewers, created_at, merged_at, closed_at, status, associated_issue_id, changed_files, additions, deletions, comments_count, build_status, test_coverage_delta) VALUES
('infotainment-system-autopmtestproject/PR#1', 'AUTOSW-2025-IFS', 'feat: Add CAN message parser implementation', 'EMP002', '["EMP003", "EMP005"]', '2025-01-24 10:00:00', NULL, NULL, 'Open', 'IFS-1', 5, 234, 12, 3, 'Pending', 2.5),
('adas-driver-assistance-autopmtestproject/PR#1', 'AUTOSW-2025-ADAS', 'feat: Implement ACC stop-and-go logic', 'EMP004', '["EMP006", "EMP005"]', '2025-02-05 14:00:00', NULL, NULL, 'Open', 'ADAS-2', 8, 456, 34, 5, 'Success', 3.2);

-- ============================================================================
-- 5. RESOURCE ALLOCATION - Sample Time Tracking
-- ============================================================================

INSERT INTO resource_allocation (allocation_id, employee_id, project_id, week_start_date, overtime_hours, planned_hours, logged_hours, task_ids) VALUES
('ALLOC-001', 'EMP002', 'AUTOSW-2025-IFS', '2025-01-20', 5.0, 40.0, 42.0, '["IFS-1", "IFS-3"]'),
('ALLOC-002', 'EMP003', 'AUTOSW-2025-IFS', '2025-01-20', 0.0, 40.0, 38.0, '["IFS-2"]'),
('ALLOC-003', 'EMP004', 'AUTOSW-2025-ADAS', '2025-02-03', 3.0, 40.0, 43.0, '["ADAS-1", "ADAS-2"]'),
('ALLOC-004', 'EMP006', 'AUTOSW-2025-ADAS', '2025-02-03', 0.0, 40.0, 35.0, '["ADAS-3"]');

-- ============================================================================
-- 6. TEAM COMMUNICATION LOGS - Sample Messages
-- ============================================================================

INSERT INTO team_communication_logs (message_id, project_id, sender_id, timestamp, message_text, is_blocker_signal) VALUES
('MSG-001', 'AUTOSW-2025-IFS', 'EMP002', '2025-01-24 15:30:00', 'CAN parser blocked - waiting for ECU firmware specs from vendor', TRUE),
('MSG-002', 'AUTOSW-2025-ADAS', 'EMP004', '2025-02-05 09:00:00', 'ACC implementation on track, code review needed', FALSE),
('MSG-003', 'AUTOSW-2025-ADAS', 'EMP006', '2025-02-06 11:00:00', 'Radar calibration delayed due to weather testing equipment unavailable', TRUE),
('MSG-004', 'AUTOSW-2025-IFS', 'EMP003', '2025-01-25 16:00:00', 'Voice control integration complete, ready for testing', FALSE);

-- ============================================================================
-- 7. HISTORICAL PROJECT PERFORMANCE - Past Projects
-- ============================================================================

INSERT INTO historical_project_performance (historical_project_id, project_name, original_end_date, actual_end_date, delay_days, defect_density, integration_issues_count, root_causes, compliance_audit_result) VALUES
('HIST-001', 'Powertrain Control Module 2024', '2024-06-30', '2024-08-15', 46, 2.3, 8, '["late_dependency", "resource_shortage"]', 'Minor NC'),
('HIST-002', 'Battery Management System 2024', '2024-09-30', '2024-09-28', -2, 1.1, 2, '[]', 'Pass'),
('HIST-003', 'Vehicle Gateway Module 2024', '2024-12-15', '2025-01-20', 36, 3.5, 12, '["ambiguous_req", "late_dependency", "integration_complexity"]', 'Major NC');

-- ============================================================================
-- 8. TASK DEPENDENCIES
-- ============================================================================

INSERT INTO task_dependencies (dependency_id, dependent_task_id, blocking_task_id, dependency_type, expected_ready_date, status) VALUES
('DEP-001', 'IFS-2', 'IFS-1', 'Internal', '2025-01-28', 'At Risk'),
('DEP-002', 'VD-2', 'VD-1', 'Internal', '2025-03-10', 'On Track'),
('DEP-003', 'ADAS-2', 'ADAS-1', 'Internal', '2025-02-15', 'On Track');

-- ============================================================================
-- END OF SEED DATA
-- ============================================================================
