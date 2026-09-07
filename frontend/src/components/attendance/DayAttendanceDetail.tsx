import { CheckCircle2, Clock, XCircle } from "lucide-react"

export interface DayClassSession {
  id: string
  subject_name: string
  time: string
  status: "Present" | "Absent" | "Late" | "Upcoming" | "Not Started" | "Cancelled"
  attendance_time?: string
}

export function DayAttendanceDetail({ selectedDate, classes, isLoading }: { selectedDate: Date, classes: DayClassSession[], isLoading: boolean }) {
  // Format date to "Tue, Sep 1, 2026"
  const dateStr = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }).format(selectedDate)
  
  return (
    <div className="px-5 py-2">
      
      <div className="flex items-center justify-between px-2 mb-4">
        <h3 className="text-[17px] font-bold tracking-tight text-foreground">Selected Day</h3>
        <span className="text-[14px] font-medium text-foreground/50">{dateStr}</span>
      </div>
      
      {isLoading ? (
        <div className="space-y-3">
          <div className="h-20 bg-muted/30 rounded-2xl animate-pulse"></div>
        </div>
      ) : classes.length === 0 ? (
        <div className="bg-transparent border border-dashed border-border/60 rounded-[24px] p-6 text-center">
          <p className="text-[14px] font-medium text-foreground/40">No classes on this day</p>
        </div>
      ) : (
        <div className="space-y-3">
          {classes.map(c => (
            <div key={c.id} className="bg-card dark:bg-card/40 border border-transparent dark:border-border/30 shadow-[0_4px_24px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_24px_rgb(0,0,0,0.1)] rounded-[28px] p-5 flex items-center gap-4">
              
              <div className="shrink-0">
                {c.status === "Present" && (
                  <div className="w-[42px] h-[42px] rounded-full bg-green-500/20 text-green-600 dark:bg-green-500 dark:text-white flex items-center justify-center">
                    <CheckCircle2 className="w-[22px] h-[22px] fill-current" /> 
                  </div>
                )}
                {c.status === "Absent" && (
                  <div className="w-[42px] h-[42px] rounded-full bg-destructive/10 text-destructive dark:bg-destructive dark:text-white flex items-center justify-center">
                    <XCircle className="w-[22px] h-[22px] fill-current" /> 
                  </div>
                )}
                {c.status === "Late" && (
                  <div className="w-[42px] h-[42px] rounded-full bg-amber-500/10 text-amber-600 dark:bg-amber-500 dark:text-white flex items-center justify-center">
                    <Clock className="w-[22px] h-[22px] fill-current" /> 
                  </div>
                )}
              </div>
              
              <div className="flex flex-col flex-1">
                <h4 className="font-bold text-[17px] tracking-tight leading-none mb-1.5 text-foreground">{c.status}</h4>
                <p className="text-[13px] text-foreground/50 font-medium leading-none mb-2">{c.subject_name}</p>
                {c.time && (
                  <div className="flex items-center text-[12px] font-medium text-foreground/40">
                     <Clock className="w-3.5 h-3.5 mr-1.5 opacity-70" />
                     {c.time}
                  </div>
                )}
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  )
}
