import { useState, useEffect } from "react"

export interface SubjectStat {
  subject_name: string
  presentCount: number
}

// Map pseudo-random colors deterministically based on string length to give Subject Cards unique iOS-flavor icon bounds
const getColor = (str: string) => {
  const colors = [
    "bg-blue-500", "bg-indigo-500", "bg-purple-500", 
    "bg-pink-500", "bg-rose-500", "bg-orange-500", 
    "bg-emerald-500"
  ];
  return colors[str.length % colors.length];
}

export function SubjectProgressList({ subjects }: { subjects: SubjectStat[] }) {
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 200)
    return () => clearTimeout(timer)
  }, [])

  if (subjects.length === 0) return null

  return (
    <div className="px-5 py-3 mt-1">
      <div className="flex items-center justify-between px-2 mb-4">
        <h3 className="text-[17px] font-bold tracking-tight text-foreground">
          Classes By Subject
        </h3>
      </div>
      
      <div className="bg-card dark:bg-card/40 rounded-[24px] border border-transparent dark:border-border/30 shadow-[0_4px_24px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_24px_rgb(0,0,0,0.1)] overflow-hidden">
        <div className="flex flex-col divide-y divide-border/40 dark:divide-border/20">
          {subjects.map((sub, idx) => {
             const displayName = sub.subject_name === "All" || !sub.subject_name ? "General Session" : sub.subject_name;
             const colorClass = getColor(displayName);
             // We'll enforce a relative scale relative to max presentCount so the bar renders meaningfully
             const maxCount = Math.max(...subjects.map(s => s.presentCount), 1);
             const visualRatio = Math.min((sub.presentCount / maxCount) * 100, 100);

             return (
              <div key={idx} className="flex items-center justify-between p-4 px-5">
                <div className="flex items-center gap-4">
                  <div className={`w-[38px] h-[38px] rounded-[12px] flex items-center justify-center shrink-0 ${colorClass}`}>
                    <span className="text-white font-bold text-[16px]">{displayName.charAt(0).toUpperCase()}</span>
                  </div>
                  <div className="flex flex-col justify-center">
                    <h4 className="font-bold text-foreground tracking-tight text-[15px] leading-tight mb-0.5">
                      {displayName}
                    </h4>
                    <p className="text-[12px] text-foreground/50 font-medium">
                      {sub.presentCount} Classes Attended
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center justify-end w-20">
                   <div className="w-16 flex items-center justify-end rounded-full h-[6px] bg-muted/80 overflow-hidden relative">
                      <div 
                        className="absolute right-0 h-full bg-foreground transition-all duration-1000 ease-[cubic-bezier(0.4,0,0.2,1)] rounded-full"
                        style={{ width: mounted ? `${visualRatio}%` : '0%' }}
                      />
                   </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
