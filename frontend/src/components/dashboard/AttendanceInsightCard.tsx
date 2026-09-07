import { Card } from "@/components/ui/card"

export function AttendanceInsightCard({ message }: { message?: string }) {
  if (!message) return null

  return (
    <div className="px-6 py-2">
      <Card className="rounded-[16px] border-none shadow-[0_8px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_8px_20px_rgb(0,0,0,0.15)] bg-card p-4">
        <p className="text-sm font-medium leading-relaxed text-foreground/90">
          {message}
        </p>
      </Card>
    </div>
  )
}
