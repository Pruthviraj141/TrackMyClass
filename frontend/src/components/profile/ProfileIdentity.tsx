interface ProfileIdentityProps {
  name: string
  role?: string
  department?: string
  institution?: string
  rollNumber?: string
  isLoading?: boolean
}

export function ProfileIdentity({ 
  name, 
  role = "Student", 
  department = "Department", 
  institution = "Institution", 
  rollNumber = "Roll No.",
  isLoading 
}: ProfileIdentityProps) {
  
  if (isLoading) {
    return (
      <div className="flex flex-col items-center py-6 px-4 animate-pulse">
        <div className="w-24 h-24 rounded-full bg-muted/40 mb-4"></div>
        <div className="h-6 w-48 bg-muted/40 rounded mb-2"></div>
        <div className="h-3 w-64 bg-muted/40 rounded mb-1"></div>
        <div className="h-3 w-56 bg-muted/40 rounded mb-1"></div>
        <div className="h-3 w-32 bg-muted/40 rounded"></div>
      </div>
    )
  }

  // Provide realistic defaults if fields are empty to maintain layout exactly
  const displayDept = department || "Artificial Intelligence & Data Science"
  const displayInst = institution || "Vishwakarma Institute of Information Technology"
  const displayRoll = rollNumber || "24AIDS1042"

  return (
    <div className="flex flex-col items-center py-6 px-6 text-center">
      {/* Avatar Container with subtle inner shadow to mimic the image exactly */}
      <div className="w-24 h-24 rounded-full bg-muted overflow-hidden mb-4 border border-border/30 shadow-sm flex items-center justify-center text-4xl text-muted-foreground font-semibold">
        {name.charAt(0).toUpperCase()}
      </div>
      
      <h1 className="text-2xl font-bold tracking-tight text-foreground mb-1.5">{name}</h1>
      
      <div className="text-[13px] leading-tight text-foreground/60 space-y-0.5">
        <p>
          <span className="font-medium text-foreground/70">{role}</span> · {displayDept}
        </p>
        <p>{displayInst}</p>
        <p>Roll No. {displayRoll}</p>
      </div>
    </div>
  )
}
