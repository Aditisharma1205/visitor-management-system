import { NavLink } from "react-router-dom";

export default function DashboardLayout({ children }) {
    return (
        <div className="flex min-h-screen bg-gray-100">

            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md hidden md:block">
                <div className="p-5 text-xl font-bold border-b">
                    VisionPass
                </div>

                <nav className="p-4 space-y-2">

                    <NavLink to="/" className="block p-2 rounded hover:bg-gray-100">
                        🏠 Dashboard
                    </NavLink>

                    <NavLink to="/register" className="block p-2 rounded hover:bg-gray-100">
                        📝 Register
                    </NavLink>

                    <NavLink to="/recognize" className="block p-2 rounded hover:bg-gray-100">
                        📷 Recognize
                    </NavLink>

                    <NavLink to="/users" className="block p-2 rounded hover:bg-gray-100">
                        👥 Users
                    </NavLink>

                    <NavLink to="/logs" className="block p-2 rounded hover:bg-gray-100">
                        📜 Logs
                    </NavLink>

                    <NavLink to="/unknown" className="block p-2 rounded hover:bg-gray-100">
                        ⚠ Unknown
                    </NavLink>

                </nav>
            </aside>

            {/* Main */}
            <main className="flex-1 p-6">
                {children}
            </main>

        </div>
    );
}