import React, { useEffect, useState, useRef } from "react";
import api from "../services/api";

const AdminMonitor = () => {
  const [sessionId, setSessionId] = useState(null);
  const [frameData, setFrameData] = useState(null);
  const [activeTracks, setActiveTracks] = useState([]);
  const canvasRef = useRef(null);

  // 1. Poll for active session ID to pick up new sessions automatically
  useEffect(() => {
    let active = true;
    const fetchSession = async () => {
      try {
        const res = await api.get("/session/active");
        if (active) {
          const newSessionId = res.data.session_id;
          setSessionId(newSessionId);
          if (!newSessionId) {
            // Clear current stream data when no session is active
            setFrameData(null);
            setActiveTracks([]);
          }
        }
      } catch (err) {
        console.log("Error checking active session", err);
        if (active) {
          setSessionId(null);
          setFrameData(null);
          setActiveTracks([]);
        }
      }
      if (active) {
        setTimeout(fetchSession, 3000); // Check every 3 seconds
      }
    };

    fetchSession();

    return () => {
      active = false;
    };
  }, []);

  // 2. Poll live frame + tracks when a session is active
  useEffect(() => {
    if (!sessionId) return;

    let active = true;
    const poll = async () => {
      try {
        const res = await api.get(`/session/live/${sessionId}`);
        if (active) {
          setFrameData(res.data.frame);
          setActiveTracks(res.data.active_tracks || []);
        }
      } catch (err) {
        console.log("Live fetch error", err);
      }
      if (active && sessionId) {
        setTimeout(poll, 100); // Poll at 10 FPS
      }
    };

    poll();

    return () => {
      active = false;
    };
  }, [sessionId]);

  // 3. Draw frame and recognized/unknown overlays onto the canvas
  useEffect(() => {
    if (!frameData) return;

    let active = true;
    const img = new Image();
    img.src = `data:image/jpeg;base64,${frameData}`;
    img.onload = () => {
      if (!active) return;
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      const scaleX = canvas.width / img.naturalWidth;
      const scaleY = canvas.height / img.naturalHeight;

      activeTracks.forEach((track) => {
        if (!track.bbox) return;
        const [x1, y1, x2, y2] = track.bbox;
        const rx1 = x1 * scaleX;
        const ry1 = y1 * scaleY;
        const rx2 = x2 * scaleX;
        const ry2 = y2 * scaleY;

        const color = track.recognized ? "#4CAF50" : "#F44336";
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(rx1, ry1, rx2 - rx1, ry2 - ry1);

        ctx.fillStyle = color;
        ctx.font = "bold 14px Arial";
        const label = track.recognized ? `Recognized: ${track.name}` : "Unknown";
        const textWidth = ctx.measureText(label).width;
        ctx.fillRect(rx1 - 1.5, ry1 - 22, textWidth + 10, 22);

        ctx.fillStyle = "#FFFFFF";
        ctx.fillText(label, rx1 + 3, ry1 - 6);
      });
    };

    return () => {
      active = false;
    };
  }, [frameData, activeTracks]);

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Admin Live Monitoring</h2>

      {!sessionId && (
        <div style={styles.warning}>No active camera session</div>
      )}

      <div style={styles.main}>
        {/* VIDEO AREA */}
        <div style={styles.videoBox}>
          {frameData ? (
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              style={styles.video}
            />
          ) : (
            <div style={styles.placeholder}>Waiting for stream...</div>
          )}
        </div>

        {/* SIDEBAR */}
        <div style={styles.sidebar}>
          <h3>Active Tracks</h3>

          {activeTracks.length === 0 ? (
            <p>No faces detected</p>
          ) : (
            activeTracks.map((track) => (
              <div key={track.track_id} style={styles.card}>
                <p>
                  <b>{track.name}</b>
                </p>
                <p>Track ID: {track.track_id}</p>
                <p>Status: {track.recognized ? "Known" : "Unknown"}</p>
                {track.bbox && (
                  <p style={styles.bboxText}>
                    BBox: [{track.bbox.map(Math.round).join(", ")}]
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminMonitor;

const styles = {
  container: {
    padding: "20px",
    fontFamily: "Arial",
    backgroundColor: "#0f0f0f",
    color: "white",
    height: "100vh",
  },
  title: {
    marginBottom: "20px",
  },
  main: {
    display: "flex",
    gap: "20px",
  },
  videoBox: {
    flex: 2,
    backgroundColor: "#1a1a1a",
    borderRadius: "10px",
    overflow: "hidden",
    height: "500px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  video: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },
  placeholder: {
    color: "#888",
  },
  sidebar: {
    flex: 1,
    backgroundColor: "#1a1a1a",
    borderRadius: "10px",
    padding: "10px",
    overflowY: "auto",
  },
  card: {
    backgroundColor: "#2a2a2a",
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "8px",
  },
  warning: {
    color: "red",
  },
  bboxText: {
    fontSize: "12px",
    color: "#aaa",
    fontFamily: "monospace",
    marginTop: "5px",
  },
};