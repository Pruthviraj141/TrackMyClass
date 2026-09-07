import { CheckCircle2, Clock, XCircle } from "lucide-react"

export interface ClassSession {
  id: string
  subject_name: string
  time: string
  status: "Present" | "Absent" | "Late" | "Upcoming" | "Not Started" | "Cancelled"
}

export function TodaySection({ classes, isLoading }: { classes: ClassSession[], isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="px-5 py-3">
        <div className="flex items-center justify-between px-2 mb-4">
          <h3 className="text-[17px] font-bold tracking-tight text-foreground flex items-center gap-2">
            Today's Classes <span className="w-5 h-5 rounded-full bg-muted flex items-center justify-center text-[10px] font-bold">-</span>
          </h3>
          <span className="text-[13px] font-medium text-primary cursor-pointer hover:underline">View All</span>
        </div>
        <div className="space-y-3">
          <div className="h-[80px] bg-muted/30 rounded-2xl animate-pulse"></div>
          <div className="h-[80px] bg-muted/30 rounded-2xl animate-pulse"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-5 py-3">
      <div className="flex items-center justify-between px-2 mb-4">
        <h3 className="text-[17px] font-bold tracking-tight text-foreground flex items-center gap-2">
          Today's Classes 
          <span className="min-w-5 h-5 px-1.5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[11px] font-bold">
            {classes.length}
          </span>
        </h3>
        <span className="text-[13px] font-medium text-foreground/40 hover:text-primary transition-colors cursor-pointer">View All</span>
      </div>
      
      {classes.length === 0 ? (
        <div className="bg-transparent border border-dashed border-border/60 rounded-[24px] p-6 text-center">
          <p className="text-[14px] font-medium text-foreground/40">No classes today</p>
        </div>
      ) : (
        <div className="space-y-3">
          {classes.map((c) => (
            <div key={c.id} className="bg-card dark:bg-card/40 border border-transparent dark:border-border/30 rounded-[24px] p-4 flex items-center gap-4 shadow-[0_4px_24px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_24px_rgb(0,0,0,0.1)]">
              
              <div className="shrink-0">
                {c.status === "Present" && (
                  <div className="w-[42px] h-[42px] rounded-[14px] bg-green-500/10 text-green-600 dark:bg-green-500/20 dark:text-green-500 flex items-center justify-center">
                    <CheckCircle2 className="w-[20px] h-[20px] stroke-[2.5]" /> 
                  </div>
                )}
                {c.status === "Absent" && (
                  <div className="w-[42px] h-[42px] rounded-[14px] bg-destructive/10 text-destructive flex items-center justify-center">
                    <XCircle className="w-[20px] h-[20px] stroke-[2.5]" /> 
                  </div>
                )}
                {c.status === "Late" && (
                  <div className="w-[42px] h-[42px] rounded-[14px] bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-500 flex items-center justify-center">
                    <Clock className="w-[20px] h-[20px] stroke-[2.5]" /> 
                  </div>
                )}
              </div>
              
              <div className="flex flex-col flex-1">
                <h4 className="font-bold text-[16px] tracking-tight leading-none mb-1.5 text-foreground">{c.subject_name}</h4>
                <div className="flex items-center text-[12px] font-medium text-foreground/50">
                   <Clock className="w-3.5 h-3.5 mr-1.5 opacity-70" />
                   {c.time}
                </div>
              </div>

              <div className="shrink-0 pl-2">
                {c.status === "Present" && (
                  <span className="bg-green-500/10 text-green-700 dark:text-green-500 px-3 py-1.5 rounded-full text-[11px] font-bold tracking-wide">
                    Present
                  </span>
                )}
                {c.status === "Absent" && (
                  <span className="bg-destructive/10 text-destructive px-3 py-1.5 rounded-full text-[11px] font-bold tracking-wide">
                    Absent
                  </span>
                )}
                {c.status === "Late" && (
                  <span className="bg-amber-500/10 text-amber-700 dark:text-amber-500 px-3 py-1.5 rounded-full text-[11px] font-bold tracking-wide">
                    Late
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
