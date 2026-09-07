import { Card } from "@/components/ui/card"
import { Check, AlertTriangle, PlayCircle } from "lucide-react"

export interface ActivityEvent {
  id: string
  type: "session_start" | "session_end" | "recognition" | "anomaly"
  message: string
  time: string
}

interface RecentActivityProps {
  events: ActivityEvent[]
  isLoading?: boolean
}

export function RecentActivity({ events, isLoading }: RecentActivityProps) {
  if (isLoading) {
    return (
      <Card className="p-5 border-border/40 shadow-sm bg-card h-full animate-pulse">
         <div className="h-4 w-32 bg-muted/50 rounded mb-6" />
         <div className="space-y-4">
           {[1, 2, 3, 4].map(i => <div key={i} className="h-4 w-full bg-muted/30 rounded" />)}
         </div>
      </Card>
    )
  }

  return (
    <Card className="p-5 border-border/40 shadow-sm bg-card h-full flex flex-col gap-4">
      <div>
        <h3 className="font-semibold text-[15px] leading-tight">Recent Activity</h3>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {events.length === 0 ? (
          <div className="text-[13px] text-foreground/40 italic py-4">No recent activity.</div>
        ) : (
          <div className="space-y-4">
            {events.map(event => {
              let Icon = Check
              let colorText = "text-green-500"
              
              if (event.type === "anomaly") {
                Icon = AlertTriangle
                colorText = "text-amber-500"
              } else if (event.type === "session_start") {
                Icon = PlayCircle
                colorText = "text-primary"
              }
              
              return (
                <div key={event.id} className="flex items-start justify-between gap-3 text-[13px]">
                  <div className="flex items-start gap-2.5">
                    <Icon className={`w-4 h-4 mt-0.5 ${colorText}`} />
                    <span className="text-foreground/80 font-medium">{event.message}</span>
                  </div>
                  <span className="text-foreground/40 font-mono text-[11px] whitespace-nowrap">{event.time}</span>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </Card>
  )
}
