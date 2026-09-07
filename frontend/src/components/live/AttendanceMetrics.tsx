interface AttendanceMetricsProps {
  present: number
  unknown: number
  total: number
}

export function AttendanceMetrics({ present, unknown, total }: AttendanceMetricsProps) {
  const percentage = total > 0 ? (present / total) * 100 : 0
  const rateStr = total > 0 ? percentage.toFixed(1) : "0.0"

  // Gradient width clamp
  const safeWidth = Math.min(Math.max(percentage, 5), 100)

  return (
    <div className="px-5 py-4 w-full">
      <div className="flex items-center justify-between px-2 mb-4">
        {/* Present Block */}
        <div className="flex flex-col items-center flex-1">
          <span className="text-4xl font-bold tracking-tight text-foreground" style={{ fontVariantNumeric: "tabular-nums" }}>
            {present}
          </span>
          <span className="text-[10px] font-bold tracking-widest uppercase text-green-500 mt-1">Present</span>
        </div>

        {/* Divider */}
        <div className="w-[1px] h-10 bg-border/40" />

        {/* Unknown Block */}
        <div className="flex flex-col items-center flex-1">
          <span className="text-4xl font-bold tracking-tight text-amber-500" style={{ fontVariantNumeric: "tabular-nums" }}>
            {unknown}
          </span>
          <span className="text-[10px] font-bold tracking-widest uppercase text-foreground/50 mt-1">Unknown</span>
        </div>

        {/* Divider */}
        <div className="w-[1px] h-10 bg-border/40" />

        {/* Total Block */}
        <div className="flex flex-col items-center flex-1 opacity-60">
          <span className="text-4xl font-bold tracking-tight text-foreground" style={{ fontVariantNumeric: "tabular-nums" }}>
            {total}
          </span>
          <span className="text-[10px] font-bold tracking-widest uppercase text-foreground/50 mt-1">Total</span>
        </div>
      </div>

      {/* Progress Bar Container */}
      <div className="px-2">
        <div className="h-1 w-full bg-muted overflow-hidden rounded-full relative">
          <div 
            className="absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r from-blue-600 via-indigo-500 to-green-400"
            style={{ width: `${safeWidth}%` }}
          />
        </div>
        <div className="text-right mt-2">
          <span className="text-[10px] uppercase font-semibold text-foreground/40 tracking-wider">
            {rateStr}% attendance rate
          </span>
        </div>
      </div>
    </div>
  )
}
