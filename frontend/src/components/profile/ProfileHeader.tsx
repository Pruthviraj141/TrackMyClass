import { ArrowLeft, Settings } from "lucide-react"
import { useNavigate } from "react-router-dom"

export function ProfileHeader() {
  const navigate = useNavigate()

  return (
    <header className="flex items-center justify-between px-4 py-3 bg-background sticky top-0 z-10 border-b border-border/40">
      <div className="flex items-center gap-3">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 -ml-2 text-foreground/80 hover:text-foreground rounded-full hover:bg-muted/50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
      </div>
      <span className="font-semibold text-lg tracking-tight">Profile</span>
      <button className="p-2 -mr-2 text-foreground/80 hover:text-foreground rounded-full hover:bg-muted/50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20">
        <Settings className="w-5 h-5" />
      </button>
    </header>
  )
}
