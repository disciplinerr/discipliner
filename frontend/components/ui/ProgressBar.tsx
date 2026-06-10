export default function ProgressBar({
  value,
  total,
  className = "",
}: {
  value: number;
  total: number;
  className?: string;
}) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div className={`h-1.5 w-full overflow-hidden rounded-full bg-elevated ${className}`}>
      <div
        className="h-full origin-left animate-grow rounded-full bg-foreground transition-all duration-500"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
