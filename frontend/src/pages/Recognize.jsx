import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";

const FACE_WIDTH = 640;
const FACE_HEIGHT = 480;
const STALE_MS = 2000;

function Recognize() {
    const webcamRef = useRef(null);
    const canvasRef = useRef(null);
    const frameInterval = useRef(null);
    const socket = useRef(null);
    const frameInFlight = useRef(false);

    const [isRunning, setIsRunning] = useState(false);
    const [faces, setFaces] = useState([]);
    const [notification, setNotification] = useState(null);

    // Auto-clear notification after 3 seconds
    useEffect(() => {
        if (!notification) return;
        const timer = setTimeout(() => {
            setNotification(null);
        }, 3000);
        return () => clearTimeout(timer);
    }, [notification]);

    // Handle WebSocket connection and frame sending interval based on isRunning state
    useEffect(() => {
        if (isRunning) {
            console.log("CREATING WS CONNECTION");
            socket.current = new WebSocket("ws://127.0.0.1:8000/ws");

            socket.current.onopen = () => {
                console.log("WS CONNECTED");
            };

            socket.current.onclose = () => {
                console.log("WS CLOSED");
                frameInFlight.current = false;
            };

            socket.current.onerror = (error) => {
                console.error("WS ERROR", error);
                frameInFlight.current = false;
            };

            socket.current.onmessage = (event) => {
                const data = JSON.parse(event.data);

                // Handle spoofing notifications and state
                if (data.type === "spoof") {
                    setNotification({
                        type: "error",
                        text: "🚫 Spoof Attack Detected",
                        subtext: `Spoof Score: ${(data.spoof_score * 100).toFixed(1)}%`
                    });

                    const spoofId = `spoof_${data.bbox.map(Math.round).join("_")}`;
                    setFaces((prev) => {
                        const filtered = prev.filter((f) => f.track_id !== spoofId);
                        return [
                            ...filtered,
                            {
                                track_id: spoofId,
                                name: "SPOOF DETECTED",
                                recognized: false,
                                spoof: true,
                                bbox: data.bbox,
                                lastSeen: Date.now()
                            }
                        ];
                    });
                    return;
                }

                // Handle frame summary to clear inactive track IDs
                if (data.type === "frame_summary") {
                    frameInFlight.current = false;
                    setFaces((prev) =>
                        prev.filter((face) =>
                            face.spoof || data.active_track_ids.includes(face.track_id)
                        )
                    );
                    return;
                }

                // Trigger notifications for live recognized faces or unknown visitors
                if (data.recognized && data.name) {
                    setFaces((prev) => {
                        const alreadyNotified = prev.some(
                            (f) => f.track_id === data.track_id && f.recognized
                        );
                        if (!alreadyNotified) {
                            setNotification({
                                type: "success",
                                text: `✅ Welcomed: ${data.name}`
                            });
                        }
                        return prev;
                    });
                } else if (data.type === "unknown_alert") {
                    setFaces((prev) => {
                        const alreadyNotified = prev.some(
                            (f) => f.track_id === data.track_id && f.type === "unknown_alert"
                        );
                        if (!alreadyNotified) {
                            setNotification({
                                type: "warning",
                                text: `👤 Unknown Visitor: ${data.name || "Unknown"}`
                            });
                        }
                        return prev;
                    });
                }

                // Update detected faces state
                setFaces((prev) => {
                    const filtered = prev.filter((face) => {
                        if (face.track_id === data.track_id) return false;

                        if (
                            data.recognized &&
                            face.recognized &&
                            face.user_id === data.user_id
                        )
                            return false;

                        if (
                            data.recognized &&
                            face.name === data.name
                        )
                            return false;

                        return true;
                    });

                    return [
                        ...filtered,
                        {
                            ...data,
                            lastSeen: Date.now()
                        }
                    ];
                });
            };

            console.log("CREATING INTERVAL");
            frameInterval.current = setInterval(() => {
                if (
                    !socket.current ||
                    socket.current.readyState !== WebSocket.OPEN ||
                    !webcamRef.current ||
                    frameInFlight.current
                ) {
                    return;
                }

                const image = webcamRef.current.getScreenshot();
                if (!image) return;

                frameInFlight.current = true;
                socket.current.send(image);

                // Safe fallback timeout
                setTimeout(() => {
                    frameInFlight.current = false;
                }, 2000);
            }, 300);
        }

        return () => {
            if (frameInterval.current) {
                console.log("CLEARING INTERVAL");
                clearInterval(frameInterval.current);
                frameInterval.current = null;
            }
            if (socket.current) {
                console.log("CLOSING WS");
                socket.current.close();
                socket.current = null;
            }
            frameInFlight.current = false;
            setFaces([]);
        };
    }, [isRunning]);

    // Handle periodic cleanup of stale faces (stale threshold = 2 seconds)
    useEffect(() => {
        const cleanup = setInterval(() => {
            setFaces((prev) =>
                prev.filter((face) => Date.now() - face.lastSeen < STALE_MS)
            );
        }, 1000);

        return () => clearInterval(cleanup);
    }, []);

    // Draw boxes when the faces state changes
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // ENTRY/EXIT LINE
        ctx.beginPath();
        ctx.moveTo(0, 240);
        ctx.lineTo(canvas.width, 240);
        ctx.strokeStyle = "yellow";
        ctx.lineWidth = 3;
        ctx.stroke();

        faces.forEach((face) => {
            if (!face.bbox) return;

            const [x1, y1, x2, y2] = face.bbox;

            // Green for recognized, Red for spoof or unknown
            const color = face.spoof ? "red" : (face.recognized ? "green" : "red");

            ctx.strokeStyle = color;
            ctx.lineWidth = 3;
            ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

            ctx.fillStyle = color;
            ctx.font = "18px Arial";
            ctx.fillText(
                face.name || "Unknown",
                x1,
                y1 > 20 ? y1 - 10 : 20
            );
        });
    }, [faces]);

    const startRecognition = () => {
        console.log("START CLICKED");
        setIsRunning(true);
    };

    const stopRecognition = () => {
        console.log("STOP CLICKED");
        setIsRunning(false);
    };

    return (
        <div className="max-w-7xl mx-auto relative">
            {/* Premium Toast Notifications */}
            {notification && (
                <div
                    className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-6 py-4 rounded-2xl shadow-xl border transition-all duration-300 transform translate-y-0 opacity-100 ${
                        notification.type === "error"
                            ? "bg-red-50 border-red-200 text-red-800"
                            : notification.type === "warning"
                            ? "bg-amber-50 border-amber-200 text-amber-800"
                            : "bg-green-50 border-green-200 text-green-800"
                    }`}
                >
                    <span className="text-xl">
                        {notification.type === "error"
                            ? "🚫"
                            : notification.type === "warning"
                            ? "👤"
                            : "✅"}
                    </span>
                    <div>
                        <p className="font-semibold">{notification.text}</p>
                        {notification.subtext && (
                            <p className="text-xs opacity-90">{notification.subtext}</p>
                        )}
                    </div>
                </div>
            )}

            <div className="mb-8">
                <h1 className="text-4xl font-bold">
                    Live Recognition
                </h1>

                <p className="text-slate-500 mt-2">
                    Real-time AI face recognition
                </p>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6">
                        <div
                            className="relative mx-auto"
                            style={{
                                width: FACE_WIDTH,
                                height: FACE_HEIGHT,
                            }}
                        >
                            <Webcam
                                ref={webcamRef}
                                screenshotFormat="image/jpeg"
                                width={FACE_WIDTH}
                                height={FACE_HEIGHT}
                                mirrored
                            />

                            <canvas
                                ref={canvasRef}
                                width={FACE_WIDTH}
                                height={FACE_HEIGHT}
                                style={{
                                    position: "absolute",
                                    top: 0,
                                    left: 0,
                                    pointerEvents: "none",
                                }}
                            />
                        </div>

                        <div className="flex gap-4 mt-6">
                            <button
                                onClick={startRecognition}
                                disabled={isRunning}
                                className="bg-green-600 text-white px-6 py-3 rounded-xl disabled:opacity-50"
                            >
                                Start Recognition
                            </button>

                            <button
                                onClick={stopRecognition}
                                disabled={!isRunning}
                                className="bg-red-600 text-white px-6 py-3 rounded-xl disabled:opacity-50"
                            >
                                Stop Recognition
                            </button>
                        </div>
                    </div>
                </div>

                <div>
                    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6">
                        <div className="mb-6">
                            <div
                                className={`inline-flex px-3 py-1 rounded-full text-sm ${
                                    isRunning
                                        ? "bg-green-100 text-green-700"
                                        : "bg-red-100 text-red-700"
                                }`}
                            >
                                {isRunning
                                    ? "Recognition Running"
                                    : "Recognition Stopped"}
                            </div>
                        </div>

                        <h2 className="text-xl font-semibold mb-4">
                            Detected Faces
                        </h2>

                        {faces.length === 0 && (
                            <div className="text-slate-500">
                                No faces detected
                            </div>
                        )}

                        {faces.map((face) => (
                            <div
                                key={face.track_id}
                                className="border rounded-2xl p-4 mb-4"
                            >
                                <div className="flex justify-between">
                                    <h3 className="font-semibold">
                                        {face.name || "Unknown"}
                                    </h3>

                                    <span
                                        className={
                                            face.spoof
                                                ? "text-red-600 font-bold"
                                                : face.recognized
                                                ? "text-green-600"
                                                : "text-amber-600"
                                        }
                                    >
                                        {face.spoof
                                            ? "SPOOF"
                                            : face.recognized
                                            ? "Recognized"
                                            : "Unknown"}
                                    </span>
                                </div>

                                <p className="text-sm text-slate-500 mt-2">
                                    Similarity:{" "}
                                    {typeof face.similarity === "number"
                                        ? face.similarity.toFixed(2)
                                        : "N/A"}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Recognize;