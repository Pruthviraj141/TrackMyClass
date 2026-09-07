import { useState, useMemo, useEffect } from "react"
import { useParams } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { format, subDays, addDays } from "date-fns"
import { Calendar, ChevronLeft, ChevronRight, Search } from "lucide-react"
import { api } from "@/lib/api"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { AttendanceSummary } from "@/components/teacher/attendance/AttendanceSummary"
import { StudentRoster } from "@/components/teacher/attendance/StudentRoster"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function TeacherAttendance() {
  const { collegeCode } = useParams<{ collegeCode: string }>()
  const queryClient = useQueryClient()
  
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [selectedSubject, setSelectedSubject] = useState<string>("")
  const [searchQuery, setSearchQuery] = useState("")
  const [filterMode, setFilterMode] = useState<"all" | "present" | "absent">("all")
  
  const dateStr = format(selectedDate, "yyyy-MM-dd")
  
  // 1. Fetch Data
  const { data, isLoading, error } = useQuery({
    queryKey: ['teacher-attendance', collegeCode, dateStr, selectedSubject],
    queryFn: async () => {
      // Teacher leverages the same historical endpoint but locked to current institution physically via token
      const res = await api.get(`/admin/historical-data?date=${dateStr}&subject=${selectedSubject}`)
      return res.data
    },
    refetchInterval: 30000 // Poll every 30s in case live session is running
  })

  // 1.5 Auto-Select Subject
  useEffect(() => {
    if (data?.available_subjects) {
      const valid = data.available_subjects.filter((s: string) => s !== "All" && s !== "None")
      if (valid.length > 0 && (!selectedSubject || selectedSubject === "All")) {
        setSelectedSubject(valid[0])
      }
    }
  }, [data?.available_subjects, selectedSubject])

  // 2. Data processing — deduplicate by student_id to prevent duplicate React keys
  const allStudents = useMemo(() => {
    if (!data) return []
    // Deduplicate present_list by student_id (keep first occurrence)
    const seenIds = new Set<string>()
    const present = (data.present_list || []).filter((s: any) => {
      if (seenIds.has(s.student_id)) return false
      seenIds.add(s.student_id)
      return true
    }).map((s: any) => ({ ...s, status: 'present' }))
    const late = (data.late_list || []).filter((s: any) => {
      if (seenIds.has(s.student_id)) return false
      seenIds.add(s.student_id)
      return true
    }).map((s: any) => ({ ...s, status: 'late' }))
    const absent = (data.absent_list || []).filter((s: any) => !seenIds.has(s.student_id)).map((s: any) => ({ ...s, status: 'absent' }))
    
    // Sort combined by Roll Number
    return [...present, ...late, ...absent].sort((a: any, b: any) => {
      const rA = a.roll_number || ""
      const rB = b.roll_number || ""
      return rA.localeCompare(rB)
    })
  }, [data])

  const filteredStudents = useMemo(() => {
    return allStudents.filter((s: any) => {
      const matchQuery = s.name?.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         s.roll_number?.toLowerCase().includes(searchQuery.toLowerCase())
      
      const matchFilter = filterMode === "all" ? true : s.status === filterMode
      
      return matchQuery && matchFilter
    })
  }, [allStudents, searchQuery, filterMode])

  // 3. Stats for Summary
  const stats = {
    total: data?.total_registered || 0,
    present: data?.total_present || 0,
    late: data?.total_late || 0,
    absent: data?.absent_list?.length || 0,
    percentage: data?.attendance_pct || 0
  }

  // 4. Loading & Error
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] text-destructive">
        <p>Failed to load attendance data.</p>
        <Button variant="outline" className="mt-4" onClick={() => queryClient.invalidateQueries({ queryKey: ['teacher-attendance'] })}>
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-32 md:pb-8 pt-4 px-4 sm:px-6 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-4xl mx-auto">
      
      {/* HEADER & DATE */}
      <div className="flex flex-col gap-2">
        <h1 className="text-[28px] font-bold tracking-tight text-foreground leading-tight">Attendance</h1>
        <p className="text-[15px] text-muted-foreground font-medium mb-2">Mark and manage student attendance</p>
        
        <div className="flex items-center justify-between py-1 mt-1">
          <Button variant="ghost" size="icon" className="hover:bg-muted text-muted-foreground rounded-full w-9 h-9" onClick={() => setSelectedDate(subDays(selectedDate, 1))}>
            <ChevronLeft className="h-5 w-5" strokeWidth={2.5} />
          </Button>
          <div className="flex flex-col items-center">
            <span className="text-[15px] font-semibold text-foreground tracking-tight flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground mb-[2px]" strokeWidth={2.5} />
              {format(selectedDate, "EEE, MMM d, yyyy")}
            </span>
            {format(selectedDate, "yyyy-MM-dd") === format(new Date(), "yyyy-MM-dd") && (
              <span className="text-[10px] text-primary font-bold bg-primary/10 px-2.5 py-0.5 rounded-full uppercase tracking-wider mt-1">Today</span>
            )}
          </div>
          <Button variant="ghost" size="icon" className="hover:bg-muted text-muted-foreground rounded-full w-9 h-9" onClick={() => setSelectedDate(addDays(selectedDate, 1))} disabled={format(selectedDate, "yyyy-MM-dd") === format(new Date(), "yyyy-MM-dd")}>
            <ChevronRight className="h-5 w-5" strokeWidth={2.5} />
          </Button>
        </div>

        {/* SUBJECT FILTERS */}
        {data?.available_subjects?.filter((s: string) => s !== "All" && s !== "None").length > 0 ? (
          <div className="flex gap-2.5 overflow-x-auto pb-2 pt-2 scrollbar-none w-full px-1">
            {data.available_subjects.filter((s: string) => s !== "All" && s !== "None").map((sub: string) => {
              const isActive = selectedSubject === sub
              return (
                <Button 
                   key={sub}
                   variant="ghost"
                   onClick={() => setSelectedSubject(sub)}
                   className={`rounded-full shrink-0 whitespace-nowrap min-w-[75px] text-[14px] font-semibold px-4 py-1 h-auto transition-all ${
                     isActive 
                       ? "bg-primary text-primary-foreground shadow-sm" 
                       : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
                   }`}
                >
                  {sub}
                </Button>
              )
            })}
          </div>
        ) : (
          <div className="py-2 px-2 text-sm font-medium text-muted-foreground">
             No classes available
          </div>
        )}
      </div>

      {/* SUMMARY */}
      <AttendanceSummary stats={stats} />

      {/* ROSTER CONTROLS */}
      {/* ROSTER CONTROLS */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center mt-2 mb-1 px-1 sm:px-0">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" strokeWidth={2.5} />
          <Input 
            placeholder="Search by name or roll number..." 
            className="pl-11 bg-muted/50 border-none shadow-none h-[42px] rounded-full focus-visible:ring-1 focus-visible:bg-muted/80 transition-colors text-[15px]"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="flex gap-2">
          <Select value={filterMode} onValueChange={(val: any) => setFilterMode(val)}>
            <SelectTrigger className="w-[110px] bg-muted/50 border-none shadow-none h-[42px] rounded-full text-[14px] font-semibold text-foreground/80 focus:ring-1 focus-visible:ring-1">
              <SelectValue placeholder="Filter" />
            </SelectTrigger>
            <SelectContent className="rounded-2xl border-border/50 shadow-lg font-medium">
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="present">Present</SelectItem>
              <SelectItem value="absent">Absent</SelectItem>
              <SelectItem value="late">Late</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* ROSTER LIST */}
      <StudentRoster 
        students={filteredStudents} 
        date={dateStr}
        collegeCode={collegeCode!}
        subjectName={selectedSubject}
      />
    </div>
  )
}
