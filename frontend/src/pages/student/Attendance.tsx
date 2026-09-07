import { useState, useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { AttendanceHeader } from "@/components/attendance/AttendanceHeader"
import { AttendanceHeaderSummary } from "@/components/attendance/AttendanceHeaderSummary"
import { AttendanceCalendar } from "@/components/attendance/AttendanceCalendar"
import { DayAttendanceDetail } from "@/components/attendance/DayAttendanceDetail"
import type { DayClassSession } from "@/components/attendance/DayAttendanceDetail"
import { AttendanceTrend } from "@/components/attendance/AttendanceTrend"
import { AttendanceInsight } from "@/components/attendance/AttendanceInsight"
import { BottomNavigation } from "@/components/dashboard/BottomNavigation" // Reused cleanly

interface AttendanceRecord {
  id: string
  date: string
  time: string
  subject_name: string
  confidence: number
  session_id: string
}

export default function StudentAttendance() {
  // Date State
  const [currentDate, setCurrentDate] = useState(new Date()) // Controls calendar month
  const [selectedDate, setSelectedDate] = useState(new Date()) // Controls day detail
  const [viewMode, setViewMode] = useState<"day" | "month" | "overall">("month")

  // Format date to local YYYY-MM-DD reliably to match server values avoiding UTC shifts
  const formatDate = (date: Date) => {
    const d = new Date(date)
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
    return d.toISOString().split('T')[0]
  }

  const { data: attendanceData, isLoading: loading } = useQuery({
    queryKey: ['studentAttendance'],
    queryFn: async () => {
       const res = await api.get("/student/my-attendance")
       return res.data
    },
    staleTime: 1000 * 60 * 2 // Cache for 2 minutes to allow snappy routing
  })

  const records: AttendanceRecord[] = attendanceData?.records || []
  const overallStats = attendanceData?.overall_stats || null

  // Handlers for month navigation
  const handleShiftMonth = (increment: number) => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + increment, 1))
  }

  // Format for Calendar Map (YYY-MM-DD -> Status)
  const calendarData = useMemo(() => {
    return overallStats?.calendar_map || {}
  }, [overallStats])

  const selectedDateStr = formatDate(selectedDate)

  // Derive Summary for selected View strictly utilizing backend's Overall Analytic computation to match exact rules
  const { percentage, present, absent, late, label } = useMemo(() => {
    let p = 0
    let a = 0
    let label = "Overall attendance"
    
    if (viewMode === "overall") {
       p = overallStats?.present || 0
       a = overallStats?.absent || 0
    } else if (viewMode === "month") {
      const monthPrefix = formatDate(currentDate).substring(0, 7)
      Object.entries(calendarData).forEach(([dateStr, status]) => {
        if (dateStr.startsWith(monthPrefix)) {
          if (status === "Present") p++
          else if (status === "Absent") a++
        }
      })
      label = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(currentDate)
    } else if (viewMode === "day") {
      const status = calendarData[selectedDateStr]
      if (status === "Present") p++
      else if (status === "Absent") a++
      
      const d = new Date(selectedDateStr)
      d.setMinutes(d.getMinutes() + d.getTimezoneOffset()) // Keep visual alignment for format
      label = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(d)
    }
    
    const total = p + a
    const pct = total > 0 ? (p / total) * 100 : 0
    
    return {
      percentage: Number(pct.toFixed(1)),
      present: p,
      absent: a,
      late: 0,
      label
    }
  }, [calendarData, currentDate, selectedDateStr, viewMode, overallStats])

  // Strictly derive total classes tracking logic natively
  const totalClasses = present + absent

  // Derive Selected Day Classes
  const dayClasses: DayClassSession[] = records
    .filter(r => r.date === selectedDateStr)
    .map(r => ({
      id: r.id,
      subject_name: r.subject_name || "Class Session",
      time: r.time,
      status: "Present",
      attendance_time: r.time
    }))

  // Derive Trend
  const trendData = useMemo(() => {
    if (records.length < 5) return []
    return [] // Placeholder real logic for future analytic endpoint
  }, [records, totalClasses, loading])

  // Derive Insight (Empty for now if no authoritative metrics)
  const hasRecords = records.length > 0 || !loading
  const insightTitle = ""
  const insightDesc = ""

  return (
    <div className="min-h-screen w-full bg-background relative flex justify-center">
      <div className="w-full max-w-md md:max-w-2xl lg:max-w-3xl bg-background min-h-screen shadow-2xl shadow-black/5 dark:shadow-none sm:border-x border-border/40 relative flex flex-col">
        <AttendanceHeader />
        
        <main className="flex-1 overflow-y-auto pb-4 scrollbar-hide">
          {loading && !records.length ? (
            <div className="p-6 space-y-4">
               <div className="w-full h-[200px] bg-muted/30 rounded-2xl animate-pulse"></div>
               <div className="w-full h-[300px] bg-muted/30 rounded-2xl animate-pulse"></div>
            </div>
          ) : (
            <>
              <div className="px-6 pt-5 pb-2">
                <div className="bg-muted p-1 rounded-full flex text-[13px] font-semibold relative h-9 w-full z-0 overflow-hidden shadow-inner">
                   <div 
                     className="absolute inset-y-1 bg-background rounded-full shadow-sm transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] z-[-1]"
                     style={{
                        width: "calc(33.333% - 5.33px)",
                        left: viewMode === "day" ? "4px" : viewMode === "month" ? "calc(33.333% + 2px)" : "calc(66.666% - 0px)"
                     }}
                   />
                   <button 
                     onClick={() => setViewMode("day")} 
                     className={`flex-1 transition-colors ${viewMode === "day" ? "text-foreground" : "text-muted-foreground hover:text-foreground/80"}`}
                   >Day</button>
                   <button 
                     onClick={() => setViewMode("month")}
                     className={`flex-1 transition-colors ${viewMode === "month" ? "text-foreground" : "text-muted-foreground hover:text-foreground/80"}`}
                   >Month</button>
                   <button 
                     onClick={() => setViewMode("overall")}
                     className={`flex-1 transition-colors ${viewMode === "overall" ? "text-foreground" : "text-muted-foreground hover:text-foreground/80"}`}
                   >Overall</button>
                </div>
              </div>

              <AttendanceHeaderSummary 
                percentage={percentage} 
                present={present}
                absent={absent}
                late={late}
                label={label}
              />


              <AttendanceCalendar
                currentDate={currentDate}
                selectedDate={selectedDate}
                onSelectDate={setSelectedDate}
                onChangeMonth={handleShiftMonth}
                attendanceData={calendarData}
              />

              <DayAttendanceDetail
                selectedDate={selectedDate}
                classes={dayClasses}
                isLoading={loading}
              />

              <AttendanceTrend data={trendData} />

              {hasRecords && insightTitle && (
                <AttendanceInsight 
                  title={insightTitle}
                  description={insightDesc}
                />
              )}
            </>
          )}
        </main>
        
        <BottomNavigation />
      </div>
    </div>
  )
}
