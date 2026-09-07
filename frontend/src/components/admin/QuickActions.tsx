import { Card } from "@/components/ui/card"
import { PlusCircle, Play, FileText, BarChart3 } from "lucide-react"

interface QuickActionsProps {
  onAddStudent: () => void
  onStartSession: () => void
  onViewReports: () => void
  onAnalytics: () => void
  isStartingSession?: boolean
}

export function QuickActions({
  onAddStudent,
  onStartSession,
  onViewReports,
  onAnalytics,
  isStartingSession
}: QuickActionsProps) {

  const btnClass = "flex items-center gap-2 px-4 py-2.5 bg-background border border-border/50 hover:bg-muted/80 rounded-[14px] text-[13px] font-semibold transition-all shadow-sm active:scale-95 disabled:opacity-50 disabled:pointer-events-none"

  return (
    <Card className="p-5 shadow-sm bg-card border-border/40 flex flex-col gap-4">
      <h3 className="font-semibold text-[15px] leading-tight">Quick Actions</h3>
      <div className="flex flex-wrap items-center gap-2">
        <button className={btnClass} onClick={onAddStudent}>
          <PlusCircle className="w-4 h-4" /> Add student
        </button>
        <button className={btnClass} onClick={onStartSession} disabled={isStartingSession}>
          <Play className="w-4 h-4" /> Start session
        </button>
        <button className={btnClass} onClick={onViewReports}>
          <FileText className="w-4 h-4" /> View reports
        </button>
        <button className={btnClass} onClick={onAnalytics}>
          <BarChart3 className="w-4 h-4" /> Generate report
        </button>
      </div>
    </Card>
  )
}
