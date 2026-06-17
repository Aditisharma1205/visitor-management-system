import { Link, useLocation } from "react-router-dom";
import {
    LayoutDashboard,
    UserPlus,
    ScanFace,
    Users,
} from "lucide-react";

function Layout({ children }) {
    const location = useLocation();

    const menuItems = [
        {
            name: "Dashboard",
            path: "/dashboard",
            icon: LayoutDashboard,
        },
        {
            name: "Register",
            path: "/register",
            icon: UserPlus,
        },
        {
            name: "Recognize",
            path: "/recognize",
            icon: ScanFace,
        },
        {
            name: "Users",
            path: "/users",
            icon: Users,
        },
    ];

    return (
        <div className="min-h-screen flex bg-gray-100">

            <aside className="w-64 bg-slate-900 text-white shadow-lg">

                <div className="p-6 text-2xl font-bold border-b border-slate-700">
                    VisionPass
                </div>

                <nav className="mt-6">

                    {menuItems.map((item) => {

                        const Icon = item.icon;

                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-3 px-6 py-4 transition duration-200 ${
                                    location.pathname === item.path
                                        ? "bg-blue-600"
                                        : "hover:bg-slate-800"
                                }`}
                            >
                                <Icon size={20} />

                                {item.name}
                            </Link>
                        );
                    })}

                </nav>

            </aside>

            <main className="flex-1 p-8">

                {children}

            </main>

        </div>
    );
}

export default Layout;