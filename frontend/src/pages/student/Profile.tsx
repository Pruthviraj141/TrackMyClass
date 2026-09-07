import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { ProfileHeader } from "@/components/profile/ProfileHeader"
import { ProfileIdentity } from "@/components/profile/ProfileIdentity"
import { AccountInformation } from "@/components/profile/AccountInformation"
import { AttendanceSnapshot } from "@/components/profile/AttendanceSnapshot"
import { BiometricStatusCard } from "@/components/profile/BiometricStatusCard"
import { PreferencesSection } from "@/components/profile/PreferencesSection"
import { SecuritySection } from "@/components/profile/SecuritySection"
import { LogoutAction } from "@/components/profile/LogoutAction"
import { BottomNavigation } from "@/components/dashboard/BottomNavigation"

export default function StudentProfile() {
  const { data: profile, isLoading: loadingProfile } = useQuery({
    queryKey: ['studentProfile'],
    queryFn: async () => {
      const res = await api.get("/student/my-profile")
      return res.data
    },
    staleTime: 1000 * 60 * 5,
  })

  const { data: attendanceData, isLoading: loadingAttendance } = useQuery({
    queryKey: ['studentAttendance'],
    queryFn: async () => {
       const res = await api.get("/student/my-attendance")
       return res.data
    },
    staleTime: 1000 * 60 * 2
  })
  
  const overallStats = attendanceData?.overall_stats || null

  // Derive final stats purely from authoritative backend
  const dispPercentage = overallStats?.percentage || 0
  const dispPresent = overallStats?.present || 0
  const dispAbsent = overallStats?.absent || 0
  const dispLate = overallStats?.late || 0

  // Fallbacks for profile missing edgecases
  const studentName = profile?.name || (loadingProfile ? "" : "-")
  const studentRoll = profile?.roll_number || (loadingProfile ? "" : "Not Available")
  const studentEmail = profile?.email || ""
  
  const isBiometricRegistered = true 
  const loadingBiometric = false

  return (
    <div className="min-h-screen w-full bg-background relative flex justify-center">
      <div className="w-full max-w-md md:max-w-2xl lg:max-w-3xl bg-background min-h-screen shadow-2xl shadow-black/5 dark:shadow-none sm:border-x border-border/40 relative flex flex-col">
        <ProfileHeader />
        
        <main className="flex-1 overflow-y-auto pb-32 px-4 sm:px-6 pt-4 space-y-6 scrollbar-hide">
          <ProfileIdentity 
            name={studentName}
            rollNumber={studentRoll}
            isLoading={loadingProfile}
          />
          
          <AccountInformation 
            isLoading={loadingProfile}
            studentId={studentRoll}
            email={studentEmail}
          />
          
          <AttendanceSnapshot 
            percentage={dispPercentage}
            present={dispPresent}
            absent={dispAbsent}
            late={dispLate}
            isLoading={loadingAttendance}
          />
          
          <BiometricStatusCard 
            isRegistered={isBiometricRegistered}
            isLoading={loadingBiometric}
          />
          
          <PreferencesSection />
          
          <SecuritySection />
          
          <LogoutAction />
        </main>
        
        <BottomNavigation />
      </div>
    </div>
  )
}
