import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { api } from "@/lib/api"

// Components
import { KpiGrid } from "@/components/admin/KpiGrid"
import { LiveSessionsPanel } from "@/components/admin/LiveSessionsPanel"
import { AttendanceTrend } from "@/components/admin/AttendanceTrend"
import { AttendanceDistribution } from "@/components/admin/AttendanceDistribution"
import { RecentActivity, type ActivityEvent } from "@/components/admin/RecentActivity"
import { AttentionPanel, type AttentionItem } from "@/components/admin/AttentionPanel"
import { SystemHealth } from "@/components/admin/SystemHealth"
import { QuickActions } from "@/components/admin/QuickActions"

interface DashboardApiData {
  active_session: boolean
  session_name: string
  start_time: string
  total_registered: number
  total_present: number
  attendance_pct: number
  present_list: any[]
  absent_list: any[]
}

interface HealthApiData {
  status: string
  worker: { status: string }
  redis: { status: string }
}

export default function AdminDashboardPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // 1. Core Dashboard Data
  const { data: dash, isLoading: loadDash, error: errDash } = useQuery<DashboardApiData>({
    queryKey: ["adminDashboardData"],
    queryFn: async () => (await api.get("/admin/dashboard-data")).data,
    refetchInterval: 10000,
  })

  // 2. Health Data
  const { data: health, isLoading: loadHealth } = useQuery<HealthApiData>({
    queryKey: ["adminHealth"],
    queryFn: async () => (await api.get("/diagnostics/metrics")).data,
    refetchInterval: 30000,
  })

  // 3. Trend Data Mapping (simulating across 5 days based on local dates)
  const { data: trend, isLoading: loadTrend } = useQuery({
    queryKey: ["adminTrendData"],
    queryFn: async () => {
      const results = []
      const today = new Date()
      // Fetch past 5 days iteratively natively efficiently
      for (let i = 4; i >= 0; i--) {
        const d = new Date(today)
        d.setDate(d.getDate() - i)
        const dateStr = d.toISOString().split("T")[0]
        try {
          const res = await api.get(`/admin/historical-data?date=${dateStr}&subject=All`)
          const pct = res.data.attendance_pct || 0
          const shortDate = d.toLocaleDateString("en-US", { month: "short", day: "numeric" })
          results.push({ date: shortDate, percentage: pct })
        } catch {
          // Ignore failures for specific dates and drop them safely
        }
      }
      return results
    },
    staleTime: 60000, 
  })

  // Actions
  const startSessionMutation = useMutation({
    mutationFn: async (name: string) => (await api.post("/attendance/session/start", { subject_name: name })).data,
    onSuccess: () => {
      toast.success("Session started successfully")
      queryClient.invalidateQueries({ queryKey: ["adminDashboardData"] })
      // Delay navigation slightly to let endpoints sync
      setTimeout(() => navigate(`sessions/active/monitor`), 500)
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || "Failed to start session")
    }
  })

  const handleStartSession = () => {
    // Generate an automatic name if none is explicitly dictated by a form
    const nameStr = `Session ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
    startSessionMutation.mutate(nameStr)
  }

  // --- Derive props safely from APIs ---

  const greeting = `Good ${new Date().getHours() < 12 ? 'morning' : 'afternoon'}, Admin`
  
  // KPI Mapping
  const kpiData = {
    totalStudents: dash?.total_registered || 0,
    attendancePct: dash?.attendance_pct || 0,
    activeSessions: dash?.active_session ? 1 : 0, 
    exceptionsCount: dash?.absent_list?.length // Using abscentees safely as proxy for "exceptions" bounds 
  }

  // Live Sessions Mapping
  const liveSessions = dash?.active_session ? [{
    id: "active",
    course: dash.session_name,
    section: "A",
    teacher: "Admin", // Fallback, could map from current auth
    present: dash.total_present,
    total: dash.total_registered,
    percentage: dash.attendance_pct,
    startTime: dash.start_time !== "N/A" ? new Date(dash.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Recently",
    isLive: true
  }] : []

  // Activity Mapping
  const activityEvents: ActivityEvent[] = []
  if (dash?.active_session) {
    activityEvents.push({
      id: "started",
      type: "session_start",
      message: `${dash.session_name} session started`,
      time: dash.start_time !== "N/A" ? new Date(dash.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Just now"
    })
  }
  // Add some synthetic present events based on actual lists to populate gracefully
  if (dash?.present_list && dash.present_list.length > 0) {
    activityEvents.push({
      id: "recognized",
      type: "recognition",
      message: `${dash.present_list.length} students marked present`,
      time: "Just now"
    })
  }

  // Attention Panel Mapping
  const attentionItems: AttentionItem[] = []
  if (dash?.attendance_pct !== undefined && dash.attendance_pct > 0 && dash.attendance_pct < 60) {
    attentionItems.push({
      id: "low-attendance",
      message: `${dash.absent_list?.length || 0} students below attendance threshold`,
      route: "reports"
    })
  }

  // Health Mapping
  const systemHealth = {
    api: (errDash ? "Unavailable" : "Healthy") as "Unavailable" | "Healthy",
    worker: (health?.worker?.status === "ok" ? "Healthy" : "Degraded") as "Degraded" | "Healthy",
    redis: (health?.redis?.status === "ok" ? "Healthy" : "Degraded") as "Degraded" | "Healthy",
    websocket: (health?.status === "healthy" ? "Healthy" : "Degraded") as "Degraded" | "Healthy"
  }

  return (
    <div className="w-full flex flex-col gap-6 font-sans animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header Area */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">{greeting}</h1>
          <p className="text-[13px] text-foreground/50 mt-1">Here's what's happening across your institution today.</p>
        </div>
      </div>

      {errDash && (
        <div className="p-4 bg-destructive/10 text-destructive text-sm font-semibold rounded-lg flex items-center justify-between border border-destructive/20">
          Failed to load dashboard data. Assuming degraded state.
          <button onClick={() => queryClient.invalidateQueries()} className="underline text-xs">Retry</button>
        </div>
      )}

      {/* Primary Row */}
      <KpiGrid data={kpiData} isLoading={loadDash} />

      {/* Main Container */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Column (3/4 width) */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <LiveSessionsPanel sessions={liveSessions} isLoading={loadDash} />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
            <AttendanceTrend data={trend || []} isLoading={loadTrend} />
            <RecentActivity events={activityEvents} isLoading={loadDash} />
          </div>
        </div>

        {/* Right Column (1/4 width) */}
        <div className="lg:col-span-1 flex flex-col gap-6 h-full">
          <AttendanceDistribution 
            present={dash?.total_present || 0}
            absent={dash?.absent_list?.length || 0}
            late={0} // Late logic not cleanly separable from pure API right now
            isLoading={loadDash}
          />
          <AttentionPanel items={attentionItems} />
          <SystemHealth data={systemHealth} isLoading={loadHealth} />
          <QuickActions 
            onAddStudent={() => navigate("students")}
            onStartSession={handleStartSession}
            onViewReports={() => navigate("reports")}
            onAnalytics={() => navigate("reports")}
            isStartingSession={startSessionMutation.isPending}
          />
        </div>

      </div>

    </div>
  )
}
