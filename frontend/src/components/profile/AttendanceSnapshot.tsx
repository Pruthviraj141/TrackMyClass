import { CheckCircle2, XCircle, Clock } from "lucide-react"
import { useNavigate } from "react-router-dom"

interface AttendanceSnapshotProps {
  percentage: number
  present: number
  absent: number
  late: number
  isLoading?: boolean
}

export function AttendanceSnapshot({ 
  percentage, 
  present, 
  absent, 
  late,
  isLoading
}: AttendanceSnapshotProps) {
  const navigate = useNavigate()

  if (isLoading) {
    return (
      <div className="px-5 py-2">
        <div className="bg-card rounded-[20px] shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none p-4 h-[120px] animate-pulse">
          <div className="h-full w-full bg-muted/20 rounded-lg"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-5 py-2">
      <button 
        onClick={() => navigate("/student/attendance")}
        className="w-full text-left bg-card rounded-[20px] shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none p-5 flex items-center justify-between transition-transform active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-primary/20"
      >
        <div className="flex flex-col">
          <span className="text-[17px] font-semibold text-foreground mb-1">Attendance</span>
          <span className="text-4xl font-bold tracking-tight text-primary">{percentage}%</span>
          <span className="text-[12px] text-foreground/60 font-medium mt-1">Overall attendance</span>
        </div>
        
        <div className="flex flex-col items-end gap-3">
          <div className="flex items-center gap-4">
             <div className="flex flex-col items-center">
               <span className="text-green-500 flex items-center justify-center w-5 h-5 rounded-full bg-green-500/10 mb-1">
                 <CheckCircle2 className="w-3.5 h-3.5" />
               </span>
               <span className="text-[11px] font-semibold text-foreground/70 mb-0.5">Present</span>
               <span className="text-sm font-bold">{present}</span>
             </div>
             <div className="flex flex-col items-center">
               <span className="text-destructive flex items-center justify-center w-5 h-5 rounded-full bg-destructive/10 mb-1">
                 <XCircle className="w-3.5 h-3.5" />
               </span>
               <span className="text-[11px] font-semibold text-foreground/70 mb-0.5">Absent</span>
               <span className="text-sm font-bold">{absent}</span>
             </div>
             <div className="flex flex-col items-center">
               <span className="text-amber-500 flex items-center justify-center w-5 h-5 rounded-full bg-amber-500/10 mb-1">
                 <Clock className="w-3.5 h-3.5" />
               </span>
               <span className="text-[11px] font-semibold text-foreground/70 mb-0.5">Late</span>
               <span className="text-sm font-bold">{late}</span>
             </div>
          </div>
          <p className="text-[11px] font-medium text-foreground/60 flex items-center gap-1.5 mt-1">
          </p>
        </div>
      </button>
    </div>
  )
}
