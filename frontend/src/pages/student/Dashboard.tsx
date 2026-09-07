import { api } from "@/lib/api"
import { AppHeader } from "@/components/dashboard/AppHeader"
import { Greeting } from "@/components/dashboard/Greeting"
import { AttendanceSummaryCard, AttendanceSummarySkeleton } from "@/components/dashboard/AttendanceSummaryCard"
import { TodaySection, type ClassSession } from "@/components/dashboard/TodaySection"
import { NextClassCard } from "@/components/dashboard/NextClassCard"
import { AttendanceInsightCard } from "@/components/dashboard/AttendanceInsightCard"
import { SubjectProgressList } from "@/components/dashboard/SubjectProgressList"
import { BottomNavigation } from "@/components/dashboard/BottomNavigation"

// Interfaces removed temporarily since React Query infers or uses any in this file currently unless strictly typed via hooks

import { useQuery } from "@tanstack/react-query"

export default function StudentDashboard() {
  const { data: profile } = useQuery({
    queryKey: ['studentProfile'],
    queryFn: async () => {
      const res = await api.get("/student/my-profile")
      return res.data
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  })

  const { data: attendanceData, isLoading: loadingAttendance } = useQuery({
    queryKey: ['studentAttendance'],
    queryFn: async () => {
       const res = await api.get("/student/my-attendance")
       return res.data
    },
    staleTime: 1000 * 60 * 2
  })

  // Destructure cached data
  const records = attendanceData?.records || []
  const overallStats = attendanceData?.overall_stats || null
  const subjectStats = attendanceData?.subject_stats || []

  // Summary Metrics direct from Backend Authority
  const percentage = overallStats?.percentage || 0
  const present = overallStats?.present || 0
  const absent = overallStats?.absent || 0
  const late = overallStats?.late || 0

  // Subject Breakdowns directly from Backend
  const mappedSubjects = subjectStats.map(s => ({
    subject_name: s.subject_name,
    presentCount: s.present,
    totalClasses: s.total_classes,
    percentage: s.percentage
  }))

  // Derive Today's Classes
  const today = new Date().toISOString().split("T")[0]
  const todayRecords = records.filter(r => r.date === today)
  
  // Generating a mix of real backend Data + mock upcoming limits structurally
  const todayClasses: ClassSession[] = todayRecords.map(r => ({
    id: r.id,
    subject_name: r.subject_name || "Session",
    time: r.time,
    status: "Present"
  }))
  
  // No mock generation block injected for visual consistency
  return (
    <div className="min-h-screen w-full bg-background relative flex justify-center">
      <div className="w-full max-w-md md:max-w-2xl lg:max-w-3xl bg-background min-h-screen shadow-2xl shadow-black/5 dark:shadow-none sm:border-x border-border/40 relative flex flex-col">
        <AppHeader profileName={profile?.name} />
        
        <main className="pb-32 px-4 sm:px-6 pt-4 space-y-6 overflow-x-hidden">
          <div>
            <Greeting name={profile?.name} />
          </div>
          
          <div>
            {loadingAttendance ? (
              <AttendanceSummarySkeleton />
            ) : (
              <AttendanceSummaryCard 
                percentage={percentage} 
                present={present} 
                absent={absent} 
                late={late} 
              />
            )}
          </div>
          
          <div>
            {records.length > 0 && <NextClassCard />}
          </div>

          <div>
            <TodaySection classes={todayClasses} isLoading={loadingAttendance} />
          </div>

          <div>
            {!loadingAttendance && <SubjectProgressList subjects={mappedSubjects} />}
          </div>
          
          <div>
            {records.length > 0 && <AttendanceInsightCard />}
          </div>
        </main>
        
        <BottomNavigation />
      </div>
    </div>
  )
}
