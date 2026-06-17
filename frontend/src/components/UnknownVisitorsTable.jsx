import { useEffect, useState } from "react";

function UnknownVisitorsTable() {

    const [visitors, setVisitors] = useState([]);

    const reviewVisitor = async (id) => {

        try {

            await fetch(
                `http://127.0.0.1:8000/unknown-visitors/${id}/review`,
                {
                    method: "PUT",
                }
            );

            setVisitors((prev) =>
                prev.map((visitor) =>
                    visitor.id === id
                        ? {
                              ...visitor,
                              reviewed: true,
                          }
                        : visitor
                )
            );

        } catch (error) {

            console.error(error);

        }
    };

    useEffect(() => {

        fetch(
            "http://127.0.0.1:8000/unknown-visitors"
        )
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

            <h2>Unknown Visitors</h2>

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
                        <th className="text-left p-3">ID</th>
                        <th className="text-left p-3">Image</th>
                        <th className="text-left p-3">Detected At</th>
                        <th className="text-left p-3">Reviewed</th>
                    </tr>

                </thead>

                <tbody>

                    {visitors.length === 0 ? (

                        <tr className="border-b hover:bg-gray-50">

                            <td className="p-3" colSpan="4">
                                No unknown visitors found
                            </td>

                        </tr>

                    ) : (

                        visitors.map((visitor) => (

                            <tr className="border-b hover:bg-gray-50" key={visitor.id}>

                                <td className="p-3">{visitor.id}</td>

                                <td className="p-3">
                                <img src={`http://127.0.0.1:8000/${visitor.image_path.replace(/\\/g, "/")}`}alt="Unknown Visitor" width="100"/>
                                </td>

                                <td className="p-3">
                                    {new Date(
                                        visitor.detected_at
                                    ).toLocaleString()}
                                </td>

                                <td className="p-3">

                                {visitor.reviewed ? (

                                    "Yes"

                                ) : (

                                    <button
                                        onClick={() =>
                                            reviewVisitor(visitor.id)
                                        }
                                    >
                                        Mark Reviewed
                                    </button>

                                )}

                            </td>

                            </tr>

                        ))

                    )}

                </tbody>

            </table>

        </div>

    );
}

export default UnknownVisitorsTable;