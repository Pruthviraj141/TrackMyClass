import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"

interface TrendDataPoint {
  name: string
  value: number
}

export function AttendanceTrend({ data }: { data: TrendDataPoint[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="px-6 py-2">
        <div className="bg-card rounded-[24px] p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.1)] border-none text-center">
          <p className="text-sm font-medium text-foreground/50">Not enough attendance data for a trend yet</p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-6 py-3">
      <div className="bg-card rounded-[24px] p-5 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.15)] border-none">
        <h3 className="text-[15px] font-semibold text-foreground mb-4">Attendance Trend</h3>
        
        <div className="h-[140px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                </linearGradient>
              </defs>
              {/* Using strokeDasharray to create dashed lines, avoiding solid borders */}
              <YAxis 
                hide 
                domain={['dataMin - 10', 'dataMax + 10']} 
              />
              <XAxis 
                dataKey="name" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 11, fill: 'hsl(var(--foreground))', opacity: 0.5 }} 
                dy={10}
              />
              <Tooltip 
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
                itemStyle={{ color: 'hsl(var(--foreground))', fontWeight: 'bold' }}
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Attendance']}
                labelStyle={{ color: 'hsl(var(--foreground))', opacity: 0.7, fontSize: 12, marginBottom: '4px' }}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="hsl(var(--primary))" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorValue)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
