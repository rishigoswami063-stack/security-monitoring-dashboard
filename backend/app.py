
import os

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

from database import (
    initialize_database,
    seed_security_events,
    seed_incidents,
    seed_vulnerabilities,
    seed_audit_logs,
    add_audit_log,
    get_connection
)

app = Flask(__name__)
CORS(app)

# Configure these using environment variables.
# Never publish real secrets or passwords in source code.
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

ALGORITHM = "HS256"

ALLOWED_INCIDENT_STATUSES = {
    "Open",
    "Investigating",
    "Resolved"
}


# ---------------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------------

initialize_database()
seed_security_events()
seed_incidents()
seed_vulnerabilities()
seed_audit_logs()


# ---------------------------------------------------------
# JWT TOKEN
# ---------------------------------------------------------

def create_token(user):
    payload = {
        "user_id": user.get("id", 1),
        "username": user.get("username", "admin"),
        "exp": datetime.now(timezone.utc) + timedelta(hours=8)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ---------------------------------------------------------
# JWT AUTHENTICATION
# ---------------------------------------------------------

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not SECRET_KEY:
            return jsonify({
                "success": False,
                "message": "Server authentication is not configured"
            }), 500

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "success": False,
                "message": "Authorization token is required"
            }), 401

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "success": False,
                "message": "Invalid authorization header"
            }), 401

        try:
            payload = jwt.decode(
                parts[1],
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )
            request.current_user = payload

        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Token has expired"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid token"
            }), 401

        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "Security Monitoring Dashboard API is running"
    })


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/api/dashboard", methods=["GET"])
@token_required
def dashboard():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) AS count FROM security_events"
        )
        total_events = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM security_events
            WHERE event_type = 'Failed Login'
        """)
        failed_logins = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM incidents
            WHERE status != 'Resolved'
        """)
        open_incidents = cursor.fetchone()["count"]

        cursor.execute(
            "SELECT COUNT(*) AS count FROM vulnerabilities"
        )
        vulnerabilities = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM vulnerabilities
            WHERE severity = 'Critical'
        """)
        critical_vulnerabilities = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM vulnerabilities
            WHERE severity = 'High'
        """)
        high_vulnerabilities = cursor.fetchone()["count"]

        return jsonify({
            "security_score": 78,
            "total_events": total_events,
            "failed_logins": failed_logins,
            "open_incidents": open_incidents,
            "vulnerabilities": vulnerabilities,
            "critical_vulnerabilities": critical_vulnerabilities,
            "high_vulnerabilities": high_vulnerabilities
        })

    finally:
        conn.close()


# ---------------------------------------------------------
# SECURITY POSTURE
# ---------------------------------------------------------

@app.route("/api/security-posture", methods=["GET"])
@token_required
def security_posture():
    return jsonify({
        "security_score": 78,
        "status": "Good",
        "authentication": 85,
        "network_security": 76,
        "endpoint_security": 80,
        "data_protection": 72,
        "incident_response": 79
    })


# ---------------------------------------------------------
# SECURITY EVENTS
# ---------------------------------------------------------

@app.route("/api/security-events", methods=["GET"])
@token_required
def security_events():
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM security_events
            ORDER BY id DESC
        """)

        return jsonify([
            dict(row) for row in cursor.fetchall()
        ])

    finally:
        conn.close()


# ---------------------------------------------------------
# INCIDENTS - LIST
# ---------------------------------------------------------

@app.route("/api/incidents", methods=["GET"])
@token_required
def incidents():
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM incidents
            ORDER BY id DESC
        """)

        return jsonify([
            dict(row) for row in cursor.fetchall()
        ])

    finally:
        conn.close()


# ---------------------------------------------------------
# INCIDENTS - SINGLE RECORD
# ---------------------------------------------------------

@app.route("/api/incidents/<int:incident_id>", methods=["GET"])
@token_required
def get_incident(incident_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM incidents WHERE id = ?",
            (incident_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return jsonify({
                "success": False,
                "message": "Incident not found"
            }), 404

        return jsonify(dict(row))

    finally:
        conn.close()


# ---------------------------------------------------------
# INCIDENTS - UPDATE STATUS
# ---------------------------------------------------------

@app.route(
    "/api/incidents/<int:incident_id>/status",
    methods=["PATCH"]
)
@token_required
def update_incident_status(incident_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if not isinstance(new_status, str):
        return jsonify({
            "success": False,
            "message": "A valid status is required"
        }), 400

    new_status = new_status.strip().title()

    if new_status not in ALLOWED_INCIDENT_STATUSES:
        return jsonify({
            "success": False,
            "message": (
                "Status must be Open, Investigating, or Resolved"
            )
        }), 400

    username = request.current_user.get(
        "username", "unknown"
    )

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM incidents WHERE id = ?",
            (incident_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return jsonify({
                "success": False,
                "message": "Incident not found"
            }), 404

        incident = dict(row)
        old_status = incident.get("status")

        if old_status == new_status:
            return jsonify({
                "success": True,
                "message": "Incident already has this status",
                "incident": incident
            })

        cursor.execute(
            "UPDATE incidents SET status = ? WHERE id = ?",
            (new_status, incident_id)
        )

        conn.commit()

        add_audit_log(
            source="Incident Management",
            action="Incident Status Updated",
            status="Success",
            details=(
                f"Incident #{incident_id}: "
                f"{old_status} -> {new_status}; "
                f"updated by {username}"
            )
        )

        cursor.execute(
            "SELECT * FROM incidents WHERE id = ?",
            (incident_id,)
        )
        updated_incident = dict(cursor.fetchone())

        return jsonify({
            "success": True,
            "message": "Incident status updated successfully",
            "incident": updated_incident
        })

    except Exception:
        conn.rollback()
        app.logger.exception("Incident status update failed")

        return jsonify({
            "success": False,
            "message": "Could not update incident status"
        }), 500

    finally:
        conn.close()


# ---------------------------------------------------------
# VULNERABILITIES
# ---------------------------------------------------------

@app.route("/api/vulnerabilities", methods=["GET"])
@token_required
def vulnerabilities():
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM vulnerabilities
            ORDER BY id DESC
        """)

        return jsonify([
            dict(row) for row in cursor.fetchall()
        ])

    finally:
        conn.close()


# ---------------------------------------------------------
# AUDIT LOGS
# ---------------------------------------------------------

@app.route("/api/audit-logs", methods=["GET"])
@token_required
def audit_logs():
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM audit_logs
            ORDER BY id DESC
        """)

        return jsonify([
            dict(row) for row in cursor.fetchall()
        ])

    finally:
        conn.close()


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    if not SECRET_KEY or not ADMIN_USERNAME or not ADMIN_PASSWORD:
        app.logger.error(
            "Authentication environment variables are missing"
        )
        return jsonify({
            "success": False,
            "message": "Server authentication is not configured"
        }), 500

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "Username and password are required"
        }), 400

    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401

    user = {
        "id": 1,
        "username": username,
        "role": "admin"
    }

    token = create_token(user)

    try:
        add_audit_log(
            source="Authentication",
            action="User Login",
            status="Success",
            details=f"User {username} logged in"
        )
    except Exception:
        app.logger.exception("Login audit log failed")

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": user
    })


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------

if __name__ == "__main__":
    # Do not enable Flask debug mode for public deployment.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )