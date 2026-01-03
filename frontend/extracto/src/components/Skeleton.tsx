export default function Skeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="h-28 rounded-xl bg-white/10 animate-pulse" />
      ))}
    </div>
  );
}
