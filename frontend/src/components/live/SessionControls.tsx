import { Square, Pause, Sun } from "lucide-react"

interface SessionControlsProps {
  onEndSession: () => void
  onPause?: () => void
  onSettings?: () => void
  isEnding?: boolean
}

export function SessionControls({ onEndSession, onPause, onSettings, isEnding }: SessionControlsProps) {
  return (
    <div className="px-5 py-3 w-full flex items-center justify-between gap-3">
      {/* End Session Button */}
      <button 
        onClick={onEndSession}
        disabled={isEnding}
        className="flex-1 flex items-center justify-center gap-2 bg-destructive/10 text-destructive font-semibold py-3.5 rounded-[16px] transition-transform active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none hover:bg-destructive/15 focus:outline-none focus:ring-2 focus:ring-destructive/30"
      >
        <Square className="w-4 h-4 fill-current" />
        <span className="text-[15px]">End Session</span>
      </button>

      {/* Secondary Controls */}
      <button 
        onClick={onPause}
        className="w-[52px] h-[52px] flex items-center justify-center bg-muted/40 hover:bg-muted/60 text-foreground/70 transition-colors rounded-[16px] focus:outline-none focus:ring-2 focus:ring-primary/20"
      >
        <Pause className="w-5 h-5 fill-current" />
      </button>

      <button 
        onClick={onSettings}
        className="w-[52px] h-[52px] flex items-center justify-center bg-muted/40 hover:bg-muted/60 text-foreground/70 transition-colors rounded-[16px] focus:outline-none focus:ring-2 focus:ring-primary/20"
      >
        <Sun className="w-5 h-5" />
      </button>
    </div>
  )
}
