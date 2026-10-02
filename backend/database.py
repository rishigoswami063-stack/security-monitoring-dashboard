import sqlite3


DATABASE = "security_monitoring.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            component TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def add_audit_log(action, result="Success", user_id=None):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO audit_logs
        (user_id, action, result)
        VALUES (?, ?, ?)
        """,
        (user_id, action, result),
    )

    connection.commit()
    connection.close()


def seed_security_events():
    connection = get_connection()
    cursor = connection.cursor()

    existing_events = cursor.execute(
        "SELECT COUNT(*) FROM security_events"
    ).fetchone()[0]

    if existing_events > 0:
        connection.close()
        return

    events = [
        (
            "Failed Login",
            "Multiple failed login attempts detected",
            "High",
            "Authentication Service",
        ),
        (
            "Unauthorized API Request",
            "API request received without valid authorization",
            "Critical",
            "API Gateway",
        ),
        (
            "Password Policy Violation",
            "User attempted to set a password that violates security policy",
            "Medium",
            "Identity Service",
        ),
        (
            "Suspicious Login",
            "Login detected from an unusual location",
            "High",
            "Authentication Service",
        ),
        (
            "Configuration Change",
            "Security configuration was modified",
            "Medium",
            "Cloud Console",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO security_events
        (event_type, description, severity, source)
        VALUES (?, ?, ?, ?)
        """,
        events,
    )

    connection.commit()
    connection.close()


def seed_incidents():
    connection = get_connection()
    cursor = connection.cursor()

    existing_incidents = cursor.execute(
        "SELECT COUNT(*) FROM incidents"
    ).fetchone()[0]

    if existing_incidents > 0:
        connection.close()
        return

    incidents = [
        (
            "Repeated failed login attempts",
            "Multiple unsuccessful authentication attempts were detected for an administrative account.",
            "High",
            "Open",
        ),
        (
            "Unauthorized API request",
            "An API request was detected without valid authorization.",
            "Critical",
            "Open",
        ),
        (
            "Suspicious login location",
            "A login was detected from an unusual geographic location.",
            "High",
            "Investigating",
        ),
        (
            "Security configuration change",
            "A security-related configuration was modified.",
            "Medium",
            "Resolved",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO incidents
        (title, description, severity, status)
        VALUES (?, ?, ?, ?)
        """,
        incidents,
    )

    connection.commit()
    connection.close()


def seed_vulnerabilities():
    connection = get_connection()
    cursor = connection.cursor()

    existing_vulnerabilities = cursor.execute(
        "SELECT COUNT(*) FROM vulnerabilities"
    ).fetchone()[0]

    if existing_vulnerabilities > 0:
        connection.close()
        return

    vulnerabilities = [
        (
            "Outdated authentication library",
            "An outdated authentication dependency contains known security weaknesses.",
            "Critical",
            "Authentication Service",
            "Open",
        ),
        (
            "Missing access control validation",
            "An API endpoint does not consistently validate user authorization.",
            "High",
            "API Gateway",
            "Open",
        ),
        (
            "Weak password configuration",
            "Current password configuration does not meet the recommended security policy.",
            "Medium",
            "Identity Service",
            "In Progress",
        ),
        (
            "Verbose error messages",
            "Application errors expose more implementation information than required.",
            "Low",
            "Web Application",
            "Resolved",
        ),
        (
            "Unencrypted internal communication",
            "A service communication path requires stronger transport protection.",
            "High",
            "Internal Network",
            "Open",
        ),
        (
            "Unused service account",
            "An inactive service account is still enabled and should be reviewed.",
            "Medium",
            "Cloud IAM",
            "Open",
        ),
        (
            "Missing security headers",
            "Recommended HTTP security headers are not configured on one application endpoint.",
            "Low",
            "Web Application",
            "Resolved",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO vulnerabilities
        (title, description, severity, component, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        vulnerabilities,
    )

    connection.commit()
    connection.close()


def seed_audit_logs():
    connection = get_connection()
    cursor = connection.cursor()

    existing_logs = cursor.execute(
        "SELECT COUNT(*) FROM audit_logs"
    ).fetchone()[0]

    if existing_logs > 0:
        connection.close()
        return

    logs = [
        (
            None,
            "Admin login",
            "Success",
        ),
        (
            None,
            "Viewed security events",
            "Success",
        ),
        (
            None,
            "Viewed incident #2",
            "Success",
        ),
        (
            None,
            "Reviewed vulnerability #1",
            "Success",
        ),
        (
            None,
            "Security posture checked",
            "Success",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO audit_logs
        (user_id, action, result)
        VALUES (?, ?, ?)
        """,
        logs,
    )

    connection.commit()
    connection.close()