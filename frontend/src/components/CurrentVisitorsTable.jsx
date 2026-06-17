import { useEffect, useState } from "react";

function CurrentVisitorsTable() {
    const [visitors, setVisitors] = useState([]);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/visitor/inside")
            .then((res) => res.json())
            .then((data) => {
                setVisitors(data);
            })
            .catch((err) => {
                console.error(err);
            });
    }, []);

    return (
        <div style={{ marginTop: "40px" }}>
            <h2>Current Visitors</h2>

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
                    </tr>
                </thead>

                <tbody>
                    {visitors.length === 0 ? (
                        <tr className="border-b hover:bg-gray-50">
                            <td className="p-3" colSpan="2">
                                No visitors inside
                            </td>
                        </tr>
                    ) : (
                        visitors.map((visitor) => (
                            <tr className="border-b hover:bg-gray-50"
                                key={visitor.visitor_log_id}
                            >
                                <td className="p-3">{visitor.name}</td>

                                <td className="p-3">
                                    {new Date(
                                        visitor.entry_time
                                    ).toLocaleString()}
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
}

export default CurrentVisitorsTable;