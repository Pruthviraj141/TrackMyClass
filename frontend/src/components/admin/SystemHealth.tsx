import { Card } from "@/components/ui/card"
import { CheckCircle2, AlertTriangle, Info } from "lucide-react"

interface SystemHealthData {
  api: "Healthy" | "Degraded" | "Unavailable" | "Checking"
  worker: "Healthy" | "Degraded" | "Unavailable" | "Checking"
  redis: "Healthy" | "Degraded" | "Unavailable" | "Checking"
  websocket: "Healthy" | "Degraded" | "Unavailable" | "Checking"
}

interface SystemHealthProps {
  data: SystemHealthData
  isLoading: boolean
}

function StatusIndicator({ label, status }: { label: string, status: SystemHealthData["api"] }) {
  const getColors = () => {
    switch (status) {
      case "Healthy": return "text-green-500"
      case "Degraded": return "text-amber-500"
      case "Unavailable": return "text-destructive"
      default: return "text-foreground/40"
    }
  }

  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-[13px] font-medium text-foreground/70">{label}</span>
      <div className="flex items-center gap-1.5 text-[12px] font-semibold tracking-wide">
        <span className={`w-1.5 h-1.5 rounded-full ${getColors()} ${status === 'Healthy' ? '' : 'animate-pulse'}`} />
        <span className={getColors()}>{status}</span>
      </div>
    </div>
  )
}

export function SystemHealth({ data, isLoading }: SystemHealthProps) {
  if (isLoading) {
    return (
      <Card className="p-5 border-border/40 shadow-sm bg-card animate-pulse h-full">
        <div className="h-5 w-24 bg-muted/50 rounded" />
      </Card>
    )
  }

  return (
    <Card className="p-5 border-border/40 shadow-sm bg-card h-full flex flex-col gap-4">
      <div>
        <h3 className="font-semibold text-[15px] leading-tight">System Health</h3>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 flex-1">
        <StatusIndicator label="API" status={data.api} />
        <StatusIndicator label="Recognition Workers" status={data.worker} />
        <StatusIndicator label="Redis" status={data.redis} />
        <StatusIndicator label="WebSocket" status={data.websocket} />
      </div>

      <div className="text-[11px] text-foreground/40 flex items-center gap-1 pt-2 border-t border-border/40">
        <Info className="w-3 h-3" />
        Last checked: Just now
      </div>
    </Card>
  )
}
