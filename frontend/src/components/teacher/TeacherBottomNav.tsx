import { Link, useLocation, useParams } from "react-router-dom"
import { CalendarCheck, Radio } from "lucide-react"

export function TeacherBottomNav() {
  const location = useLocation()
  const { collegeCode } = useParams<{ collegeCode: string }>()
  
  const navItems = [
    { path: `/${collegeCode}/teacher/live`, label: "Live", icon: Radio },
    { path: `/${collegeCode}/teacher/attendance`, label: "Attendance", icon: CalendarCheck },
  ]

  return (
    <>
      <div className="h-[88px] w-full shrink-0 md:hidden" />
      
      <div className="fixed bottom-0 left-0 right-0 w-full bg-background/80 backdrop-blur-xl border-t border-border/40 pb-safe z-50 md:hidden pb-4">
        <div className="flex items-center justify-around h-16 px-1 max-w-md mx-auto relative">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/')
            const Icon = item.icon
            

            
            return (
              <Link 
                key={item.path}
                to={item.path}
                className="flex flex-col items-center justify-center w-14 h-full gap-1 touch-manipulation focus:outline-none"
              >
                <div className={`transition-colors flex flex-col items-center ${isActive ? 'text-primary' : 'text-foreground/40 hover:text-foreground/70'}`}>
                  <Icon className="w-6 h-6" strokeWidth={isActive ? 2.5 : 2} />
                  <span className={`text-[10px] mt-1 font-medium ${isActive ? 'font-semibold' : ''}`}>
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
