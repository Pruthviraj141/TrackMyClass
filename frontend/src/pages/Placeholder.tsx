import { CalendarClock } from "lucide-react"

export default function PlaceholderPage({ title = "Coming Soon" }: { title?: string }) {
  return (
    <div className="w-full min-h-screen bg-background relative flex flex-col items-center justify-center max-w-md md:max-w-2xl lg:max-w-3xl mx-auto sm:border-x border-border/40 px-6 text-center">
      <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-6">
        <CalendarClock className="w-10 h-10 text-primary" />
      </div>
      <h1 className="text-2xl font-bold tracking-tight text-foreground mb-2">{title}</h1>
      <p className="text-muted-foreground">
        This section is currently under development. Please check back in a future update!
      </p>
    </div>
  )
}
