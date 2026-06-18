import {
  LayoutDashboard,
  UserPlus,
  ScanFace,
  Users,
  Shield,
} from "lucide-react";

import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const links = [
    {
      name: "Dashboard",
      icon: LayoutDashboard,
      path: "/dashboard",
    },
    {
      name: "Register",
      icon: UserPlus,
      path: "/register",
    },
    {
      name: "Recognize",
      icon: ScanFace,
      path: "/recognize",
    },
    {
      name: "Users",
      icon: Users,
      path: "/users",
    },
  ];

  return (
    <aside className="w-72 min-h-screen bg-slate-900 text-white flex flex-col">
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <Shield size={34} />
          <div>
            <h1 className="font-bold text-xl">
              VisionPass
            </h1>
            <p className="text-xs text-slate-400">
              Visitor Intelligence
            </p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4">
        {links.map((link) => {
          const Icon = link.icon;

          return (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl mb-2 transition ${
                  isActive
                    ? "bg-indigo-600"
                    : "hover:bg-slate-800"
                }`
              }
            >
              <Icon size={20} />
              {link.name}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}