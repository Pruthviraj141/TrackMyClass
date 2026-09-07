import { Outlet, useLocation, useNavigate, useParams } from "react-router-dom"
import { LogOut } from "lucide-react"
import { toast } from "sonner"
import { TeacherBottomNav } from "@/components/teacher/TeacherBottomNav"

export default function TeacherLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { collegeCode } = useParams<{ collegeCode: string }>()

  const handleLogout = () => {
    localStorage.removeItem("token")
    toast.success("Logged out successfully")
    navigate(`/${collegeCode}/login`)
  }

  const isLive = location.pathname.endsWith("/live")

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {!isLive && (
        <header className="pt-6 pb-2 px-5 sticky top-0 z-30 bg-background/70 backdrop-blur-xl flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <svg className="w-8 h-8 text-primary shrink-0" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" fill="none"/>
            </svg>
            <div className="flex flex-col">
              <span className="font-bold tracking-tight text-lg leading-tight text-foreground">TrackMyClass</span>
              <span className="text-sm text-muted-foreground font-medium leading-none">Teacher</span>
            </div>
          </div>
          
          {/* Right Actions */}
          <div className="flex items-center gap-4">
             <div className="flex items-center gap-3">
                {/* Notification Bell */}
                <button className="relative p-1 text-muted-foreground hover:text-foreground transition-colors focus:outline-none hidden sm:block">
                  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
                  <span className="absolute top-0 right-1 w-2.5 h-2.5 bg-destructive rounded-full border-2 border-background"></span>
                </button>
                {/* Avatar */}
                <div className="w-9 h-9 rounded-full bg-muted flex items-center justify-center font-bold text-sm tracking-wider text-muted-foreground">
                   PG
                </div>
             </div>
             
             {/* Logout Pill */}
             <button
               onClick={handleLogout}
               className="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary rounded-lg text-sm font-semibold transition-all active:scale-95"
             >
               <LogOut className="h-4 w-4" strokeWidth={2.5} />
               <span className="hidden sm:inline">Logout</span>
             </button>
          </div>
        </header>
      )}

      <main className="flex-1 w-full max-w-full">
        <Outlet />
      </main>

      {!isLive && <TeacherBottomNav />}
    </div>
  )
}
