
import { useEffect, useState } from "react";
import Login from "./Login";
import "./App.css";

const API = "https://security-monitoring-dashboard.onrender.com";

async function authFetch(url, options = {}) {
  const token = localStorage.getItem("token");
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return fetch(url, { ...options, headers });
}

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });

  const [activePage, setActivePage] = useState("Dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [posture, setPosture] = useState(null);
  const [events, setEvents] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState("Checking...");

  const handleLogin = (loggedInUser) => {
    setUser(loggedInUser);
    localStorage.setItem("user", JSON.stringify(loggedInUser));
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");

    setUser(null);
    setDashboard(null);
    setPosture(null);
    setEvents([]);
    setIncidents([]);
    setVulnerabilities([]);
    setAuditLogs([]);
    setBackendStatus("Checking...");
  };

  const refreshIncidents = async () => {
    const response = await authFetch(`${API}/api/incidents`);

    if (!response.ok) {
      throw new Error("Could not refresh incidents");
    }

    const data = await response.json();
    setIncidents(data);
  };

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    const loadData = async () => {
      try {
        setLoading(true);

        const [
          dashboardResponse,
          postureResponse,
          eventsResponse,
          incidentsResponse,
          vulnerabilitiesResponse,
          auditLogsResponse,
        ] = await Promise.all([
          authFetch(`${API}/api/dashboard`),
          authFetch(`${API}/api/security-posture`),
          authFetch(`${API}/api/security-events`),
          authFetch(`${API}/api/incidents`),
          authFetch(`${API}/api/vulnerabilities`),
          authFetch(`${API}/api/audit-logs`),
        ]);

        const responses = [
          dashboardResponse,
          postureResponse,
          eventsResponse,
          incidentsResponse,
          vulnerabilitiesResponse,
          auditLogsResponse,
        ];

        if (responses.some(
          (response) =>
            response.status === 401 || response.status === 403
        )) {
          localStorage.removeItem("user");
          localStorage.removeItem("token");

          if (!cancelled) {
            setUser(null);
            setBackendStatus("Disconnected");
          }
          return;
        }

        if (responses.some((response) => !response.ok)) {
          throw new Error("Backend request failed");
        }

        const [
          dashboardData,
          postureData,
          eventsData,
          incidentsData,
          vulnerabilitiesData,
          auditLogsData,
        ] = await Promise.all(
          responses.map((response) => response.json())
        );

        if (cancelled) return;

        setDashboard(dashboardData);
        setPosture(postureData);
        setEvents(eventsData);
        setIncidents(incidentsData);
        setVulnerabilities(vulnerabilitiesData);
        setAuditLogs(auditLogsData);
        setBackendStatus("Connected");
      } catch (error) {
        if (!cancelled) {
          console.error("Backend error:", error);
          setBackendStatus("Disconnected");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 10000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [user]);

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>
          <div>
            <div className="brand-name">Sentinel</div>
            <div className="brand-subtitle">Security Monitor</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {[
            "Dashboard",
            "Security Events",
            "Incidents",
            "Vulnerabilities",
            "Audit Logs",
          ].map((page) => (
            <button
              key={page}
              className={
                activePage === page ? "nav-btn active" : "nav-btn"
              }
              onClick={() => setActivePage(page)}
            >
              {page}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        <header className="top-header">
          <div>
            <div className="section-label">SECURITY OPERATIONS</div>
            <h1>{activePage}</h1>
          </div>

          <div className="user-area">
            <div className="avatar">
              {user.username?.charAt(0).toUpperCase()}
            </div>

            <div className="user-info">
              <strong>{user.username}</strong>
              <span>
                {user.role === "admin"
                  ? "Security Administrator"
                  : "Security User"}
              </span>
            </div>

            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </header>

        <div className="status-row">
          <span>Backend status:</span>
          <strong
            className={
              backendStatus === "Connected"
                ? "status-connected"
                : "status-disconnected"
            }
          >
            {backendStatus}
          </strong>
        </div>

        {activePage === "Dashboard" && (
          <DashboardPage
            dashboard={dashboard}
            posture={posture}
            events={events}
            loading={loading}
          />
        )}

        {activePage === "Security Events" && (
          <SecurityEventsPage events={events} />
        )}

        {activePage === "Incidents" && (
          <IncidentsPage
            incidents={incidents}
            refreshIncidents={refreshIncidents}
          />
        )}

        {activePage === "Vulnerabilities" && (
          <VulnerabilitiesPage vulnerabilities={vulnerabilities} />
        )}

        {activePage === "Audit Logs" && (
          <AuditLogsPage logs={auditLogs} />
        )}
      </main>
    </div>
  );
}

function DashboardPage({ dashboard, posture, events, loading }) {
  if (loading || !dashboard || !posture) {
    return <div className="loading">Loading security dashboard...</div>;
  }

  return (
    <section className="page-content">
      <div className="page-heading">
        <h2>Security overview</h2>
        <p>Monitor security events, incidents and system activity.</p>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Security score"
          value={`${dashboard.security_score}%`}
          subtitle="Calculated from current findings"
        />
        <StatCard
          title="Failed logins"
          value={dashboard.failed_logins}
          subtitle="Detected security events"
        />
        <StatCard
          title="Open incidents"
          value={dashboard.open_incidents}
          subtitle="Requires attention"
        />
        <StatCard
          title="Vulnerabilities"
          value={dashboard.vulnerabilities}
          subtitle="Current findings"
        />
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Security posture</h3>
              <p>Current security findings</p>
            </div>
          </div>

          <div className="posture-list">
            <PostureRow label="Security score" value={`${posture.security_score}%`} />
            <PostureRow label="Critical vulnerabilities" value={dashboard.critical_vulnerabilities} />
            <PostureRow label="High vulnerabilities" value={dashboard.high_vulnerabilities} />
            <PostureRow label="Open incidents" value={dashboard.open_incidents} />
            <PostureRow label="Failed login events" value={dashboard.failed_logins} />
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Recent security events</h3>
              <p>Latest activity detected by the system</p>
            </div>
            <span className="view-label">{events.length} events</span>
          </div>

          <div className="events-list">
            {events.slice(0, 5).map((event) => (
              <EventRow key={event.id} event={event} />
            ))}

            {events.length === 0 && (
              <div className="empty">No security events found.</div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function SecurityEventsPage({ events }) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <h2>Security Events</h2>
        <p>All security events detected by the system.</p>
      </div>

      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>Event</th>
              <th>Description</th>
              <th>Severity</th>
              <th>Source</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id}>
                <td><strong>{event.event_type}</strong></td>
                <td>{event.description}</td>
                <td><SeverityBadge severity={event.severity} /></td>
                <td>{event.source}</td>
                <td>{event.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {events.length === 0 && (
          <div className="empty">No events found.</div>
        )}
      </div>
    </section>
  );
}

/* INCIDENTS PAGE WITH STATUS UPDATE */

function IncidentsPage({ incidents, refreshIncidents }) {
  const [selectedStatuses, setSelectedStatuses] = useState({});
  const [updatingId, setUpdatingId] = useState(null);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("success");

  const handleStatusChange = (incidentId, status) => {
    setSelectedStatuses((previous) => ({
      ...previous,
      [incidentId]: status,
    }));
  };

  const updateIncident = async (incident) => {
    const status =
      selectedStatuses[incident.id] ?? incident.status;

    if (status === incident.status) {
      setMessage("This incident already has that status.");
      setMessageType("success");
      return;
    }

    try {
      setUpdatingId(incident.id);
      setMessage("");

      const response = await authFetch(
        `${API}/api/incidents/${incident.id}/status`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.message || "Could not update incident.");
      }

      setMessage(data.message || "Incident status updated successfully.");
      setMessageType("success");

      await refreshIncidents();

      setSelectedStatuses((previous) => ({
        ...previous,
        [incident.id]: status,
      }));
    } catch (error) {
      console.error("Incident update error:", error);
      setMessage(error.message || "Could not update incident.");
      setMessageType("error");
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <section className="page-content">
      <div className="page-heading">
        <h2>Incidents</h2>
        <p>Review security incidents and update their investigation status.</p>
      </div>

      {message && (
        <div
          className={`incident-message ${messageType}`}
          role="status"
        >
          {message}
        </div>
      )}

      <div className="cards-list">
        {incidents.map((incident) => {
          const selectedStatus =
            selectedStatuses[incident.id] ?? incident.status;

          return (
            <div className="incident-card" key={incident.id}>
              <div className="card-top">
                <div>
                  <h3>{incident.title}</h3>
                  <span>Incident #{incident.id}</span>
                </div>
                <SeverityBadge severity={incident.severity} />
              </div>

              <p>{incident.description}</p>

              <div className="incident-footer">
                <span>
                  Status: <strong>{incident.status}</strong>
                </span>
                <span>{incident.created_at}</span>
              </div>

              <div className="incident-actions">
                <label htmlFor={`status-${incident.id}`}>
                  Update status
                </label>

                <select
                  id={`status-${incident.id}`}
                  value={selectedStatus}
                  onChange={(event) =>
                    handleStatusChange(incident.id, event.target.value)
                  }
                  disabled={updatingId === incident.id}
                >
                  <option value="Open">Open</option>
                  <option value="Investigating">Investigating</option>
                  <option value="Resolved">Resolved</option>
                </select>

                <button
                  type="button"
                  className="incident-update-btn"
                  onClick={() => updateIncident(incident)}
                  disabled={
                    updatingId === incident.id ||
                    selectedStatus === incident.status
                  }
                >
                  {updatingId === incident.id
                    ? "Updating..."
                    : "Save status"}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {incidents.length === 0 && (
        <div className="empty">No incidents found.</div>
      )}
    </section>
  );
}

function VulnerabilitiesPage({ vulnerabilities }) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <h2>Vulnerabilities</h2>
        <p>Identified security weaknesses in the system.</p>
      </div>

      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Description</th>
              <th>Severity</th>
              <th>Component</th>
              <th>Status</th>
              <th>Detected</th>
            </tr>
          </thead>
          <tbody>
            {vulnerabilities.map((item) => (
              <tr key={item.id}>
                <td><strong>{item.title}</strong></td>
                <td>{item.description}</td>
                <td><SeverityBadge severity={item.severity} /></td>
                <td>{item.component}</td>
                <td>{item.status}</td>
                <td>{item.detected_at}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {vulnerabilities.length === 0 && (
          <div className="empty">No vulnerabilities found.</div>
        )}
      </div>
    </section>
  );
}

function AuditLogsPage({ logs }) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <h2>Audit Logs</h2>
        <p>Recorded administrative and security activity.</p>
      </div>

      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>Action</th>
              <th>Result</th>
              <th>User ID</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td><strong>{log.action}</strong></td>
                <td>
                  <span
                    className={
                      log.result?.startsWith("Success")
                        ? "result-success"
                        : "result-failed"
                    }
                  >
                    {log.result}
                  </span>
                </td>
                <td>{log.user_id ?? "System"}</td>
                <td>{log.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {logs.length === 0 && (
          <div className="empty">No audit logs found.</div>
        )}
      </div>
    </section>
  );
}

function StatCard({ title, value, subtitle }) {
  return (
    <div className="stat-card">
      <div className="stat-title">{title}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-subtitle">{subtitle}</div>
    </div>
  );
}

function PostureRow({ label, value }) {
  return (
    <div className="posture-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function EventRow({ event }) {
  return (
    <div className="event-row">
      <div className="event-dot"></div>
      <div className="event-content">
        <div className="event-title">{event.event_type}</div>
        <div className="event-description">{event.description}</div>
        <div className="event-meta">{event.source}</div>
      </div>
      <SeverityBadge severity={event.severity} />
    </div>
  );
}

function SeverityBadge({ severity }) {
  return (
    <span
      className={`severity severity-${String(
        severity || ""
      ).toLowerCase()}`}
    >
      {severity || "Unknown"}
    </span>
  );
}

export default App;
