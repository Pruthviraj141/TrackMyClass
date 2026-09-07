import { Card } from "@/components/ui/card"

export function AttendanceInsight({ title, description }: { title: string, description: string }) {
  return (
    <div className="px-6 py-2 mb-6">
      <Card className="rounded-[16px] border-none shadow-[0_8px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_8px_20px_rgb(0,0,0,0.15)] bg-card p-5">
        <h3 className="text-[15px] font-semibold text-foreground leading-tight mb-1">{title}</h3>
        <p className="text-[13px] text-foreground/60 leading-relaxed font-medium">
          {description}
        </p>
      </Card>
    </div>
  )
}
