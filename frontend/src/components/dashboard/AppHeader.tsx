import { Bell, LogOut } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { useState, useRef, useEffect } from "react"

export function AppHeader({ profileName }: { profileName?: string }) {
  const initial = profileName ? profileName.charAt(0).toUpperCase() : ""
  const navigate = useNavigate()
  const [showMenu, setShowMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem("token")
    toast.success("Successfully logged out")
    navigate("/login", { replace: true })
  }

  return (
    <header className="flex items-center justify-between pt-5 pb-3 px-6 sticky top-0 z-30 bg-background/70 backdrop-blur-xl border-b border-border/40">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 bg-primary rounded-sm hidden sm:block md:hidden"></div>
        <svg className="w-7 h-7 text-primary" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" fill="none"/>
        </svg>
        <span className="font-semibold text-lg tracking-tight">TrackMyClass</span>
      </div>
      <div className="flex items-center gap-4">
        <button className="text-foreground/70 hover:text-foreground transition-colors p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-primary/20">
          <Bell className="w-5 h-5" />
        </button>
        <div className="relative" ref={menuRef}>
          <button 
            onClick={() => setShowMenu(!showMenu)}
            className="w-8 h-8 rounded-full bg-muted flex items-center justify-center border font-medium text-sm shadow-sm relative focus:outline-none focus:ring-2 focus:ring-primary/20 active:scale-95 transition-transform"
          >
            {initial}
            <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-primary border-2 border-background rounded-full"></span>
          </button>
          
          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-card rounded-xl shadow-lg border border-border/40 overflow-hidden z-50 animate-in fade-in zoom-in-95 duration-100">
              <button 
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-4 py-3 text-sm text-destructive hover:bg-destructive/10 transition-colors text-left font-medium"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
