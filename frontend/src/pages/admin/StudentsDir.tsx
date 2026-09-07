import { useState, useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { Search, Plus, Wand2, ChevronRight, CheckCircle2 } from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

interface StudentDirectoryItem {
  student_id: string
  name: string
  roll_number: string
  class_name: string
  attendance_pct: number
  status: "Active" | "Inactive"
}

export default function StudentsDir() {
  const navigate = useNavigate()
  const { collegeCode } = useParams<{ collegeCode: string }>()
  
  const [search, setSearch] = useState("")
  const [activeFilter, setActiveFilter] = useState("All")
  
  const filters = ["All", "Active", "Class", "Attendance", "Status"]

  const { data: students, isLoading, isError } = useQuery<StudentDirectoryItem[]>({
    queryKey: ["admin_directory"],
    queryFn: async () => {
      const res = await api.get("/admin/directory")
      return res.data
    },
    staleTime: 5000
  })

  const filteredStudents = useMemo(() => {
    if (!students) return []
    let list = students
    
    if (activeFilter === "Active") {
      list = list.filter(s => s.status === "Active")
    }
    
    if (search.trim()) {
      const query = search.toLowerCase()
      list = list.filter(s => 
        s.name.toLowerCase().includes(query) || 
        s.roll_number.toLowerCase().includes(query)
      )
    }
    
    return list
  }, [students, search, activeFilter])

  const totals = useMemo(() => {
    if (!students) return { total: 0, active: 0, inactive: 0, avgAttendance: 0 }
    
    const active = students.filter(s => s.status === "Active").length
    const inactive = students.length - active
    const sum = students.reduce((acc, curr) => acc + curr.attendance_pct, 0)
    const avgAttendance = students.length > 0 ? Math.round(sum / students.length) : 0
    
    return {
      total: students.length,
      active,
      inactive,
      avgAttendance
    }
  }, [students])

  // Get Initials for Avatar
  const getInitials = (name: string) => {
    return name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase()
  }

  if (isError) {
    return (
      <div className="flex h-[50vh] flex-col items-center justify-center p-4 text-center">
        <p className="text-destructive font-semibold text-lg mb-2">Couldn't load students</p>
        <p className="text-muted-foreground mb-4">Something went wrong while loading the directory.</p>
        <button 
          onClick={() => window.location.reload()}
          className="text-primary font-medium hover:underline px-4 py-2"
        >
          Try again
        </button>
      </div>
    )
  }

  return (
    <div className="w-full flex flex-col font-sans relative pb-24 max-w-4xl mx-auto select-none animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header */}
      <header className="flex items-center justify-between py-6 sticky top-0 bg-background/80 backdrop-blur-3xl z-20 mb-2">
        <div className="flex flex-col">
           <h1 className="text-[28px] font-bold tracking-tight text-foreground leading-none mb-1">Students</h1>
           <span className="text-[15px] text-muted-foreground font-medium">{totals.total} enrolled</span>
        </div>
        
        <div className="flex items-center gap-4 text-foreground/80">
          <button className="hover:text-foreground transition-colors"><Plus className="w-5 h-5" /></button>
          <button className="hover:text-foreground transition-colors"><Search className="w-5 h-5" /></button>
          <button className="hover:text-foreground transition-colors"><Wand2 className="w-5 h-5" /></button>
        </div>
      </header>

      <div className="px-5">
        
        {/* Search */}
        <div className="relative mt-2 mb-4">
           <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground/60" />
           <Input 
             placeholder="Search students..." 
             className="pl-10 bg-white dark:bg-secondary/40 border-border/40 rounded-[14px] h-[48px] text-[16px] shadow-sm"
             value={search}
             onChange={(e) => setSearch(e.target.value)}
           />
        </div>
        
        {/* Filters List */}
        <div className="flex items-center gap-3 overflow-x-auto pb-4 scrollbar-hide -mx-5 px-5">
          {filters.map((filter) => (
             <button 
               key={filter}
               onClick={() => setActiveFilter(filter)}
               className={cn(
                 "whitespace-nowrap px-4 py-[6px] rounded-full text-[14px] font-semibold transition-all shadow-sm border",
                 activeFilter === filter 
                   ? "bg-indigo-100/50 text-indigo-700 border-indigo-200 dark:bg-indigo-900/30 dark:text-indigo-300 dark:border-indigo-800/50" 
                   : "bg-white text-muted-foreground border-border/40 hover:bg-slate-100 dark:bg-secondary/40 dark:hover:bg-secondary/60"
               )}
             >
                {filter}
             </button>
          ))}
        </div>

        {/* Summary Strip */}
        <div className="flex items-center justify-between mt-2 mb-4">
          <div>
            <h2 className="text-[17px] font-bold text-foreground leading-tight">{filteredStudents.length} Students</h2>
            <p className="text-[13px] text-muted-foreground font-medium mt-0.5">{totals.active} Active • {totals.inactive} Inactive</p>
          </div>
          <div className="text-right">
            <h2 className="text-[15px] font-bold text-foreground leading-tight">Average</h2>
            <p className="text-[13px] text-muted-foreground font-medium mt-0.5">attendance {totals.avgAttendance}%</p>
          </div>
        </div>
        
        {/* Roster List */}
        <div className="flex flex-col gap-3">
          {isLoading ? (
             Array.from({ length: 6 }).map((_, i) => (
               <div key={i} className="bg-white dark:bg-secondary/20 rounded-[20px] p-4 flex items-center shadow-sm animate-pulse">
                  <div className="w-[52px] h-[52px] rounded-full bg-slate-200 dark:bg-secondary mr-4" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-slate-200 dark:bg-secondary rounded w-1/3" />
                    <div className="h-3 bg-slate-200 dark:bg-secondary rounded w-1/2" />
                  </div>
               </div>
             ))
          ) : filteredStudents.length === 0 ? (
             <div className="py-16 text-center">
                <p className="text-[16px] font-bold text-foreground mb-1">No students found</p>
                <p className="text-[14px] text-muted-foreground">Try a different name, roll number, or filter.</p>
                <button 
                  onClick={() => { setSearch(""); setActiveFilter("All"); }}
                  className="mt-4 px-4 py-2 bg-secondary text-secondary-foreground rounded-full text-sm font-semibold"
                >
                  Clear search
                </button>
             </div>
          ) : (
            filteredStudents.map((student) => (
              <div 
                key={student.student_id} 
                className="bg-white dark:bg-secondary/20 rounded-[20px] p-4 flex items-center justify-between shadow-sm border border-slate-100 dark:border-border/10 cursor-pointer active:scale-[0.98] transition-transform"
                onClick={() => toast.info("Student details view is under development")}
              >
                 <div className="flex items-center gap-4 cursor-pointer">
                    {/* Avatar Bubble */}
                    <div className="relative w-[52px] h-[52px] flex items-center justify-center rounded-full bg-slate-100 text-slate-500 font-bold text-lg dark:bg-secondary dark:text-secondary-foreground flex-shrink-0">
                      {getInitials(student.name)}
                      
                      {/* Checkmark overlay */}
                      <div className="absolute right-[-4px] bottom-[-2px] w-5 h-5 bg-white dark:bg-background rounded-full flex items-center justify-center">
                        <CheckCircle2 className="w-[18px] h-[18px] text-green-500" fill="white" />
                      </div>
                    </div>
                    
                    {/* Info */}
                    <div className="flex flex-col justify-center translate-y-[-2px]">
                      <h3 className="text-[16px] font-bold text-foreground tracking-tight">{student.name}</h3>
                      <p className="text-[14px] font-medium text-muted-foreground mt-0.5">Roll {student.roll_number} • {student.class_name}</p>
                    </div>
                 </div>
                 
                 {/* Stats */}
                 <div className="flex items-center gap-3">
                   <div className="flex flex-col items-end text-right translate-y-[-2px]">
                      {student.status === "Active" ? (
                        <div className="flex items-center gap-1.5">
                          <div className="w-2 h-2 rounded-full bg-green-500"></div>
                          <span className="text-[14px] font-bold text-green-600 dark:text-green-500">{student.attendance_pct}%</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5">
                          <span className="text-[14px] font-semibold text-muted-foreground">Inactive</span>
                        </div>
                      )}
                      <span className="text-[13px] text-muted-foreground font-medium mt-0.5">attendance</span>
                   </div>
                   
                   <ChevronRight className="w-5 h-5 text-muted-foreground/40" />
                 </div>
                 
              </div>
            ))
          )}
        </div>
      </div>
      
      <div className="fixed bottom-[100px] right-0 left-0 flex justify-center pointer-events-none md:justify-end md:right-10 md:bottom-10 lg:max-w-4xl lg:mx-auto">
         <button 
           onClick={() => navigate(`/${collegeCode}/admin/students/add`)}
           className="pointer-events-auto bg-primary hover:bg-primary/95 text-primary-foreground shadow-lg shadow-primary/20 flex items-center gap-2 px-6 py-4 rounded-full transition-transform active:scale-95"
         >
            <Plus className="w-5 h-5" />
            <span className="font-semibold tracking-tight text-[16px]">Add Student</span>
         </button>
      </div>

    </div>
  )
}
