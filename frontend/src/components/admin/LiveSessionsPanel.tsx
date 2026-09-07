import { useNavigate } from "react-router-dom"
import { Card } from "@/components/ui/card"

interface LiveSession {
  id: string
  course: string
  section: string
  teacher: string
  present: number
  total: number
  percentage: number
  startTime: string
  isLive: boolean
}

interface LiveSessionsPanelProps {
  sessions: LiveSession[]
  isLoading?: boolean
}

export function LiveSessionsPanel({ sessions, isLoading }: LiveSessionsPanelProps) {
  const navigate = useNavigate()

  if (isLoading) {
    return (
      <Card className="p-5 border-border/40 shadow-sm bg-card animate-pulse">
        <div className="h-6 w-32 bg-muted/50 rounded mb-4" />
        <div className="space-y-3">
          <div className="h-10 bg-muted/30 rounded" />
          <div className="h-10 bg-muted/30 rounded" />
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-5 border-border/40 shadow-sm bg-card flex flex-col gap-4">
      <div>
        <h3 className="font-semibold text-[15px] leading-tight">Live Sessions</h3>
        <p className="text-[13px] text-foreground/50">Classes currently in progress or recently ended</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-[13px] whitespace-nowrap">
          <thead>
            <tr className="border-b border-border/40 text-foreground/50">
              <th className="pb-2 font-medium pr-4">Course</th>
              <th className="pb-2 font-medium pr-4">Section</th>
              <th className="pb-2 font-medium pr-4">Teacher</th>
              <th className="pb-2 font-medium pr-4 text-center">Attendance</th>
              <th className="pb-2 font-medium pr-4 text-right">Percentage</th>
              <th className="pb-2 font-medium pr-4 text-center">Session State</th>
              <th className="pb-2 font-medium pr-4 text-right">Time</th>
              <th className="pb-2 font-medium pl-2"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/20">
            {sessions.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-foreground/40 italic">
                  No classes are currently in progress.
                </td>
              </tr>
            ) : (
              sessions.map(s => (
                <tr key={s.id} className="group hover:bg-muted/30 transition-colors">
                  <td className="py-3 pr-4 font-medium">{s.course}</td>
                  <td className="py-3 pr-4 text-foreground/70">{s.section}</td>
                  <td className="py-3 pr-4 text-foreground/70">{s.teacher}</td>
                  <td className="py-3 pr-4 text-center max-w-[120px]">
                    <div className="flex flex-col items-center gap-1">
                      <span className="font-semibold text-foreground/80">{s.present} / {s.total} present</span>
                      <div className="h-0.5 w-full bg-muted/50 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary rounded-full transition-all" 
                          style={{ width: `${Math.min(s.percentage, 100)}%` }} 
                        />
                      </div>
                    </div>
                  </td>
                  <td className="py-3 pr-4 text-right font-mono" style={{ fontVariantNumeric: "tabular-nums" }}>
                    {s.percentage.toFixed(1)}%
                  </td>
                  <td className="py-3 pr-4 text-center">
                    {s.isLive ? (
                      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-green-500/10 text-green-600 dark:text-green-400 rounded-full text-[11px] font-bold uppercase tracking-wider border border-green-500/20">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                        Live
                      </div>
                    ) : (
                      <div className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-muted text-foreground/50 rounded-full text-[11px] font-bold uppercase tracking-wider border border-border/40">
                        Ended
                      </div>
                    )}
                  </td>
                  <td className="py-3 pr-4 text-right font-mono text-foreground/60">{s.startTime}</td>
                  <td className="py-3 pl-2 text-right">
                    <button 
                      onClick={() => navigate(s.isLive ? `sessions/active/monitor` : `reports`)}
                      className="px-3 py-1 bg-background border border-border/50 hover:bg-muted/80 rounded-[6px] text-[12px] font-medium transition-colors"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
