export function NextClassCard() {
  return (
    <div className="px-5 py-2">
      <div className="bg-card dark:bg-card/40 rounded-[28px] p-6 shadow-[0_4px_24px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_24px_rgb(0,0,0,0.1)] border border-transparent dark:border-border/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-[17px] font-bold tracking-tight text-foreground flex items-center gap-1.5">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
            Next Class
          </h3>
          <span className="text-[13px] font-medium text-foreground/40 hover:text-primary cursor-pointer transition-colors">View All</span>
        </div>
        <div className="bg-muted/30 dark:bg-muted/10 border border-dashed border-border/60 rounded-[20px] p-6 flex flex-col items-center justify-center text-center">
          <p className="text-[14px] font-semibold text-foreground/50">No upcoming classes</p>
          <p className="text-[12px] text-foreground/40 mt-1">Enjoy your free time!</p>
        </div>
      </div>
    </div>
  )
}
