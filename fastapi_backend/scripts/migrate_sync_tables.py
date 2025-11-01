"""
Database migration to add comment and sync log tables
Run this to update the schema with new tables for enhanced sync
"""

from sqlalchemy import text
from database import engine


def migrate_add_sync_tables():
    """Add new tables for comments and sync logs"""
    
    with engine.connect() as conn:
        # Create GitHubComment table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS github_comments (
                comment_id VARCHAR(100) PRIMARY KEY,
                pr_id VARCHAR(100),
                issue_id VARCHAR(100),
                author_id VARCHAR(100),
                body TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                reactions JSON,
                last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pr_id) REFERENCES github_activity(pr_id) ON DELETE CASCADE,
                FOREIGN KEY (issue_id) REFERENCES github_issues(issue_id) ON DELETE CASCADE,
                FOREIGN KEY (author_id) REFERENCES employee_profile(employee_id) ON DELETE SET NULL
            )
        """))
        
        # Create JiraComment table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS jira_comments (
                comment_id VARCHAR(100) PRIMARY KEY,
                issue_id VARCHAR(100) NOT NULL,
                author_id VARCHAR(100),
                body TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (issue_id) REFERENCES jira_tasks(issue_id) ON DELETE CASCADE,
                FOREIGN KEY (author_id) REFERENCES employee_profile(employee_id) ON DELETE SET NULL
            )
        """))
        
        # Create SyncLog table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                log_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                sync_type VARCHAR(50),
                project_id VARCHAR(100),
                status VARCHAR(50),
                items_synced INTEGER DEFAULT 0,
                error_message TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds FLOAT,
                FOREIGN KEY (project_id) REFERENCES project_metadata(project_id) ON DELETE SET NULL
            )
        """))
        
        # Create VectorEmbedding table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vector_embeddings (
                embedding_id VARCHAR(100) PRIMARY KEY,
                content_type VARCHAR(50),
                content_id VARCHAR(100),
                project_id VARCHAR(100),
                title VARCHAR(500),
                content_text TEXT,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project_metadata(project_id) ON DELETE CASCADE
            )
        """))
        
        # Create ChatHistory table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_history (
                chat_id VARCHAR(100) PRIMARY KEY,
                user_id VARCHAR(100),
                message TEXT,
                response TEXT,
                context_items JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES employee_profile(employee_id) ON DELETE CASCADE
            )
        """))
        
        # Add new columns to sync_status_data tracking (if needed)
        try:
            conn.execute(text("""
                ALTER TABLE sync_control 
                ADD COLUMN IF NOT EXISTS last_enhanced_sync TIMESTAMP
            """))
        except Exception:
            pass  # Column might already exist or not supported
        
        conn.commit()
        
    print("✓ Database migration completed successfully")
    print("  - Added github_comments table")
    print("  - Added jira_comments table")
    print("  - Added sync_logs table")
    print("  - Added vector_embeddings table")
    print("  - Added chat_history table")


if __name__ == "__main__":
    print("Starting database migration...")
    migrate_add_sync_tables()
