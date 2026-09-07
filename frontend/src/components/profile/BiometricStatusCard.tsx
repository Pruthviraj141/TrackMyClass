import { ShieldCheck, Lock } from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"

interface BiometricStatusProps {
  isRegistered: boolean
  isLoading?: boolean
}

export function BiometricStatusCard({ isRegistered, isLoading }: BiometricStatusProps) {
  const navigate = useNavigate()
  const { collegeCode } = useParams<{ collegeCode: string }>()
  
  if (isLoading) {
    return (
       <div className="px-5 py-2">
         <div className="bg-card rounded-[20px] shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none p-5 flex gap-4 h-[115px] animate-pulse">
           <div className="w-12 h-12 rounded-full bg-muted/20 flex-shrink-0"></div>
           <div className="flex-1 space-y-2 py-1">
             <div className="h-4 w-32 bg-muted/20 rounded"></div>
             <div className="h-3 w-48 bg-muted/20 rounded"></div>
             <div className="h-4 w-24 bg-muted/20 rounded mt-2"></div>
           </div>
         </div>
       </div>
    )
  }

  return (
    <div className="px-5 py-2">
      <div className="bg-card rounded-[20px] p-5 shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none flex gap-4 items-start">
        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
          <Lock className="w-5 h-5 text-primary" />
        </div>
        <div className="flex-1">
          <h3 className="text-[16px] font-semibold text-foreground leading-tight">Face recognition</h3>
          
          <div className="flex items-center gap-1.5 mt-1.5 mb-1.5">
            {isRegistered ? (
               <>
                 <ShieldCheck className="w-3.5 h-3.5 text-green-600" />
                 <span className="text-[12px] font-semibold text-green-600">Registration complete</span>
               </>
            ) : (
               <>
                 <span className="text-[12px] font-semibold text-amber-600">Registration pending</span>
               </>
            )}
          </div>
          
          <p className="text-[12px] text-foreground/60 leading-snug mb-3 max-w-[220px]">
            Your biometric profile is securely managed for attendance verification.
          </p>
          
          <button 
             onClick={() => navigate(`/${collegeCode}/student/face-enrollment`)}
             className="text-[13px] font-medium text-primary hover:text-primary/80 transition-colors bg-primary/5 hover:bg-primary/10 px-3 py-1.5 rounded-full inline-flex cursor-pointer"
          >
            {isRegistered ? "Manage face data" : "Set up face recognition"}
          </button>
        </div>
      </div>
    </div>
  )
}
