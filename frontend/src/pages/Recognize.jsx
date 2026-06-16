import { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import api from "../services/api";

function Recognize() {
    const webcamRef = useRef(null);
    const canvasRef = useRef(null);

    const [isRunning, setIsRunning] = useState(false);

    const [faces, setFaces] = useState([]);

    useEffect(() => {
        let interval;

        if (isRunning) {
            interval = setInterval(() => {
                recognizeFace();
            }, 2000);
        }

        return () => {
            clearInterval(interval);
        };
    }, [isRunning]);
    const drawBoxes = (faces) => {
        const canvas = canvasRef.current;

        if (!canvas) return;

        const ctx = canvas.getContext("2d");

        ctx.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );

        faces.forEach((face) => {
            const [x1, y1, x2, y2] =
                face.bbox;

            ctx.strokeStyle =
                face.recognized
                    ? "green"
                    : "red";

            ctx.lineWidth = 3;

            ctx.strokeRect(
                x1,
                y1,
                x2 - x1,
                y2 - y1
            );

            ctx.fillStyle =
                face.recognized
                    ? "green"
                    : "red";

            ctx.font =
                "18px Arial";

            ctx.fillText(
                face.name,
                x1,
                y1 - 10
            );
        });
    };

    const recognizeFace = async () => {
        try {
            const imageSrc = webcamRef.current.getScreenshot();

            if (!imageSrc) {
                return;
            }

            const blob = await fetch(imageSrc).then((res) =>
                res.blob()
            );

            const formData = new FormData();

            formData.append(
                "photo",
                blob,
                "webcam.jpg"
            );

            const response = await api.post(
                "/recognize",
                formData,
                {
                    headers: {
                        "Content-Type":
                            "multipart/form-data",
                    },
                }
            );

            setFaces(response.data.faces || []);
            drawBoxes(response.data.faces || []);
        } catch (error) {
            console.error(error);

            if (
                error.response &&
                error.response.data
            ) {
                setResult({
                    recognized: false,
                    name: "",
                    similarity: 0,
                    message:
                        error.response.data.detail,
                });
            }
        }
    };

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "20px",
                padding: "20px",
            }}
        >
            <h1>Live Face Recognition</h1>

                    <div
            style={{
                position: "relative",
                width: 640,
                height: 480,
            }}
        >
            <Webcam
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                width={640}
                height={480}
                mirrored
            />

            <canvas
                ref={canvasRef}
                width={640}
                height={480}
                style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    pointerEvents: "none",
                }}
            />
        </div>
            <div
                style={{
                    display: "flex",
                    gap: "10px",
                }}
            >
                <button
                    onClick={() =>
                        setIsRunning(true)
                    }
                >
                    Start Recognition
                </button>

                <button
                    onClick={() =>
                        setIsRunning(false)
                    }
                >
                    Stop Recognition
                </button>
            </div>

            <div>
            <h2>Detected Faces</h2>

            {faces.length === 0 ? (
                <p>No faces detected</p>
            ) : (
                faces.map((face, index) => (
                    <div key={index}>
                        <strong>
                            {face.name}
                        </strong>

                        {" | "}

                        {face.recognized
                            ? "Recognized"
                            : "Unknown"}

                        {" | "}

                        Similarity:
                        {" "}
                        {face.similarity.toFixed(
                            2
                        )}
                    </div>
                ))
            )}
        </div>
        </div>
    );
}

export default Recognize;