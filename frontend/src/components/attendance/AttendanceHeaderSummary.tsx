import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { CheckCircle2, XCircle, Clock } from "lucide-react"

interface AttendanceSummaryProps {
  percentage: number
  present: number
  absent: number
  late: number
  label?: string
}

export function AttendanceHeaderSummary({ percentage, present, absent, late, label = "Overall attendance" }: AttendanceSummaryProps) {
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 200)
    return () => clearTimeout(timer)
  }, [])

  const radius = 40
  const circumference = 2 * Math.PI * radius
  const dashOffset = mounted ? circumference - ((percentage / 100) * circumference) : circumference

  return (
    <div className="px-5 py-3">
      <Card className="rounded-[28px] border-none shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)] bg-card overflow-hidden">
        
        {/* Top Row: Dial */}
        <div className="flex flex-row items-center justify-center px-6 pt-6 pb-2">
          
          {/* Progress Ring */}
          <div className="relative w-[120px] h-[120px] flex items-center justify-center">
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
              <defs>
                <linearGradient id="attendanceGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#4f46e5" />
                  <stop offset="100%" stopColor="#818cf8" />
                </linearGradient>
              </defs>
              <circle 
                cx="50" cy="50" r={radius} 
                fill="none" 
                className="stroke-muted/40" 
                strokeWidth="10" 
              />
              <circle 
                cx="50" cy="50" r={radius} 
                fill="none" 
                stroke="url(#attendanceGradient)" 
                strokeWidth="10" 
                strokeLinecap="round" 
                strokeDasharray={circumference} 
                strokeDashoffset={dashOffset}
                style={{ transition: 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-[28px] font-bold tracking-tight text-foreground leading-none" style={{ fontFeatureSettings: '"tnum"' }}>
                {percentage}%
              </span>
              <span className="text-[9px] text-foreground/50 font-medium tracking-wide mt-1 leading-none uppercase max-w-[60px] text-center">
                {label === "Overall attendance" ? "Overall" : label}
              </span>
            </div>
          </div>

        </div>

        {/* Bottom Row: Stats Columns */}
        <div className="flex items-center justify-between px-6 pb-6 pt-4">
          
          {/* Present */}
          <div className="flex flex-col items-start w-1/3">
            <div className="flex items-center gap-1.5 mb-1.5">
              <CheckCircle2 className="w-[14px] h-[14px] text-green-500 fill-green-500/20" /> 
              <span className="text-[11px] font-semibold text-foreground/60 uppercase tracking-wide">Present</span>
            </div>
            <div className="flex flex-col items-start px-0.5">
              <span className="text-[26px] font-bold tracking-tight leading-none text-foreground">{present}</span>
              <span className="text-[11px] text-foreground/40 font-medium mt-1">classes</span>
            </div>
          </div>

          {/* Absent */}
          <div className="flex flex-col items-center w-1/3">
            <div className="flex items-center gap-1.5 mb-1.5">
              <XCircle className="w-[14px] h-[14px] text-destructive fill-destructive/20" /> 
              <span className="text-[11px] font-semibold text-foreground/60 uppercase tracking-wide">Absent</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-[26px] font-bold tracking-tight leading-none text-foreground">{absent}</span>
              <span className="text-[11px] text-foreground/40 font-medium mt-1">classes</span>
            </div>
          </div>

          {/* Late */}
          <div className="flex flex-col items-end w-1/3">
            <div className="flex items-center gap-1.5 mb-1.5">
              <Clock className="w-[14px] h-[14px] text-amber-500 fill-amber-500/20" /> 
              <span className="text-[11px] font-semibold text-foreground/60 uppercase tracking-wide">Late</span>
            </div>
            <div className="flex flex-col items-end px-0.5">
              <span className="text-[26px] font-bold tracking-tight leading-none text-foreground">{late}</span>
              <span className="text-[11px] text-foreground/40 font-medium mt-1">classes</span>
            </div>
          </div>

        </div>

      </Card>
    </div>
  )
}
