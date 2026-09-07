import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts"
import { XCircle, Clock } from "lucide-react"

interface AttendanceSummaryProps {
  stats: {
    total: number
    present: number
    absent: number
    percentage: number
  }
}

export function AttendanceSummary({ stats }: AttendanceSummaryProps) {
  const chartData = [
    { name: "Present", value: stats.present, color: "hsl(var(--primary))" },
    { name: "Absent", value: stats.absent, color: "hsl(var(--destructive))" },
  ]

  const lateCount = (stats as any).late || 0

  return (
    <div className="flex flex-col gap-4 px-1">
      {/* 2x2 Grid for Stats -> Removed Registered and Present, ONLY Absent & Late as per design */}
      <div className="grid grid-cols-2 gap-3">
        {/* Absent */}
        <div className="bg-rose-50 dark:bg-rose-950/30 rounded-[20px] p-4 flex flex-col justify-between aspect-[1.3/1]">
          <div className="flex items-start justify-between">
            <span className="text-rose-600 dark:text-rose-400 font-bold text-[15px]">Absent</span>
            <div className="bg-rose-100 dark:bg-rose-900/40 p-1.5 rounded-full text-rose-600 dark:text-rose-400">
              <XCircle className="w-4 h-4" strokeWidth={2.5} />
            </div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-rose-700 dark:text-rose-300 mt-2">{stats.absent}</h3>
        </div>

        {/* Late */}
        <div className="bg-[#FFFAEB] dark:bg-amber-950/30 rounded-[20px] p-4 flex flex-col justify-between aspect-[1.3/1]">
          <div className="flex items-start justify-between">
            <span className="text-amber-600 dark:text-amber-400 font-bold text-[15px]">Late</span>
            <div className="bg-amber-100 dark:bg-amber-900/40 p-1.5 rounded-full text-amber-600 dark:text-amber-400">
              <Clock className="w-4 h-4" strokeWidth={2.5} />
            </div>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-amber-700 dark:text-amber-300 mt-2">{lateCount}</h3>
        </div>
      </div>

      {/* Attendance Rate Chart Card */}
      <div className="bg-card border border-border/40 rounded-[24px] p-5 flex items-center justify-between shadow-sm">
        <div className="flex flex-col gap-1">
          <span className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Attendance Rate</span>
          <div className="flex items-baseline gap-1 mt-1">
            <h3 className="text-[42px] font-bold tracking-tighter tabular-nums leading-none">
              {stats.percentage}
            </h3>
            <span className="text-xl font-bold text-muted-foreground">%</span>
          </div>
          <div className="flex items-center gap-3 mt-3">
             <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
               <div className="w-2.5 h-2.5 rounded-full bg-primary" /> Present
             </div>
             <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
               <div className="w-2.5 h-2.5 rounded-full bg-destructive" /> Absent
             </div>
          </div>
        </div>

        <div className="w-[100px] h-[100px] shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={36}
                outerRadius={50}
                paddingAngle={4}
                dataKey="value"
                stroke="none"
                cornerRadius={4}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                 contentStyle={{ borderRadius: '12px', border: '1px solid hsl(var(--border))', boxShadow: '0 4px 14px rgba(0,0,0,0.05)', backgroundColor: 'hsl(var(--card))' }}
                 itemStyle={{ color: 'hsl(var(--foreground))', fontWeight: 'bold' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
