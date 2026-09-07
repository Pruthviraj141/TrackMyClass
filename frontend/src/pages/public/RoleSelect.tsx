import { useParams, useNavigate } from "react-router-dom"
import { useStore } from "@/store"
import { GraduationCap, Presentation, ShieldCheck } from "lucide-react"

export default function RoleSelect() {
  const { collegeCode } = useParams<{ collegeCode: string }>()
  const navigate = useNavigate()
  const { institutionName } = useStore() // Assumes we set this in Landing

  const roles = [
    {
      id: "student",
      title: "Student",
      icon: GraduationCap,
      description: "Access dashboard, attendance, and profile.",
      color: "text-blue-600",
      bg: "bg-blue-50 dark:bg-blue-500/10",
      border: "hover:border-blue-200"
    },
    {
      id: "teacher",
      title: "Teacher",
      icon: Presentation,
      description: "Manage classes, take attendance, and view reports.",
      color: "text-indigo-600",
      bg: "bg-indigo-50 dark:bg-indigo-500/10",
      border: "hover:border-indigo-200"
    },
    {
      id: "admin",
      title: "Institution Admin",
      icon: ShieldCheck,
      description: "Manage institution settings, students, and teachers.",
      color: "text-purple-600",
      bg: "bg-purple-50 dark:bg-purple-500/10",
      border: "hover:border-purple-200"
    }
  ]

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            {institutionName || collegeCode?.toUpperCase()}
          </h1>
          <p className="text-muted-foreground font-medium">
            Welcome to TrackMyClass. Continue as:
          </p>
        </div>

        <div className="grid gap-3">
          {roles.map((role) => {
            const Icon = role.icon
            return (
              <button
                key={role.id}
                onClick={() => navigate(`/${collegeCode}/login?role=${role.id}`)}
                className={`flex items-center gap-4 p-4 rounded-xl border bg-card text-left transition-all hover:-translate-y-0.5 hover:shadow-sm ${role.border}`}
              >
                <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 ${role.bg}`}>
                  <Icon className={`w-6 h-6 w-5 h-5 ${role.color}`} />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground text-[15px]">{role.title}</h3>
                  <p className="text-xs text-muted-foreground font-medium mt-0.5">{role.description}</p>
                </div>
              </button>
            )
          })}
        </div>
        
        <div className="text-center pt-4">
          <button 
            onClick={() => navigate("/")}
            className="text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
          >
            Switch Institution
          </button>
        </div>
      </div>
    </div>
  )
}
