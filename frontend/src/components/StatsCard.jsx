function StatsCard({
    title,
    value,
    icon: Icon,
}) {
    return (
        <div className="bg-white rounded-2xl shadow-md p-6 flex justify-between items-center">

            <div>

                <p className="text-gray-500 text-sm">
                    {title}
                </p>

                <h2 className="text-3xl font-bold mt-2">
                    {value}
                </h2>

            </div>

            <div className="bg-blue-100 p-4 rounded-full">

                <Icon
                    className="text-blue-600"
                    size={30}
                />

            </div>

        </div>
    );
}

export default StatsCard;