export default function StatsCard({
  title,
  value,
  icon: Icon,
}) {
  return (
    <div className="bg-white rounded-2xl shadow-sm p-6 hover:shadow-lg transition">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-slate-500 text-sm">
            {title}
          </p>

          <h2 className="text-3xl font-bold mt-2">
            {value}
          </h2>
        </div>

        <div className="bg-indigo-100 p-3 rounded-xl">
          <Icon size={28} />
        </div>
      </div>
    </div>
  );
}