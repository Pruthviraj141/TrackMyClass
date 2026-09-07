import { CheckCircle2, ChevronRight, Users } from "lucide-react"

interface Props {
  subject: string
  presentCount: number
  totalCount: number
  onFinalize: () => void
  isFinalizing: boolean
}

export function AttendanceReviewScreen({ subject, presentCount, totalCount, onFinalize, isFinalizing }: Props) {
  return (
    <div className="flex flex-col items-center justify-center p-6 md:p-12 w-full max-w-lg mx-auto bg-background/50 h-full animate-in fade-in duration-500">
      <div className="w-20 h-20 bg-blue-100 dark:bg-blue-900/40 rounded-full flex items-center justify-center mb-6">
        <CheckCircle2 className="w-10 h-10 text-blue-600 dark:text-blue-400" />
      </div>
      
      <h2 className="text-3xl font-bold tracking-tight text-foreground mb-3 text-center">Scan Completed</h2>
      <p className="text-slate-500 dark:text-slate-400 text-center mb-8 text-[15px]">
        Review the captured attendance for <span className="font-semibold text-foreground">{subject}</span> before finalizing the session.
      </p>

      <div className="w-full bg-card border border-border/40 rounded-3xl p-6 mb-8 shadow-sm">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <Users className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-[15px] font-medium text-foreground">Students Present</p>
              <p className="text-sm text-muted-foreground">{presentCount} detected & recorded</p>
            </div>
          </div>
          <span className="text-2xl font-bold text-foreground">{presentCount}</span>
        </div>

        <div className="h-[1px] bg-border/40 w-full mb-5" />
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <Users className="w-6 h-6 text-slate-600 dark:text-slate-400" />
            </div>
            <div>
              <p className="text-[15px] font-medium text-foreground">Not Seen</p>
              {totalCount > 0 ? (
                 <p className="text-sm text-muted-foreground">{Math.max(0, totalCount - presentCount)} missing</p>
              ) : (
                 <p className="text-sm text-muted-foreground">Unknown total</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <button
        onClick={onFinalize}
        disabled={isFinalizing}
        className="w-full bg-primary hover:bg-primary/95 text-primary-foreground font-semibold py-4 rounded-xl transition-all disabled:opacity-50 flex justify-center items-center gap-2 shadow-lg shadow-primary/20 text-[16px]"
      >
        {isFinalizing ? "Finalizing Session..." : "Finalize Attendance"}
        {!isFinalizing && <ChevronRight className="w-5 h-5" />}
      </button>
      <p className="text-xs text-center text-muted-foreground mt-6 font-medium tracking-wide">
        YOU CAN MAKE MANUAL CORRECTIONS FROM THE DASHBOARD AFTER FINALIZING.
      </p>
    </div>
  )
}
