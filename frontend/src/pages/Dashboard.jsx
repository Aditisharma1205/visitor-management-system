import { useEffect, useState } from "react";

import CurrentVisitorsTable from "../components/CurrentVisitorsTable";
import VisitorHistoryTable from "../components/VisitorHistoryTable";
import UnknownVisitorsTable from "../components/UnknownVisitorsTable";

import StatsCard from "../components/StatsCard";

import {
    Users,
    UserCheck,
    ClipboardList,
    AlertTriangle,
} from "lucide-react";

function Dashboard() {

    const [stats, setStats] = useState({
        current_visitors: 0,
        total_visits: 0,
        unknown_visitors: 0,
        registered_users: 0,
    });
    const sectionClass =
    "bg-white rounded-3xl shadow-sm border border-slate-200 p-6 mt-8";

    useEffect(() => {

        fetch(
            "http://127.0.0.1:8000/dashboard/stats"
        )
            .then((res) => res.json())
            .then((data) => {
                setStats(data);
            })
            .catch((err) => {
                console.error(err);
            });

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
                    title="Visitors Inside"
                    value={stats.current_visitors}
                    icon={UserCheck}
                />

                <StatsCard
                    title="Registered Users"
                    value={stats.registered_users}
                    icon={Users}
                />

                <StatsCard
                    title="Total Visits"
                    value={stats.total_visits}
                    icon={ClipboardList}
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