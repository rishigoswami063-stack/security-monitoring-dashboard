from database import get_connection

connection = get_connection()

connection.execute(
    """
    INSERT OR IGNORE INTO users
    (username, password, role)
    VALUES (?, ?, ?)
    """,
    ("admin", "admin123", "admin")
)

connection.commit()
connection.close()

print("Admin user created")