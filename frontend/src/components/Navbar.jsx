import { Link } from "react-router-dom";

function Navbar() {
    return (
        <nav
            style={{
                display: "flex",
                gap: "20px",
                padding: "15px",
                backgroundColor: "#f0f0f0",
                marginBottom: "20px",
            }}
        >

            <Link to="/dashboard">Dashboard</Link>

            <Link to="/register">
                Register
            </Link>

            <Link to="/recognize">
                Recognize
            </Link>

            <Link to="/users">
                Users
            </Link>
        </nav>
    );
}

export default Navbar;