import { Card } from "@/components/ui/card"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"

interface AttendanceDistributionProps {
  present: number
  absent: number
  late: number
  isLoading?: boolean
}

export function AttendanceDistribution({ present, absent, late, isLoading }: AttendanceDistributionProps) {
  if (isLoading) {
    return (
      <Card className="p-5 border-border/40 shadow-sm bg-card h-full animate-pulse">
        <div className="h-4 w-32 bg-muted/50 rounded mb-6" />
        <div className="mx-auto w-32 h-32 rounded-full border-[10px] border-muted/30" />
      </Card>
    )
  }

  const data = [
    { name: 'Present', value: present, color: '#4f46e5' }, // Indigo
    { name: 'Absent', value: absent, color: '#f43f5e' }, // Rose
    { name: 'Late', value: late, color: '#f59e0b' }, // Amber
  ].filter(d => d.value > 0)
  
  const total = present + absent + late
  const avg = total > 0 ? (present / total) * 100 : 0

  return (
    <Card className="p-5 border-border/40 shadow-sm bg-card h-full flex flex-col gap-4 relative">
      <div>
        <h3 className="font-semibold text-[15px] leading-tight">Attendance Distribution</h3>
        <p className="text-[13px] text-foreground/50">actual values</p>
      </div>

      <div className="flex-1 min-h-[160px] relative">
        {total === 0 ? (
           <div className="flex items-center justify-center h-full text-foreground/40 text-[13px] italic">
             No distribution data.
           </div>
        ) : (
          <>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius="65%"
                  outerRadius="90%"
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--background))', border: '1px solid hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                />
              </PieChart>
            </ResponsiveContainer>
            {/* Center Label */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <span className="text-xl font-bold font-mono tracking-tight">{avg.toFixed(1)}%</span>
            </div>
          </>
        )}
      </div>

      {total > 0 && (
         <div className="flex items-center justify-center gap-4 text-[12px] font-medium text-foreground/70">
           <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-indigo-600" /> Present</div>
           <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Absent</div>
           <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Late</div>
         </div>
      )}
    </Card>
  )
}
