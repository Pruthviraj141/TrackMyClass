import { Link, useLocation, useParams } from "react-router-dom"
import { Home, CalendarCheck, FileStack, UserCircle2 } from "lucide-react"

export function BottomNavigation() {
  const location = useLocation()
  const { collegeCode } = useParams<{ collegeCode: string }>()
  const prefix = collegeCode ? `/${collegeCode}` : ""
  
  const navItems = [
    { path: `${prefix}/student/dashboard`, label: "Home", icon: Home },
    { path: `${prefix}/student/attendance`, label: "Attendance", icon: CalendarCheck },
    { path: `${prefix}/student/classes`, label: "Classes", icon: FileStack },
    { path: `${prefix}/student/profile`, label: "Profile", icon: UserCircle2 },
  ]

  return (
    <>
      {/* Spacer to prevent content from hiding behind fixed floating nav */}
      <div className="h-[120px] w-full shrink-0" />
      
      <div className="fixed bottom-0 left-0 right-0 z-50 flex justify-center pb-[calc(env(safe-area-inset-bottom)+1.25rem)] px-4 pointer-events-none">
        
        <div className="pointer-events-auto flex items-center justify-between gap-1 sm:gap-2 px-5 py-2.5 bg-white/85 dark:bg-[#18181b]/85 backdrop-blur-xl border border-black/5 dark:border-white/10 rounded-[32px] shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.4)] transition-all">
          
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path) || 
                             (item.path === "/student/dashboard" && location.pathname === "/student")
                             
            const Icon = item.icon
            
            return (
              <Link 
                key={item.path}
                to={item.path}
                className="flex flex-col items-center justify-center w-[60px] sm:w-[68px] h-[52px] gap-1 touch-manipulation focus:outline-none rounded-2xl active:scale-90 transition-transform duration-200"
              >
                <div className={`transition-colors duration-300 flex flex-col items-center ${isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'}`}>
                  
                  <div className={`relative flex items-center justify-center transition-all duration-300 ${isActive ? 'drop-shadow-[0_0_8px_rgba(79,70,229,0.3)] dark:drop-shadow-[0_0_12px_rgba(129,140,248,0.4)] -translate-y-0.5' : ''}`}>
                    <Icon className="w-5 h-5" strokeWidth={isActive ? 2.5 : 2} />
                  </div>
                  
                  <span className={`text-[10px] mt-[3px] tracking-tight transition-all duration-300 ${isActive ? 'font-semibold' : 'font-medium'}`}>
                    {item.label}
                  </span>
                  
                </div>
              </Link>
            )
          })}
        </div>
      </div>
    </>
  )
}
