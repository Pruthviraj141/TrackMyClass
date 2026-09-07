import { Outlet, Link, useLocation, useNavigate, useParams } from "react-router-dom"
import { LayoutDashboard, Users, FileText, Video, LogOut } from "lucide-react"
import { useMutation } from "@tanstack/react-query"
import { cn } from "@/lib/utils"
import { api } from "@/lib/api"
import { toast } from "sonner"
import { useStore } from "@/store"

export default function AdminLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { collegeCode } = useParams<{ collegeCode: string }>()
  const { clearInstitution } = useStore()

  const navItems = [
    { name: "Dashboard", href: `/${collegeCode}/admin/dashboard`, icon: LayoutDashboard },
    { name: "Live Monitor", href: `/${collegeCode}/admin/sessions/active/monitor`, icon: Video },
    { name: "Students", href: `/${collegeCode}/admin/students`, icon: Users },
    { name: "Reports", href: `/${collegeCode}/admin/reports`, icon: FileText },
  ]

  const logoutMutation = useMutation({
    mutationFn: async () => {
      await api.post("/auth/logout")
    },
    onSuccess: () => {
      toast.success("Logged out successfully")
      localStorage.removeItem("token")
      clearInstitution()
      navigate(`/${collegeCode}/login`)
    },
    onError: () => {
      toast.error("Failed to logout")
    }
  })

  const handleLogout = () => {
    logoutMutation.mutate()
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background">
      {/* Sidebar (Desktop) */}
      <aside className="hidden md:flex w-64 flex-col border-r border-border/50 bg-background/70 backdrop-blur-3xl h-screen sticky top-0">
        <div className="p-6 border-b border-border/50 h-[88px] flex items-center gap-3">
          <LayoutDashboard className="h-6 w-6 text-primary" />
          <span className="font-semibold tracking-tight text-xl text-foreground">Admin Center</span>
        </div>
        <nav className="flex-1 py-6 px-4 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname.includes(item.href.split('/').pop() || item.href)
            return (
              <Link
                key={item.href}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 px-4 py-2.5 rounded-[12px] transition-all text-[15px] font-medium",
                  isActive 
                    ? "bg-primary text-primary-foreground shadow-sm shadow-primary/20" 
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>
        <div className="p-4 border-t border-border/50 bg-background/50 backdrop-blur-xl">
          <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 text-[15px] font-medium text-destructive hover:bg-destructive/10 rounded-[12px] transition-all">
            <LogOut className="h-5 w-5" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-x-hidden pb-[90px] md:pb-0">
        {/* Mobile Header */}
        <header className="md:hidden h-16 border-b border-border/50 bg-background/70 backdrop-blur-xl flex items-center justify-between px-5 sticky top-0 z-30">
          <div className="flex items-center gap-2">
            <LayoutDashboard className="h-5 w-5 text-primary" />
            <span className="font-semibold tracking-tight text-lg text-foreground">Admin</span>
          </div>
          <button onClick={handleLogout} className="text-sm font-medium text-primary hover:opacity-80 active:scale-95 transition-all">
            Logout
          </button>
        </header>

        <div className="flex-1 p-4 md:p-8 lg:p-10 w-full animate-in fade-in">
          <Outlet />
        </div>
      </main>

      {/* Mobile Bottom Nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-[80px] bg-background/80 backdrop-blur-2xl border-t border-border/50 flex items-center justify-around z-50 pb-safe shadow-[0_-10px_40px_rgba(0,0,0,0.03)]">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname.includes(item.href.split('/').pop() || item.href)
          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                "flex flex-col items-center justify-center w-full h-full space-y-1.5 transition-all duration-300",
                isActive ? "text-primary scale-105" : "text-muted-foreground hover:text-foreground active:scale-95"
              )}
            >
              <div className={cn(
                "p-1.5 rounded-full transition-colors",
                isActive && "bg-primary/10"
              )}>
                <Icon className={cn("h-5 w-5", isActive ? "stroke-[2.5px]" : "stroke-2")} />
              </div>
              <span className="text-[10px] font-medium tracking-wide">{item.name}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
