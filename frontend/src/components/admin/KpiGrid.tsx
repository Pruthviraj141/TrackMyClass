import { Users, Calendar, Clock, AlertTriangle, Info } from 'lucide-react'
import { Card } from '@/components/ui/card'

interface KpiData {
  totalStudents: number
  attendancePct: number
  activeSessions: number
  exceptionsCount?: number
}

interface KpiGridProps {
  data: KpiData
  isLoading?: boolean
}

export function KpiGrid({ data, isLoading }: KpiGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-28 bg-muted/50 rounded-[24px] animate-pulse" />
        ))}
      </div>  
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Students */}
      <Card className="p-5 flex flex-col justify-between h-28 border-border/40 shadow-sm bg-card hover:bg-card/80 transition-colors">
        <div className="flex justify-between items-start">
          <span className="text-[13px] font-semibold text-foreground/70">Students</span>
          <Users className="w-4 h-4 text-foreground/40" />
        </div>
        <div>
          <span className="text-3xl font-bold tracking-tight" style={{ fontVariantNumeric: "tabular-nums" }}>
            {data.totalStudents.toLocaleString()}
          </span>
          <p className="text-[11px] text-green-500 font-medium mt-1">
            ↗ active enrolled
          </p>
        </div>
      </Card>

      {/* Today's Attendance */}
      <Card className="p-5 flex flex-col justify-between h-28 border-border/40 shadow-sm bg-card hover:bg-card/80 transition-colors">
        <div className="flex justify-between items-start">
          <span className="text-[13px] font-semibold text-foreground/70">Today's Attendance</span>
          <Calendar className="w-4 h-4 text-foreground/40" />
        </div>
        <div>
          <span className="text-3xl font-bold tracking-tight" style={{ fontVariantNumeric: "tabular-nums" }}>
            {data.attendancePct.toFixed(1)}%
          </span>
          <p className="text-[11px] text-foreground/50 font-medium mt-1">
            avg rate today
          </p>
        </div>
      </Card>

      {/* Active Sessions */}
      <Card className="p-5 flex flex-col justify-between h-28 border-border/40 shadow-sm bg-card hover:bg-card/80 transition-colors">
        <div className="flex justify-between items-start">
          <span className="text-[13px] font-semibold text-foreground/70">Active Sessions</span>
          <Clock className="w-4 h-4 text-foreground/40" />
        </div>
        <div>
          <span className="text-3xl font-bold tracking-tight" style={{ fontVariantNumeric: "tabular-nums" }}>
            {data.activeSessions}
          </span>
          <p className="text-[11px] text-foreground/50 font-medium mt-1 flex items-center gap-1">
            {data.activeSessions > 0 ? "currently live" : "none in progress"} 
            <Info className="w-3 h-3" />
          </p>
        </div>
      </Card>

      {/* Exceptions */}
      <Card className="p-5 flex flex-col justify-between h-28 border-border/40 shadow-sm bg-amber-500/5 hover:bg-amber-500/10 transition-colors border-amber-500/20">
        <div className="flex justify-between items-start">
          <span className="text-[13px] font-semibold text-amber-600 dark:text-amber-500">Attendance Exceptions</span>
          <AlertTriangle className="w-4 h-4 text-amber-500" />
        </div>
        <div>
          <span className="text-3xl font-bold tracking-tight text-amber-600 dark:text-amber-500" style={{ fontVariantNumeric: "tabular-nums" }}>
            {data.exceptionsCount !== undefined ? data.exceptionsCount : "N/A"}
          </span>
          <p className="text-[11px] text-amber-600/70 dark:text-amber-500/80 font-medium mt-1">
            {data.exceptionsCount !== undefined ? "needs attention" : "metrics unavailable"}
          </p>
        </div>
      </Card>
    </div>
  )
}
