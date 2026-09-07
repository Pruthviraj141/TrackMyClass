const currentDate = new Date(2026, 8, 1); // Sept 1 2026
const year = currentDate.getFullYear()
const month = currentDate.getMonth()
const firstDayOfMonth = new Date(year, month, 1)
const lastDayOfMonth = new Date(year, month + 1, 0)
let startDay = firstDayOfMonth.getDay() - 1
if (startDay === -1) startDay = 6 // Sunday
const daysInMonth = lastDayOfMonth.getDate()

console.log("startDay:", startDay)
console.log("daysInMonth:", daysInMonth)

const formatDate = (date) => {
    const d = new Date(date)
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
    return d.toISOString().split('T')[0]
}

const calendarDays = []
const prevMonthLastDay = new Date(year, month, 0).getDate()
for (let i = startDay - 1; i >= 0; i--) {
  calendarDays.push({
    date: new Date(year, month - 1, prevMonthLastDay - i),
    isCurrentMonth: false
  })
}
for (let i = 1; i <= daysInMonth; i++) {
  calendarDays.push({
    date: new Date(year, month, i),
    isCurrentMonth: true
  })
}
const totalSlots = Math.ceil(calendarDays.length / 7) * 7
const remainingSlots = totalSlots - calendarDays.length
for (let i = 1; i <= remainingSlots; i++) {
  calendarDays.push({
    date: new Date(year, month + 1, i),
    isCurrentMonth: false
  })
}

// Print Calendar
let row = []
for (let i=0; i<calendarDays.length; i++) {
   row.push(calendarDays[i].date.getDate())
   if(row.length === 7) {
       console.log(row.join('\t'))
       row = []
   }
}
