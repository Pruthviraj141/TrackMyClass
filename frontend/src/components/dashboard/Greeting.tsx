import { useEffect, useState } from "react"

export function Greeting({ name }: { name?: string }) {
  const [dateStr, setDateStr] = useState("")

  useEffect(() => {
    const d = new Date()
    setDateStr(
      d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })
    )
  }, [])

  if (!name) {
    return (
      <div className="px-6 py-4 space-y-2 animate-pulse">
        <div className="h-8 bg-muted rounded w-3/4 max-w-[280px]"></div>
        <div className="h-4 bg-muted rounded w-1/2 max-w-[180px]"></div>
      </div>
    )
  }

  return (
    <div className="px-5 py-4 pt-6">
      <p className="text-foreground/50 text-[12px] uppercase tracking-[0.08em] font-bold mb-1.5">{dateStr}</p>
      <h1 className="text-[26px] font-bold tracking-tight leading-tight text-foreground">
        Good morning, {name?.split(' ')[0]} <span className="inline-block animate-wave transform-origin-bottom-right">👋</span>
      </h1>
    </div>
  )
}
