import { Card } from "@/components/ui/card"
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts"

interface TrendData {
  date: string
  percentage: number
}

interface AttendanceTrendProps {
  data: TrendData[]
  isLoading?: boolean
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-background/95 backdrop-blur border border-border/50 p-2 rounded-lg shadow-lg text-xs">
        <p className="font-semibold">{label}</p>
        <p className="text-primary font-mono">{payload[0].value}% attendance</p>
      </div>
    )
  }
  return null
}

export function AttendanceTrend({ data, isLoading }: AttendanceTrendProps) {
  if (isLoading) {
    return (
      <Card className="p-5 border-border/40 shadow-sm bg-card h-full animate-pulse">
        <div className="h-4 w-32 bg-muted/50 rounded mb-6" />
        <div className="h-[200px] bg-muted/20 rounded" />
      </Card>
    )
  }

  return (
    <Card className="p-5 border-border/40 shadow-sm bg-card h-full flex flex-col gap-4">
      <div>
        <h3 className="font-semibold text-[15px] leading-tight flex items-center justify-between">
          Attendance Trend
          {data.length > 0 && <span className="text-[10px] bg-primary text-primary-foreground px-2 py-0.5 rounded-full">{data[data.length - 1].percentage}% today</span>}
        </h3>
        <p className="text-[13px] text-foreground/50">As last 7 days, average attendance</p>
      </div>

      <div className="flex-1 w-full min-h-[200px] -ml-4">
        {data.length === 0 ? (
          <div className="flex items-center justify-center h-full text-foreground/40 text-[13px] italic">
            Attendance trends will appear once classes are recorded.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPct" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" className="opacity-10" />
              <XAxis 
                dataKey="date" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 10, fill: "currentColor" }} 
                className="opacity-50"
              />
              <YAxis 
                domain={[0, 100]} 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 10, fill: "currentColor" }}
                className="opacity-50"
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area 
                type="monotone" 
                dataKey="percentage" 
                stroke="#4f46e5" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorPct)" 
                activeDot={{ r: 4, fill: "#4f46e5" }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  )
}
