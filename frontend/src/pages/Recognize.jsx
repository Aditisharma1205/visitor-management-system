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
            }, 5000);
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
    <div className="max-w-7xl mx-auto">

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

                    <div className="flex gap-4 mt-6">

                        <button
                            onClick={() =>
                                setIsRunning(true)
                            }
                            className="bg-green-600 text-white px-6 py-3 rounded-xl"
                        >
                            Start Recognition
                        </button>

                        <button
                            onClick={() =>
                                setIsRunning(false)
                            }
                            className="bg-red-600 text-white px-6 py-3 rounded-xl"
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
        {
            isRunning
                ? "Recognition Running"
                : "Recognition Stopped"
        }
    </div>

</div>
    <h2 className="text-xl font-semibold mb-4">
        Detected Faces
    </h2>
        {
    faces.length === 0 && (
        <div className="text-slate-500">
            No faces detected
        </div>
    )
}
{
    faces.map((face, index) => (

        <div
            key={index}
            className="border rounded-2xl p-4 mb-4"
        >

            <div className="flex justify-between">

                <h3 className="font-semibold">
                    {face.name}
                </h3>

                <span
                    className={
                        face.recognized
                            ? "text-green-600"
                            : "text-red-600"
                    }
                >
                    {
                        face.recognized
                            ? "Recognized"
                            : "Unknown"
                    }
                </span>

            </div>

            <p className="text-sm text-slate-500 mt-2">
                Similarity:
                {" "}
                {face.similarity.toFixed(2)}
            </p>

        </div>
    ))
}
        </div>
        </div>
        </div>
        </div>
    );
}

export default Recognize;