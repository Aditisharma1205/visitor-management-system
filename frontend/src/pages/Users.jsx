import { useEffect, useState } from "react";
import api from "../services/api";

function Users() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await api.get("/users");
            setUsers(response.data);
        } catch (error) {
            console.error(error);
            alert("Failed to fetch users");
        } finally {
            setLoading(false);
        }
    };

    const deleteUser = async (userId) => {
        const confirmDelete = window.confirm(
            "Are you sure you want to delete this user?"
        );

        if (!confirmDelete) {
            return;
        }

        try {
            await api.delete(`/users/${userId}`);

            setUsers((prevUsers) =>
                prevUsers.filter(
                    (user) => user.id !== userId
                )
            );

            alert("User deleted successfully");
        } catch (error) {
            console.error(error);
            alert("Failed to delete user");
        }
    };

    if (loading) {
        return <h2>Loading users...</h2>;
    }

    return (
        <div
            style={{
                maxWidth: "900px",
                margin: "40px auto",
                padding: "20px",
            }}
        >
            <h1>Registered Users</h1>

            {users.length === 0 ? (
                <p>No users found.</p>
            ) : (
                <table
                    border="1"
                    cellPadding="10"
                    style={{
                        width: "100%",
                        borderCollapse: "collapse",
                    }}
                >
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Registered At</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>
                        {users.map((user) => (
                            <tr key={user.id}>
                                <td>{user.id}</td>

                                <td>{user.name}</td>

                                <td>
                                    {new Date(
                                        user.created_at
                                    ).toLocaleString()}
                                </td>

                                <td>
                                    <button
                                        onClick={() =>
                                            deleteUser(
                                                user.id
                                            )
                                        }
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default Users;