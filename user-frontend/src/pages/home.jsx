import Camera from "../components/camera";
import useRecognition from "../hooks/useRecognition";

function Home() {
    const { webcamRef } = useRecognition();

    return (
        <div className="w-screen h-screen overflow-hidden bg-black">
            <Camera
                webcamRef={webcamRef}
            />
        </div>
    );
}

export default Home;