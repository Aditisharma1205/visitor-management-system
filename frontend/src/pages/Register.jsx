import { useState } from "react";
import api from "../services/api";

function Register() {
    const [name, setName] = useState("");

    const [photo, setPhoto] = useState(null);

    const [message, setMessage] = useState("");

    const [loading, setLoading] = useState(false);

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

            formData.append(
                "name",
                name
            );

            formData.append(
                "photo",
                photo
            );

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

            setMessage(
                response.data.message
            );

            setName("");

            setPhoto(null);

            document.getElementById(
                "photoInput"
            ).value = "";
        }

        catch (error) {

            console.error(error);

            if (
                error.response &&
                error.response.data
            ) {
                setMessage(
                    error.response.data.detail
                );
            }

            else {
                setMessage(
                    "Registration failed."
                );
            }
        }

        finally {
            setLoading(false);
        }
    };

    return (
        <div
            style={{
                maxWidth: "500px",
                margin: "50px auto",
                padding: "30px",
                border: "1px solid #ccc",
                borderRadius: "10px",
            }}
        >
            <h1>
                Register User
            </h1>

            <form
                onSubmit={handleSubmit}
            >
                <div
                    style={{
                        marginBottom: "20px",
                    }}
                >
                    <label>
                        Name
                    </label>

                    <br />

                    <input
                        type="text"
                        value={name}
                        onChange={(e) =>
                            setName(
                                e.target.value
                            )
                        }
                        style={{
                            width: "100%",
                            padding: "10px",
                        }}
                    />
                </div>

                <div
                    style={{
                        marginBottom: "20px",
                    }}
                >
                    <label>
                        Photo
                    </label>

                    <br />

                    <input
                        id="photoInput"
                        type="file"
                        accept="image/*"
                        onChange={(e) =>
                            setPhoto(
                                e.target.files[0]
                            )
                        }
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                >
                    {
                        loading
                            ? "Registering..."
                            : "Register"
                    }
                </button>
            </form>

            {
                message && (
                    <p
                        style={{
                            marginTop: "20px",
                        }}
                    >
                        {message}
                    </p>
                )
            }
        </div>
    );
}

export default Register;