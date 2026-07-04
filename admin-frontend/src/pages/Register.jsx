import { useState } from "react";
import { UserPlus, Upload } from "lucide-react";
import api from "../services/api";

function Register() {
    const [name, setName] = useState("");
    const [photo, setPhoto] = useState(null);
    const [preview, setPreview] = useState(null);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    const handlePhotoChange = (e) => {
        const file = e.target.files[0];

        if (!file) return;

        setPhoto(file);
        setPreview(URL.createObjectURL(file));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!name || !photo) {
            setMessage(
                "Please enter name and select a photo."
            );
            return;
        }

        try {
            setLoading(true);

            const formData = new FormData();

            formData.append("name", name);
            formData.append("photo", photo);

            const response = await api.post(
                "/register",
                formData,
                {
                    headers: {
                        "Content-Type":
                            "multipart/form-data",
                    },
                }
            );

            setMessage(response.data.message);

            setName("");
            setPhoto(null);
            setPreview(null);

            document.getElementById(
                "photoInput"
            ).value = "";
        } catch (error) {
            console.error(error);

            if (
                error.response &&
                error.response.data
            ) {
                setMessage(
                    error.response.data.detail
                );
            } else {
                setMessage(
                    "Registration failed."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto">

            <div className="mb-8">
                <h1 className="text-4xl font-bold">
                    Register User
                </h1>

                <p className="text-slate-500 mt-2">
                    Add a new user to the VisionPass database
                </p>
            </div>

            <div className="bg-white rounded-3xl shadow-sm border border-slate-200 p-8">

                <form
                    onSubmit={handleSubmit}
                    className="space-y-6"
                >

                    <div>
                        <label className="block mb-2 font-medium">
                            Full Name
                        </label>

                        <input
                            type="text"
                            value={name}
                            onChange={(e) =>
                                setName(
                                    e.target.value
                                )
                            }
                            placeholder="Enter user name"
                            className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>

                    <div>

                        <label className="block mb-2 font-medium">
                            Upload Photo
                        </label>

                        <label
                            htmlFor="photoInput"
                            className="border-2 border-dashed border-slate-300 rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer hover:border-indigo-500 transition"
                        >
                            <Upload
                                size={40}
                            />

                            <p className="mt-3 text-slate-600">
                                Click to upload image
                            </p>

                            <p className="text-sm text-slate-400">
                                JPG, PNG supported
                            </p>
                        </label>

                        <input
                            id="photoInput"
                            type="file"
                            accept="image/*"
                            onChange={
                                handlePhotoChange
                            }
                            className="hidden"
                        />
                    </div>

                    {preview && (
                        <div className="flex justify-center">
                            <img
                                src={preview}
                                alt="Preview"
                                className="w-64 h-64 object-cover rounded-2xl border"
                            />
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-indigo-600 text-white py-3 rounded-xl hover:bg-indigo-700 transition flex items-center justify-center gap-2"
                    >
                        <UserPlus size={20} />

                        {loading
                            ? "Registering..."
                            : "Register User"}
                    </button>

                </form>

                {message && (
                    <div
                        className={`mt-6 p-4 rounded-xl ${
                            message
                                .toLowerCase()
                                .includes(
                                    "success"
                                )
                                ? "bg-green-100 text-green-700"
                                : "bg-red-100 text-red-700"
                        }`}
                    >
                        {message}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Register;