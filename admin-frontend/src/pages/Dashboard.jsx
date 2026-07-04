import { useEffect, useState } from "react";

import CurrentVisitorsTable from "../components/CurrentVisitorsTable";
import VisitorHistoryTable from "../components/VisitorHistoryTable";
import UnknownVisitorsTable from "../components/UnknownVisitorsTable";

import StatsCard from "../components/StatsCard";
import api from "../services/api";

import {
    Users,
    UserCheck,
    ClipboardList,
    AlertTriangle,
    LogIn,
    LogOut,
} from "lucide-react";

const REFRESH_MS = 5000;

function Dashboard() {

    const [stats, setStats] = useState({
        current_visitors: 0,
        total_visits: 0,
        unknown_visitors: 0,
        registered_users: 0,
        todays_entries: 0,
        todays_exits: 0,
    });
    const sectionClass =
    "bg-white rounded-3xl shadow-sm border border-slate-200 p-6 mt-8";

    useEffect(() => {

        const fetchStats = () => {
            api.get("/dashboard/stats")
                .then((res) => {
                    setStats(res.data);
                })
                .catch((err) => {
                    console.error(err);
                });
        };

        fetchStats();

        const interval = setInterval(fetchStats, REFRESH_MS);

        return () => clearInterval(interval);

    }, []);

    return (

            <div className="mb-10">

            <h1 className="text-4xl font-bold mb-2">
                Dashboard
            </h1>

            <p className="text-slate-500">
                Real-time visitor analytics
            </p>


            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mt-8">

                <StatsCard
                    title="Active Visitors Inside"
                    value={stats.current_visitors}
                    icon={UserCheck}
                />

                <StatsCard
                    title="Today's Entries"
                    value={stats.todays_entries || 0}
                    icon={LogIn}
                />

                <StatsCard
                    title="Today's Exits"
                    value={stats.todays_exits || 0}
                    icon={LogOut}
                />

                <StatsCard
                    title="Unknown Visitors"
                    value={stats.unknown_visitors}
                    icon={AlertTriangle}
                />

            </div>

            <div className={sectionClass}>

                <h2 className="text-2xl font-semibold mb-4">

                    Current Visitors

                </h2>

                <CurrentVisitorsTable />

            </div>

            <div className={sectionClass}>

                <h2 className="text-2xl font-semibold mb-4">

                    Visitor History

                </h2>

                <VisitorHistoryTable />

            </div>

            <div className={sectionClass}>

                <h2 className="text-2xl font-semibold mb-4">

                    Unknown Visitors

                </h2>

                <UnknownVisitorsTable />

            </div>

        </div>

    );
}

export default Dashboard;