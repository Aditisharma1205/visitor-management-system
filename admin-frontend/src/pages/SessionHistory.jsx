import { useEffect, useState } from "react";
import api from "../services/api";

function formatDateTime(dt) {
    if (!dt) return "—";
    return new Date(dt).toLocaleString();
}

function formatDuration(start, end) {
    if (!start || !end) return "—";
    const ms = new Date(end) - new Date(start);
    if (ms < 0) return "—";
    const totalSeconds = Math.floor(ms / 1000);
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}

function StatusBadge({ status }) {
    const isActive = status === "ACTIVE";
    return (
        <span style={{
            display: "inline-block",
            padding: "3px 12px",
            borderRadius: "999px",
            fontSize: "12px",
            fontWeight: 700,
            letterSpacing: "0.5px",
            backgroundColor: isActive ? "#dcfce7" : "#f1f5f9",
            color: isActive ? "#15803d" : "#475569",
            border: `1px solid ${isActive ? "#86efac" : "#cbd5e1"}`,
        }}>
            {isActive ? "● ACTIVE" : "ENDED"}
        </span>
    );
}

function VisitorTypeBadge({ type }) {
    const isKnown = type === "known";
    return (
        <span style={{
            display: "inline-block",
            padding: "2px 10px",
            borderRadius: "999px",
            fontSize: "12px",
            fontWeight: 600,
            backgroundColor: isKnown ? "#dbeafe" : "#fee2e2",
            color: isKnown ? "#1d4ed8" : "#b91c1c",
        }}>
            {isKnown ? "Known" : "Unknown"}
        </span>
    );
}

function VisitorLogBadge({ status }) {
    const isInside = status === "INSIDE";
    return (
        <span style={{
            display: "inline-block",
            padding: "2px 10px",
            borderRadius: "999px",
            fontSize: "12px",
            fontWeight: 600,
            backgroundColor: isInside ? "#fef9c3" : "#f0fdf4",
            color: isInside ? "#a16207" : "#166534",
        }}>
            {isInside ? "Inside" : "Exited"}
        </span>
    );
}

function ExpandedVisitors({ sessionId }) {
    const [visitors, setVisitors] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        api.get(`/session/${sessionId}/visitors`)
            .then(res => setVisitors(res.data))
            .catch(() => setError("Failed to load visitors."))
            .finally(() => setLoading(false));
    }, [sessionId]);

    if (loading) return <p style={styles.expandedInfo}>Loading visitors...</p>;
    if (error) return <p style={{ color: "red", padding: "12px" }}>{error}</p>;
    if (visitors.length === 0) return <p style={styles.expandedInfo}>No visitor logs for this session.</p>;

    return (
        <table style={{ ...styles.table, marginTop: 0, fontSize: "13px" }}>
            <thead>
                <tr style={{ backgroundColor: "#334155", color: "#e2e8f0" }}>
                    <th style={styles.th}>Name</th>
                    <th style={styles.th}>Type</th>
                    <th style={styles.th}>Entry Time</th>
                    <th style={styles.th}>Exit Time</th>
                    <th style={styles.th}>Log Status</th>
                    <th style={styles.th}>Entry Snapshot</th>
                </tr>
            </thead>
            <tbody>
                {visitors.map((v, i) => (
                    <tr key={v.id} style={{ backgroundColor: i % 2 === 0 ? "#f8fafc" : "#fff" }}>
                        <td style={styles.td}>{v.name}</td>
                        <td style={styles.td}><VisitorTypeBadge type={v.type} /></td>
                        <td style={styles.td}>{formatDateTime(v.entry_time)}</td>
                        <td style={styles.td}>{formatDateTime(v.exit_time)}</td>
                        <td style={styles.td}><VisitorLogBadge status={v.status} /></td>
                        <td style={styles.td}>
                            {v.entry_snapshot ? (
                                <a
                                    href={`http://localhost:8000/${v.entry_snapshot}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    style={{ color: "#4f46e5", textDecoration: "underline" }}
                                >
                                    View
                                </a>
                            ) : "—"}
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

function SessionHistory() {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedId, setExpandedId] = useState(null);

    useEffect(() => {
        api.get("/session/history")
            .then(res => setSessions(res.data))
            .catch(() => setError("Failed to load session history."))
            .finally(() => setLoading(false));
    }, []);

    const toggleExpand = (id) => {
        setExpandedId(prev => prev === id ? null : id);
    };

    if (loading) {
        return <div style={styles.center}><p>Loading session history...</p></div>;
    }
    if (error) {
        return <div style={styles.center}><p style={{ color: "red" }}>{error}</p></div>;
    }

    return (
        <div style={styles.container}>
            <h1 style={styles.heading}>Session History</h1>
            <p style={styles.subheading}>
                Click any session row to expand and see its visitors.
            </p>

            {sessions.length === 0 ? (
                <p style={styles.empty}>No sessions recorded yet.</p>
            ) : (
                <div style={styles.tableWrapper}>
                    <table style={styles.table}>
                        <thead>
                            <tr style={styles.headerRow}>
                                <th style={styles.th}></th>
                                <th style={styles.th}>Session ID</th>
                                <th style={styles.th}>Start Time</th>
                                <th style={styles.th}>End Time</th>
                                <th style={styles.th}>Duration</th>
                                <th style={styles.th}>Total</th>
                                <th style={styles.th}>Known</th>
                                <th style={styles.th}>Unknown</th>
                                <th style={styles.th}>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sessions.map((s, idx) => {
                                const isExpanded = expandedId === s.id;
                                return (
                                    <>
                                        <tr
                                            key={`session-${s.id}`}
                                            onClick={() => toggleExpand(s.id)}
                                            style={{
                                                ...styles.row,
                                                backgroundColor: isExpanded
                                                    ? "#eef2ff"
                                                    : idx % 2 === 0 ? "#fff" : "#f8fafc",
                                                cursor: "pointer",
                                            }}
                                        >
                                            <td style={{ ...styles.td, width: "32px", textAlign: "center", color: "#6366f1", fontWeight: 700 }}>
                                                {isExpanded ? "▼" : "▶"}
                                            </td>
                                            <td style={styles.td}>#{s.id}</td>
                                            <td style={styles.td}>{formatDateTime(s.start_time)}</td>
                                            <td style={styles.td}>{formatDateTime(s.end_time)}</td>
                                            <td style={styles.td}>{formatDuration(s.start_time, s.end_time)}</td>
                                            <td style={{ ...styles.td, fontWeight: 600 }}>{s.total_visitors}</td>
                                            <td style={{ ...styles.td, color: "#16a34a", fontWeight: 600 }}>{s.known_visitors}</td>
                                            <td style={{ ...styles.td, color: "#dc2626", fontWeight: 600 }}>{s.unknown_visitors}</td>
                                            <td style={styles.td}><StatusBadge status={s.status} /></td>
                                        </tr>

                                        {isExpanded && (
                                            <tr key={`expanded-${s.id}`}>
                                                <td
                                                    colSpan={9}
                                                    style={{
                                                        padding: "0",
                                                        backgroundColor: "#f0f4ff",
                                                        borderBottom: "2px solid #c7d2fe",
                                                    }}
                                                >
                                                    <div style={{ padding: "16px 24px" }}>
                                                        <p style={styles.expandedLabel}>
                                                            Visitors in Session #{s.id}
                                                        </p>
                                                        <ExpandedVisitors sessionId={s.id} />
                                                    </div>
                                                </td>
                                            </tr>
                                        )}
                                    </>
                                );
            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

export default SessionHistory;

const styles = {
    container: {
        maxWidth: "1200px",
        margin: "40px auto",
        padding: "0 20px",
    },
    heading: {
        fontSize: "28px",
        fontWeight: 700,
        color: "#0f172a",
        marginBottom: "4px",
    },
    subheading: {
        fontSize: "14px",
        color: "#64748b",
        marginBottom: "28px",
    },
    center: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "200px",
        fontSize: "16px",
        color: "#64748b",
    },
    empty: {
        color: "#94a3b8",
        fontSize: "15px",
    },
    tableWrapper: {
        overflowX: "auto",
        borderRadius: "12px",
        border: "1px solid #e2e8f0",
        boxShadow: "0 1px 6px rgba(0,0,0,0.07)",
    },
    table: {
        width: "100%",
        borderCollapse: "collapse",
        fontSize: "14px",
    },
    headerRow: {
        backgroundColor: "#1e293b",
        color: "#fff",
    },
    th: {
        padding: "12px 16px",
        textAlign: "left",
        fontWeight: 600,
        whiteSpace: "nowrap",
    },
    row: {
        borderBottom: "1px solid #e2e8f0",
        transition: "background-color 0.15s",
    },
    td: {
        padding: "12px 16px",
        color: "#334155",
        whiteSpace: "nowrap",
    },
    expandedLabel: {
        fontWeight: 700,
        fontSize: "14px",
        color: "#3730a3",
        marginBottom: "10px",
    },
    expandedInfo: {
        color: "#64748b",
        padding: "10px 0",
        fontSize: "13px",
    },
};
