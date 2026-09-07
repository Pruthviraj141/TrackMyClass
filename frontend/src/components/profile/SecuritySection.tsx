import { Key, MapPin, AlertTriangle, ChevronRight } from "lucide-react"

export function SecuritySection() {
  return (
    <div className="px-5 py-2">
      <h2 className="text-[16px] font-semibold text-foreground mb-2 px-1">Security</h2>
      
      <div className="bg-card rounded-[20px] shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none overflow-hidden">
        
        <button className="w-full flex items-center justify-between px-5 py-3.5 border-b border-border/40 hover:bg-muted/30 transition-colors focus:outline-none focus:bg-muted/30">
          <div className="flex items-center gap-3">
            <Key className="w-4 h-4 text-foreground/60" />
            <span className="text-[14px] text-foreground font-medium">Change password</span>
          </div>
          <ChevronRight className="w-4 h-4 text-foreground/30" />
        </button>
        
        <button className="w-full flex items-center justify-between px-5 py-3.5 border-b border-border/40 hover:bg-muted/30 transition-colors focus:outline-none focus:bg-muted/30">
          <div className="flex items-center gap-3">
            <MapPin className="w-4 h-4 text-foreground/60" />
            <span className="text-[14px] text-foreground font-medium">Active sessions</span>
          </div>
        </button>

        <button className="w-full flex items-center justify-between px-5 py-3.5 hover:bg-muted/30 transition-colors focus:outline-none focus:bg-muted/30">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-4 h-4 text-foreground/60" />
            <span className="text-[14px] text-foreground font-medium">Two-step verification</span>
          </div>
        </button>

      </div>
    </div>
  )
}
