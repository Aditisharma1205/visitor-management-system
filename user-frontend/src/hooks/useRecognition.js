import { useEffect, useRef, useState } from "react";
import { WS_URL } from "../api/config";

const STALE_MS = 2000;

export default function useRecognition() {
    const webcamRef = useRef(null);

    const frameInterval = useRef(null);
    const socket = useRef(null);
    const frameInFlight = useRef(false);

    const [faces, setFaces] = useState([]);

    // WebSocket Connection
    useEffect(() => {
        console.log("CREATING WS CONNECTION");

        socket.current = new WebSocket(WS_URL);

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

            if (data.type === "spoof") {
                const spoofId = `spoof_${data.bbox.map(Math.round).join("_")}`;

                setFaces((prev) => {
                    const filtered = prev.filter(
                        (f) => f.track_id !== spoofId
                    );

                    return [
                        ...filtered,
                        {
                            track_id: spoofId,
                            name: "SPOOF DETECTED",
                            recognized: false,
                            spoof: true,
                            bbox: data.bbox,
                            lastSeen: Date.now(),
                        },
                    ];
                });

                return;
            }

            if (data.type === "frame_summary") {
                frameInFlight.current = false;

                setFaces((prev) =>
                    prev.filter(
                        (face) =>
                            face.spoof ||
                            data.active_track_ids.includes(face.track_id)
                    )
                );

                return;
            }

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
                        lastSeen: Date.now(),
                    },
                ];
            });
        };

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
            console.log(image ? image.length : "NO IMAGE");
            socket.current.send(image);

            setTimeout(() => {
                frameInFlight.current = false;
            }, 2000);
        }, 300);

        return () => {
            if (frameInterval.current) {
                clearInterval(frameInterval.current);
            }

            if (socket.current) {
                socket.current.close();
            }

            frameInFlight.current = false;
            setFaces([]);
        };
    }, []);

    // Remove stale faces
    useEffect(() => {
        const cleanup = setInterval(() => {
            setFaces((prev) =>
                prev.filter(
                    (face) =>
                        Date.now() - face.lastSeen < STALE_MS
                )
            );
        }, 1000);

        return () => clearInterval(cleanup);
    }, []);

    return {
        webcamRef,
        faces,
    };
}