import { useEffect, useState } from "react";
import api from "../services/api";

const REFRESH_MS = 5000;

function VisitorHistoryTable() {
    const [history, setHistory] = useState([]);

    useEffect(() => {

        const fetchHistory = () => {
            api.get("/visitor/history")
                .then((res) => setHistory(res.data))
                .catch((err) => console.error(err));
        };

        fetchHistory();

        const interval = setInterval(fetchHistory, REFRESH_MS);

        return () => clearInterval(interval);

    }, []);

    return (
        <div style={{ marginTop: "40px" }}>

            <table className="w-full"
                border="1"
                cellPadding="10"
                style={{
                    width: "100%",
                    borderCollapse: "collapse",
                }}
            >
                <thead className="border-b bg-gray-50">
                    <tr className="border-b hover:bg-gray-50">
                        <th className="text-left p-3">Name</th>
                        <th className="text-left p-3">Entry Time</th>
                        <th className="text-left p-3">Exit Time</th>
                        <th className="text-left p-3">Duration</th>
                        <th className="text-left p-3">Status</th>
                    </tr>
                </thead>

                <tbody>
                    {history.length === 0 ? (
                        <tr className="border-b hover:bg-gray-50">
                            <td className="p-3" colSpan="5">
                                No visitor history available
                            </td>
                        </tr>
                    ) : (
                        history.map((record) => (
                            <tr className="border-b hover:bg-gray-50" key={record.visitor_log_id}>
                                <td className="p-3">{record.name}</td>

                                <td className="p-3">
                                    {new Date(
                                        record.entry_time
                                    ).toLocaleString()}
                                </td>

                                <td className="p-3">
                                    {record.exit_time
                                        ? new Date(
                                              record.exit_time
                                          ).toLocaleString()
                                        : "-"}
                                </td>

                                <td className="p-3">{record.duration || "-"}</td>

                                <td className="p-3">{record.status}</td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
}

export default VisitorHistoryTable;