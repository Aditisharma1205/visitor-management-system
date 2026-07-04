import { useEffect, useState } from "react";
import { Search as SearchIcon, Calendar, Clock, ArrowRight, User, AlertCircle, RefreshCw } from "lucide-react";
import api, { API_BASE_URL } from "../services/api";

function Search() {
    const [searchTerm, setSearchTerm] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [logs, setLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedVisitor, setSelectedVisitor] = useState(null);
    const [timelineLogs, setTimelineLogs] = useState([]);
    const [isTimelineLoading, setIsTimelineLoading] = useState(false);

    // Fetch search results when filters change
    useEffect(() => {
        setIsLoading(true);

        const params = {};
        if (searchTerm) params.name = searchTerm;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        api.get("/visitor/search", { params })
            .then((res) => {
                setLogs(res.data);
                setIsLoading(false);
            })
            .catch((err) => {
                console.error("Search error:", err);
                setIsLoading(false);
            });
    }, [searchTerm, startDate, endDate]);

    // Fetch timeline for selected visitor
    useEffect(() => {
        if (!selectedVisitor) {
            setTimelineLogs([]);
            return;
        }

        setIsTimelineLoading(true);

        const params = {};
        if (selectedVisitor.type === "known") {
            params.user_id = selectedVisitor.id;
        } else {
            params.unknown_visitor_id = selectedVisitor.id;
        }

        api.get("/visitor/search", { params })
            .then((res) => {
                setTimelineLogs(res.data);
                setIsTimelineLoading(false);
            })
            .catch((err) => {
                console.error("Timeline error:", err);
                setIsTimelineLoading(false);
            });
    }, [selectedVisitor]);

    const handleClearFilters = () => {
        setSearchTerm("");
        setStartDate("");
        setEndDate("");
    };

    const getSnapshotUrl = (path) => {
        if (!path) return null;
        return `${API_BASE_URL}/${path.replace(/\\/g, "/")}`;
    };

    return (
        <div className="max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-4xl font-bold">Visitor Intelligence Search</h1>
                <p className="text-slate-500 mt-2">
                    Search logs by name, filter by date ranges, and view detailed user timelines.
                </p>
            </div>

            {/* Filter Bar */}
            <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 mb-8 flex flex-wrap gap-4 items-end">
                <div className="flex-1 min-w-[250px]">
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Search Name</label>
                    <div className="relative">
                        <SearchIcon className="absolute left-3 top-3.5 h-5 w-5 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search by name (e.g., John, Unknown)..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>
                </div>

                <div className="w-[180px]">
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Start Date</label>
                    <div className="relative">
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>
                </div>

                <div className="w-[180px]">
                    <label className="block text-sm font-semibold text-slate-700 mb-2">End Date</label>
                    <div className="relative">
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>
                </div>

                <button
                    onClick={handleClearFilters}
                    className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl transition"
                >
                    Clear
                </button>
            </div>

            {/* Split Screen Layout */}
            <div className="grid lg:grid-cols-5 gap-8">
                {/* Search Results Table */}
                <div className="lg:col-span-3 bg-white rounded-3xl border border-slate-200 shadow-sm p-6 overflow-hidden">
                    <h2 className="text-xl font-bold mb-4 text-slate-800">Matching Logs</h2>
                    
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12 text-slate-500 gap-2">
                            <RefreshCw className="h-5 w-5 animate-spin" /> Loading logs...
                        </div>
                    ) : logs.length === 0 ? (
                        <div className="text-slate-500 py-12 text-center">No matching visitor logs found.</div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full border-collapse">
                                <thead>
                                    <tr className="border-b bg-slate-50 text-slate-600 text-sm font-semibold text-left">
                                        <th className="p-3">Visitor</th>
                                        <th className="p-3">Entry Time</th>
                                        <th className="p-3">Duration</th>
                                        <th className="p-3">Status</th>
                                        <th className="p-3 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {logs.map((log) => (
                                        <tr
                                            key={log.visitor_log_id}
                                            className={`border-b hover:bg-slate-50 text-slate-700 transition cursor-pointer ${
                                                selectedVisitor &&
                                                selectedVisitor.id === (log.user_id || log.unknown_visitor_id) &&
                                                selectedVisitor.type === (log.is_known ? "known" : "unknown")
                                                    ? "bg-slate-50 border-l-4 border-l-indigo-600"
                                                    : ""
                                            }`}
                                            onClick={() =>
                                                setSelectedVisitor({
                                                    type: log.is_known ? "known" : "unknown",
                                                    id: log.user_id || log.unknown_visitor_id,
                                                    name: log.name || "Unknown"
                                                })
                                            }
                                        >
                                            <td className="p-3 flex items-center gap-3">
                                                {log.image_path ? (
                                                    <img
                                                        src={getSnapshotUrl(log.image_path)}
                                                        alt={log.name || "Unknown"}
                                                        className="w-10 h-10 rounded-full object-cover border"
                                                        onError={(e) => { e.target.src = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80" }}
                                                    />
                                                ) : (
                                                    <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold border">
                                                        {(log.name || "?").charAt(0)}
                                                    </div>
                                                )}
                                                <div>
                                                    <div className="font-semibold text-slate-800">{log.name || "Unknown"}</div>
                                                    <div className="text-xs text-slate-400">
                                                        {log.is_known ? "Registered" : "Unknown"}
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="p-3 text-sm">
                                                {new Date(log.entry_time).toLocaleString()}
                                            </td>
                                            <td className="p-3 text-sm">{log.duration || "-"}</td>
                                            <td className="p-3 text-sm">
                                                <span
                                                    className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                                                        log.status === "INSIDE"
                                                            ? "bg-green-100 text-green-700"
                                                            : "bg-slate-100 text-slate-700"
                                                    }`}
                                                >
                                                    {log.status}
                                                </span>
                                            </td>
                                            <td className="p-3 text-right">
                                                <button className="text-indigo-600 hover:text-indigo-800 font-semibold text-sm flex items-center gap-1 ml-auto">
                                                    Timeline <ArrowRight className="h-4 w-4" />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Timeline Panel */}
                <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200 shadow-sm p-6 min-h-[500px]">
                    <h2 className="text-xl font-bold mb-4 text-slate-800">Timeline View</h2>

                    {!selectedVisitor ? (
                        <div className="flex flex-col items-center justify-center h-[400px] text-slate-400 text-center">
                            <User className="h-16 w-16 mb-4 opacity-50" />
                            <p className="font-semibold">No visitor selected</p>
                            <p className="text-sm mt-1">Select a visitor from the list to view their entry/exit timeline.</p>
                        </div>
                    ) : isTimelineLoading ? (
                        <div className="flex items-center justify-center h-[400px] text-slate-500 gap-2">
                            <RefreshCw className="h-5 w-5 animate-spin" /> Loading timeline...
                        </div>
                    ) : (
                        <div>
                            <div className="mb-6 flex items-center gap-4 bg-slate-50 p-4 rounded-2xl border">
                                <div className="p-3 bg-indigo-100 text-indigo-700 rounded-xl">
                                    <User className="h-6 w-6" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-slate-800 text-lg">{selectedVisitor.name}</h3>
                                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700">
                                        {selectedVisitor.type === "known" ? "Registered User" : "Unknown Visitor"}
                                    </span>
                                </div>
                            </div>

                            {timelineLogs.length === 0 ? (
                                <div className="text-slate-500 py-12 text-center">No timeline records found.</div>
                            ) : (
                                <div className="relative border-l-2 border-slate-200 ml-4 pl-6 space-y-8">
                                    {timelineLogs.map((item, idx) => (
                                        <div key={item.visitor_log_id} className="relative">
                                            {/* Vertical Timeline Indicator dot */}
                                            <span className="absolute -left-[31px] top-1 bg-white border-2 border-indigo-600 rounded-full w-4 h-4" />

                                            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 hover:shadow-md transition">
                                                <div className="flex justify-between items-start gap-4 mb-3">
                                                    <div className="flex items-center gap-2">
                                                        <Clock className="h-4 w-4 text-indigo-500" />
                                                        <span className="text-sm font-semibold text-slate-700">
                                                            {new Date(item.entry_time).toLocaleDateString()}
                                                        </span>
                                                    </div>
                                                    <span
                                                        className={`px-2 py-0.5 rounded text-xs font-semibold ${
                                                            item.status === "INSIDE"
                                                                ? "bg-green-100 text-green-700"
                                                                : "bg-slate-100 text-slate-700"
                                                        }`}
                                                    >
                                                        {item.status}
                                                    </span>
                                                </div>

                                                <div className="space-y-2 text-sm text-slate-600">
                                                    <div>
                                                        <strong>Checked In:</strong>{" "}
                                                        {new Date(item.entry_time).toLocaleTimeString()}
                                                    </div>
                                                    {item.exit_time && (
                                                        <div>
                                                            <strong>Checked Out:</strong>{" "}
                                                            {new Date(item.exit_time).toLocaleTimeString()}
                                                        </div>
                                                    )}
                                                    <div>
                                                        <strong>Total Duration:</strong> {item.duration}
                                                    </div>
                                                </div>

                                                {/* Snapshot images if present */}
                                                <div className="flex gap-2 mt-4">
                                                    {item.entry_snapshot && (
                                                        <div className="flex-1">
                                                            <p className="text-[10px] text-slate-400 font-semibold mb-1">ENTRY SNAPSHOT</p>
                                                            <img
                                                                src={getSnapshotUrl(item.entry_snapshot)}
                                                                alt="Entry Snapshot"
                                                                className="rounded-xl border object-cover h-24 w-full"
                                                                onError={(e) => { e.target.style.display = 'none'; }}
                                                            />
                                                        </div>
                                                    )}
                                                    {item.exit_snapshot && (
                                                        <div className="flex-1">
                                                            <p className="text-[10px] text-slate-400 font-semibold mb-1">EXIT SNAPSHOT</p>
                                                            <img
                                                                src={getSnapshotUrl(item.exit_snapshot)}
                                                                alt="Exit Snapshot"
                                                                className="rounded-xl border object-cover h-24 w-full"
                                                                onError={(e) => { e.target.style.display = 'none'; }}
                                                            />
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Search;
