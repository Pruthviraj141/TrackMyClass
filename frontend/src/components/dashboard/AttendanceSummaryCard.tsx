import { useState, useEffect } from "react"
import { Calendar } from "lucide-react"

interface OverallStatsProps {
  percentage: number
  present: number
  absent: number
  late: number
}

export function AttendanceSummaryCard({ percentage, present, absent, late }: OverallStatsProps) {
  const [mounted, setMounted] = useState(false)
  const totalClasses = present + absent + late
  
  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 150)
    return () => clearTimeout(timer)
  }, [])

  const radius = 46
  const circumference = 2 * Math.PI * radius
  const dashOffset = mounted ? circumference - ((percentage / 100) * circumference) : circumference

  return (
    <div className="px-5 py-2">
      <div className="bg-card dark:bg-card/40 rounded-[28px] shadow-[0_4px_24px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_24px_rgb(0,0,0,0.1)] border border-transparent dark:border-border/30 overflow-hidden">
        
        <div className="px-5pt-6 pb-2 pt-5">
           <h3 className="text-[17px] font-bold tracking-tight text-foreground px-1 mb-5">Overall Attendance</h3>
           
           <div className="flex justify-center items-center py-2 px-1">
             
             {/* Center: Progress Ring */}
             <div className="relative w-[130px] h-[130px] shrink-0 flex flex-col items-center justify-center">
               <svg className="absolute inset-0 w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
                 <defs>
                   <linearGradient id="dashboardHeroRing" x1="0%" y1="0%" x2="100%" y2="0%">
                     <stop offset="0%" stopColor="#4f46e5" />
                     <stop offset="100%" stopColor="#3b82f6" />
                   </linearGradient>
                 </defs>
                 <circle cx="50" cy="50" r={radius} fill="none" className="stroke-muted/50 dark:stroke-muted/20" strokeWidth="8" />
                 <circle 
                   cx="50" cy="50" r={radius} fill="none" stroke="url(#dashboardHeroRing)" 
                   strokeWidth="8" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={dashOffset}
                   style={{ transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)' }}
                 />
               </svg>
               <div className="z-10 flex flex-col items-center justify-center translate-y-[-2px]">
                 <span className="text-[34px] font-bold tracking-tight text-foreground leading-none" style={{ fontFeatureSettings: '"tnum"' }}>
                   {percentage}%
                 </span>
                 <span className="text-[11px] font-medium text-foreground/50 mt-1.5 flex items-center gap-1">
                   <strong className="text-foreground/70">{present} / {totalClasses}</strong>
                 </span>
                 <span className="text-[9px] font-medium text-foreground/40 mt-0.5 leading-none">classes attended</span>
               </div>
             </div>

           </div>
        </div>

        {/* Legend */}
        <div className="flex items-center justify-between px-6 pt-5 pb-4">
          <div className="flex flex-col items-center">
            <div className="flex items-center gap-1.5 mb-1.5">
              <div className="w-[7px] h-[7px] rounded-full bg-green-500" />
              <span className="text-[11px] font-semibold text-foreground/50 uppercase tracking-wide">Present</span>
            </div>
            <span className="text-[20px] font-bold text-foreground leading-none">{present}</span>
          </div>

          <div className="flex flex-col items-center">
            <div className="flex items-center gap-1.5 mb-1.5">
              <div className="w-[7px] h-[7px] rounded-full bg-destructive" />
              <span className="text-[11px] font-semibold text-foreground/50 uppercase tracking-wide">Absent</span>
            </div>
            <span className="text-[20px] font-bold text-foreground leading-none">{absent}</span>
          </div>

          <div className="flex flex-col items-center">
            <div className="flex items-center gap-1.5 mb-1.5">
              <div className="w-[7px] h-[7px] rounded-full bg-amber-500" />
              <span className="text-[11px] font-semibold text-foreground/50 uppercase tracking-wide">Late</span>
            </div>
            <span className="text-[20px] font-bold text-foreground leading-none">{late}</span>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-border/40 py-3 flex items-center justify-center bg-card/30 dark:bg-card/10">
          <Calendar className="w-3.5 h-3.5 text-foreground/40 mr-1.5" />
          <span className="text-[12px] font-semibold text-foreground/50">{totalClasses} Total Classes</span>
        </div>
      </div>
    </div>
  )
}

export function AttendanceSummarySkeleton() {
  return (
    <div className="px-5 py-2">
      <div className="bg-card dark:bg-card/40 rounded-[28px] h-[260px] animate-pulse border border-transparent dark:border-border/30">
        <div className="w-full h-full bg-muted/40 rounded-[28px]" />
      </div>
    </div>
  )
}
