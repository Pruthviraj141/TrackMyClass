import { CheckCircle2, AlertTriangle } from "lucide-react"

export interface RecognitionEvent {
  id: string
  name: string
  status: "verified" | "unknown"
  timestamp: string // HH:mm:ss
  rollNumber?: string
}

interface RecentEventsProps {
  events: RecognitionEvent[]
  isProcessing?: boolean
}

export function RecentEvents({ events, isProcessing = true }: RecentEventsProps) {
  return (
    <div className="px-5 py-4 w-full flex-1 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <span className="text-[11px] font-bold tracking-widest uppercase text-foreground/40">Recent</span>
        {isProcessing && (
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            <span className="text-[10px] font-bold tracking-widest uppercase text-green-500">Processing</span>
          </div>
        )}
      </div>

      <div className="space-y-4">
        {events.length === 0 ? (
          <div className="text-center py-6 text-foreground/40 text-[13px]">
            No activity yet
          </div>
        ) : (
          events.map((event) => (
            <div key={event.id} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {event.status === "verified" ? (
                  <div className="w-8 h-8 rounded-full bg-green-500/10 flex items-center justify-center border border-green-500/20">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-amber-500/10 flex items-center justify-center border border-amber-500/20">
                    <AlertTriangle className="w-4 h-4 text-amber-500" />
                  </div>
                )}
                
                <div className="flex flex-col">
                  <div className="flex items-center gap-1.5">
                    <span className={`text-[14px] font-semibold ${event.status === "unknown" ? "text-amber-500" : "text-foreground"}`}>
                      {event.name}
                    </span>
                    {event.status === "verified" && (
                      <span className="text-[12px] font-medium text-green-500/80">Present</span>
                    )}
                  </div>
                  {event.status === "unknown" ? (
                    <span className="text-[12px] text-amber-500/80">Not registered</span>
                  ) : (
                    <span className="text-[12px] text-foreground/60">Roll No. {event.rollNumber || "N/A"}</span>
                  )}
                </div>
              </div>
              
              <span className="text-[12px] font-mono text-foreground/30">
                {event.timestamp}
              </span>
            </div>
          ))
        )}
        
        {/* Fade Out Gradient at bottom list */}
        {events.length > 0 && (
           <div className="h-10 w-full bg-gradient-to-t from-background to-transparent pointer-events-none sticky bottom-0" />
        )}
      </div>
    </div>
  )
}
