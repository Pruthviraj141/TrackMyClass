import { useMutation, useQueryClient } from "@tanstack/react-query"
import { AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { api } from "@/lib/api"
import { toast } from "sonner"
import { motion, AnimatePresence } from "framer-motion"

interface Student {
  student_id: string
  name: string
  roll_number: string
  status: "present" | "absent" | "late"
  time?: string
  confidence?: number
}

interface StudentRosterProps {
  students: Student[]
  date: string
  collegeCode: string
  subjectName: string
}

export function StudentRoster({ students, date, collegeCode, subjectName }: StudentRosterProps) {
  const queryClient = useQueryClient()

  const { mutate: updateStatus } = useMutation({
    mutationFn: async ({ student_id, newStatus }: { student_id: string, newStatus: string }) => {
      await api.post('/attendance/manual-update', {
        student_id,
        date,
        status: newStatus,
        subject_name: subjectName
      })
    },
    onMutate: async ({ student_id, newStatus }) => {
      await queryClient.cancelQueries({ queryKey: ['teacher-attendance', collegeCode, date] })
      const previousData = queryClient.getQueryData(['teacher-attendance', collegeCode, date])

      queryClient.setQueryData(['teacher-attendance', collegeCode, date], (old: any) => {
        if (!old) return old
        
        const isCurrentlyPresent = old.present_list?.some((s: any) => s.student_id === student_id)
        const isCurrentlyLate = old.late_list?.some((s: any) => s.student_id === student_id)
        let targetStudent = null
        let newPresentList = [...(old.present_list || [])]
        let newLateList = [...(old.late_list || [])]
        let newAbsentList = [...(old.absent_list || [])]
        
        if (isCurrentlyPresent) {
           targetStudent = newPresentList.find(s => s.student_id === student_id)
           newPresentList = newPresentList.filter(s => s.student_id !== student_id)
        } else if (isCurrentlyLate) {
           targetStudent = newLateList.find(s => s.student_id === student_id)
           newLateList = newLateList.filter(s => s.student_id !== student_id)
        } else {
           targetStudent = newAbsentList.find(s => s.student_id === student_id)
           newAbsentList = newAbsentList.filter(s => s.student_id !== student_id)
        }

        if (targetStudent) {
            if (newStatus === "present") {
                newPresentList.push({ ...targetStudent, time: "Manual" })
            } else if (newStatus === "late") {
                newLateList.push({ ...targetStudent, time: "LATE" })
            } else {
                newAbsentList.push(targetStudent)
            }
            
            old.total_present = newPresentList.length
            old.total_late = newLateList.length
            
            if (old.total_registered > 0) {
               old.attendance_pct = Number(((old.total_present / old.total_registered) * 100).toFixed(1))
            }
        }
        
        return {
          ...old,
          present_list: newPresentList,
          late_list: newLateList,
          absent_list: newAbsentList
        }
      })

      return { previousData }
    },
    onError: (_, __, context) => {
      toast.error("Failed to update attendance")
      queryClient.setQueryData(['teacher-attendance', collegeCode, date], context?.previousData)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['teacher-attendance', collegeCode, date] })
    }
  })

  // Group by alphabetical initial for sectioning (optional, but good for flat lists)
  // For now, just flat list
  if (students.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground border rounded-[20px] bg-card/30">
        <AlertCircle className="w-10 h-10 mb-3 opacity-40 text-muted-foreground" />
        <p className="font-semibold text-[15px] text-foreground/80">No students found</p>
        <p className="text-sm opacity-60">Try adjusting your active filters.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col bg-card rounded-[24px] shadow-sm border border-border/50 overflow-hidden divide-y divide-border/40">
      <AnimatePresence>
        {students.map((student) => {
          // Generate a stable color based on name for the avatar
          const charCode = student.name.charCodeAt(0)
          const colors = ['bg-blue-100 text-blue-700', 'bg-emerald-100 text-emerald-700', 'bg-amber-100 text-amber-700', 'bg-purple-100 text-purple-700', 'bg-rose-100 text-rose-700']
          const avatarColor = colors[charCode % colors.length]

          return (
            <motion.div
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              key={student.student_id}
              className={cn(
                "flex items-center justify-between p-4 transition-colors relative",
                student.status === "present" ? "bg-primary/5" : "bg-transparent"
              )}
            >
              {/* Left: Avatar & Identity */}
              <div className="flex items-center gap-3.5 flex-1 min-w-0 pr-4">
                 <div className={cn("w-[42px] h-[42px] rounded-full flex items-center justify-center font-bold text-[16px] shrink-0", avatarColor)}>
                   {student.name.charAt(0)}
                 </div>
                 <div className="flex flex-col min-w-0">
                    <span className="font-semibold text-[15px] text-foreground truncate tracking-tight">{student.name}</span>
                    <span className="text-[13px] text-muted-foreground font-medium uppercase tracking-wider truncate">{student.roll_number}</span>
                 </div>
              </div>

              {/* Right: Action Pills */}
              <div className="flex items-center bg-muted/60 p-[4px] rounded-full shrink-0 gap-[1px]">
                 <button
                   onClick={() => student.status !== "present" && updateStatus({ student_id: student.student_id, newStatus: "present" })}
                   className={cn(
                     "w-8 h-8 rounded-full text-[13px] font-bold transition-all flex items-center justify-center",
                     student.status === "present" 
                       ? "bg-emerald-500 text-white shadow-sm" 
                       : "text-muted-foreground hover:bg-black/5 dark:hover:bg-white/10"
                   )}
                 >
                   P
                 </button>
                 <button
                   onClick={() => student.status !== "absent" && updateStatus({ student_id: student.student_id, newStatus: "absent" })}
                   className={cn(
                     "w-8 h-8 rounded-full text-[13px] font-bold transition-all flex items-center justify-center",
                     student.status === "absent" 
                       ? "bg-rose-500 text-white shadow-sm" 
                       : "text-muted-foreground hover:bg-black/5 dark:hover:bg-white/10"
                   )}
                 >
                   A
                 </button>
                 <button
                   onClick={() => student.status !== "late" && updateStatus({ student_id: student.student_id, newStatus: "late" })}
                   className={cn(
                     "w-8 h-8 rounded-full text-[13px] font-bold transition-all flex items-center justify-center",
                     student.status === "late" 
                       ? "bg-amber-500 text-white shadow-sm" 
                       : "text-muted-foreground hover:bg-black/5 dark:hover:bg-white/10"
                   )}
                 >
                   L
                 </button>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
