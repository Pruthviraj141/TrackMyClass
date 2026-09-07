import { Book, ChevronRight } from "lucide-react"

interface SubjectCardProps {
  subjectName: string;
  courseDetails: string;
}

export function SubjectCard({ subjectName, courseDetails }: SubjectCardProps) {
  return (
    <div className="px-6 py-1">
      <div className="flex items-center justify-between p-3.5 bg-card dark:bg-card/40 rounded-[20px] shadow-[0_4px_24px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_24px_rgb(0,0,0,0.1)] cursor-pointer hover:bg-muted/50 transition-colors border border-transparent dark:border-border/30">
        <div className="flex items-center gap-3.5">
          <div className="w-[46px] h-[46px] rounded-[14px] bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center shadow-inner shadow-white/20">
            <Book className="w-[22px] h-[22px] text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-[15px] font-semibold text-foreground tracking-tight leading-none mb-1.5">{subjectName}</span>
            <span className="text-[12px] font-medium text-foreground/50 leading-none">{courseDetails}</span>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-foreground/30 mr-2" />
      </div>
    </div>
  )
}
