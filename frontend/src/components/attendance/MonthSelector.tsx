import { ChevronLeft, ChevronRight } from "lucide-react"

interface MonthSelectorProps {
  currentDate: Date
  onPrevMonth: () => void
  onNextMonth: () => void
}

export function MonthSelector({ currentDate, onPrevMonth, onNextMonth }: MonthSelectorProps) {
  const monthName = currentDate.toLocaleString('default', { month: 'long' })
  const year = currentDate.getFullYear()

  return (
    <div className="px-6 py-2">
      <div className="flex items-center justify-between">
        <button 
          onClick={onPrevMonth}
          className="p-2.5 rounded-[14px] text-foreground/60 hover:text-foreground hover:bg-muted/80 transition-all active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary/20"
        >
          <ChevronLeft className="w-[22px] h-[22px]" />
        </button>
        
        <div className="flex flex-col items-center">
          <span className="text-[17px] font-semibold tracking-tight">{monthName} {year}</span>
          <div className="flex gap-1 mt-1">
            <span className="w-4 h-1 rounded-full bg-primary/70"></span>
            <span className="w-1 h-1 rounded-full bg-border"></span>
          </div>
        </div>

        <button 
          onClick={onNextMonth}
          className="p-2.5 rounded-[14px] text-foreground/60 hover:text-foreground hover:bg-muted/80 transition-all active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary/20"
        >
          <ChevronRight className="w-[22px] h-[22px]" />
        </button>
      </div>
    </div>
  )
}
