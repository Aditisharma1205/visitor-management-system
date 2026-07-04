import Webcam from "react-webcam";

function Camera({ webcamRef }) {
    return (
        <div className="relative w-full h-full">

            <Webcam
                ref={webcamRef}
                mirrored
                screenshotFormat="image/jpeg"
                videoConstraints={{
                    facingMode: "user"
                }}
                className="absolute inset-0 w-full h-full object-cover"
            />

        </div>
    );
}

export default Camera;