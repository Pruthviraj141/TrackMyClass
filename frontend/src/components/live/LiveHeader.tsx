import { ChevronLeft } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useEffect, useState } from "react"

interface LiveHeaderProps {
  courseName?: string
  details?: string
  sessionStatus?: "LIVE" | "PAUSED" | "CONNECTING" | "ENDED" | "ERROR"
  startTimeMs?: number
}

export function LiveHeader({
  courseName = "Computer Networks",
  details = "B.Tech · 3rd Year · Section A",
  sessionStatus = "LIVE",
  startTimeMs = Date.now(),
}: LiveHeaderProps) {
  const navigate = useNavigate()
  const [elapsed, setElapsed] = useState("00:00:00")

  useEffect(() => {
    if (sessionStatus !== "LIVE" && sessionStatus !== "PAUSED") return

    const interval = setInterval(() => {
      const ms = Date.now() - startTimeMs
      const totalSeconds = Math.floor(ms / 1000)
      const hours = Math.floor(totalSeconds / 3600)
      const minutes = Math.floor((totalSeconds % 3600) / 60)
      const seconds = totalSeconds % 60

      setElapsed(
        `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
      )
    }, 1000)

    return () => clearInterval(interval)
  }, [startTimeMs, sessionStatus])

  return (
    <header className="flex items-center justify-between px-4 py-3 sticky top-0 z-10 w-full bg-background/80 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate(-1)}
          className="w-10 h-10 flex items-center justify-center bg-muted/50 hover:bg-muted/80 text-foreground rounded-[14px] transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div className="flex flex-col">
          <h1 className="font-bold text-[17px] leading-tight text-foreground tracking-tight">{courseName}</h1>
          <span className="text-[12px] text-foreground/50 font-medium">{details}</span>
        </div>
      </div>

      <div className="flex flex-col items-end gap-1">
        <div className="flex items-center gap-1.5 bg-destructive/10 px-2 py-0.5 rounded-sm">
          <span className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
          <span className="text-destructive font-bold text-[10px] tracking-wider uppercase">{sessionStatus}</span>
        </div>
        <span className="text-[12px] text-foreground/50 font-mono tracking-tighter" style={{ fontVariantNumeric: "tabular-nums" }}>
          {elapsed}
        </span>
      </div>
    </header>
  )
}
