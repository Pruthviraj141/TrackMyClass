import { Mail, GraduationCap, IdCard } from "lucide-react"

interface AccountInformationProps {
  email?: string
  studentId?: string
  department?: string
  year?: string
  isLoading?: boolean
}

export function AccountInformation({ 
  email = "", 
  studentId = "", 
  department = "", 
  year = "",
  isLoading
}: AccountInformationProps) {

  const displayEmail = email || "Not Provided"
  const displayId = studentId || "Not Provided"
  const displayDept = department || "Not Provided"

  if (isLoading) {
    return (
      <div className="px-5 py-2">
        <h2 className="text-[15px] font-semibold text-foreground mb-3 px-1">Account</h2>
        <div className="bg-card rounded-[20px] shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none p-4 h-[160px] animate-pulse">
          <div className="h-full w-full bg-muted/20 rounded-lg"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="px-5 py-2">
      <h2 className="text-[16px] font-semibold text-foreground mb-2 px-1">Account</h2>
      
      <div className="bg-card rounded-[20px] shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none overflow-hidden">
        
        {/* Email Row */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-border/40">
          <span className="text-[14px] text-foreground/60 w-1/3">Email</span>
          <div className="flex items-center gap-2 text-right justify-end w-2/3">
            <span className="text-[14px] font-medium text-foreground truncate">{displayEmail}</span>
            <Mail className="w-4 h-4 text-foreground/40 shrink-0" />
          </div>
        </div>
        
        {/* Student ID Row */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-border/40">
          <span className="text-[14px] text-foreground/60 w-1/3 leading-tight">Student ID /<br/>Roll Number</span>
          <div className="flex items-center gap-2 text-right justify-end w-2/3">
            <span className="text-[14px] font-medium text-foreground">{displayId}</span>
            <IdCard className="w-4 h-4 text-foreground/40 shrink-0" />
          </div>
        </div>
        
        {/* Department Row */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-border/40">
          <span className="text-[14px] text-foreground/60 w-1/3">Department</span>
          <div className="flex items-center gap-2 text-right justify-end w-2/3">
            <span className="text-[13px] font-medium text-foreground leading-tight">{displayDept}</span>
            <GraduationCap className="w-4 h-4 text-foreground/40 shrink-0" />
          </div>
        </div>
        
        {year && (
          <div className="flex items-center justify-between px-5 py-3.5">
            <span className="text-[14px] text-foreground/60 w-1/3">Year</span>
            <div className="flex items-center gap-2 text-right justify-end w-2/3">
              <span className="text-[14px] font-medium text-foreground">{year}</span>
            </div>
          </div>
        )}
        
      </div>
    </div>
  )
}
