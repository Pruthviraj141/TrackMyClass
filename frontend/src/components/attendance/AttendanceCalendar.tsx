interface AttendanceCalendarProps {
  currentDate: Date
  selectedDate: Date
  onSelectDate: (date: Date) => void
  onChangeMonth: (increment: number) => void
  attendanceData: Record<string, "Present" | "Absent" | "Late" | "None"> // mapping "YYYY-MM-DD" to status
}

export function AttendanceCalendar({ currentDate, selectedDate, onSelectDate, onChangeMonth, attendanceData }: AttendanceCalendarProps) {
  const daysOfWeek = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
  
  // Calculate days for the calendar grid
  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()
  
  const firstDayOfMonth = new Date(year, month, 1)
  const lastDayOfMonth = new Date(year, month + 1, 0)
  
  // JavaScript getDay() returns 0 for Sunday. We want Monday = 0.
  let startDay = firstDayOfMonth.getDay() - 1
  if (startDay === -1) startDay = 6 // Sunday
  
  const daysInMonth = lastDayOfMonth.getDate()
  
  const calendarDays = []
  
  // Previous month padding
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    calendarDays.push({
      date: new Date(year, month - 1, prevMonthLastDay - i),
      isCurrentMonth: false
    })
  }
  
  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    calendarDays.push({
      date: new Date(year, month, i),
      isCurrentMonth: true
    })
  }
  
  // Next month padding (to complete the grid)
  const totalSlots = Math.ceil(calendarDays.length / 7) * 7
  const remainingSlots = totalSlots - calendarDays.length
  for (let i = 1; i <= remainingSlots; i++) {
    calendarDays.push({
      date: new Date(year, month + 1, i),
      isCurrentMonth: false
    })
  }

  // Format date to "YYYY-MM-DD" matching local timezone exactly
  const formatDate = (date: Date) => {
    const d = new Date(date)
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
    return d.toISOString().split('T')[0]
  }

  const selectedDateStr = formatDate(selectedDate)
  
  const monthName = new Intl.DateTimeFormat('en-US', { month: 'long' }).format(currentDate)

  return (
    <div className="px-5 py-4">
      <div className="bg-card dark:bg-card/40 rounded-[28px] p-5 shadow-[0_4px_24px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_24px_rgb(0,0,0,0.1)] border border-transparent dark:border-border/30">
        
        {/* Month Header */}
        <div className="flex items-center justify-between mb-6">
          <button onClick={() => onChangeMonth(-1)} className="p-2 -ml-2 active:scale-95 transition-transform">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-foreground/40"><path d="m15 18-6-6 6-6"/></svg>
          </button>
          <span className="text-[17px] font-bold tracking-tight text-foreground">{monthName} {year}</span>
          <button 
             onClick={() => onChangeMonth(1)} 
             className="p-2 -mr-2 active:scale-95 transition-transform"
             disabled={currentDate.getMonth() >= new Date().getMonth() && currentDate.getFullYear() >= new Date().getFullYear()}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={`text-foreground/40 ${currentDate.getMonth() >= new Date().getMonth() ? 'opacity-30' : ''}`}><path d="m9 18 6-6-6-6"/></svg>
          </button>
        </div>

        {/* Days Header */}
        <div className="grid grid-cols-7 mb-4 text-center">
          {daysOfWeek.map(day => (
            <div key={day} className="text-[11px] font-medium text-foreground/40 capitalize tracking-wide">
              {day}
            </div>
          ))}
        </div>
        
        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-y-2 gap-x-2">
          {calendarDays.map((dayObj, i) => {
            const dateStr = formatDate(dayObj.date)
            const status = attendanceData[dateStr] || "None"
            const isSelected = dateStr === selectedDateStr
            
            let bgClass = "bg-transparent text-foreground/20" // Not in current month
            let dotColor = "opacity-0"
            
            if (dayObj.isCurrentMonth) {
              if (isSelected) {
                 bgClass = "bg-indigo-500 text-white shadow-md shadow-indigo-500/20"
                 dotColor = "bg-white/70" // Dot is visible inside blue box
              } else if (status === "Present") {
                 bgClass = "bg-green-500/10 text-foreground dark:bg-green-500/10"
                 dotColor = "bg-green-500"
              } else if (status === "Absent") {
                 bgClass = "bg-destructive/10 text-foreground"
                 dotColor = "bg-destructive"
              } else if (status === "Late") {
                 bgClass = "bg-amber-500/10 text-foreground"
                 dotColor = "bg-amber-500"
              } else {
                 bgClass = "bg-muted/50 text-foreground/80 dark:bg-muted/20"
              }
            }

            return (
              <button
                key={i}
                onClick={() => onSelectDate(dayObj.date)}
                className={`
                  aspect-square rounded-[14px] flex flex-col items-center justify-center transition-all focus:outline-none relative pt-1
                  ${bgClass} 
                  ${!dayObj.isCurrentMonth ? 'cursor-default pointer-events-none' : 'active:scale-90 cursor-pointer'}
                `}
              >
                <span className="text-[15px] font-semibold leading-none">{dayObj.date.getDate()}</span>
                <div className={`w-1 h-1 rounded-full mt-1 ${dotColor}`} />
              </button>
            )
          })}
        </div>
        
      </div>
    </div>
  )
}
