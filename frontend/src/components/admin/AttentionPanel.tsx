import { Card } from "@/components/ui/card"
import { useNavigate } from "react-router-dom"

export interface AttentionItem {
  id: string
  message: string
  route: string
}

interface AttentionPanelProps {
  items: AttentionItem[]
}

export function AttentionPanel({ items }: AttentionPanelProps) {
  const navigate = useNavigate()

  return (
    <Card className="p-5 shadow-sm bg-amber-500/5 border border-amber-500/20 h-full flex flex-col gap-4">
      <div>
        <h3 className="font-semibold text-[15px] leading-tight text-amber-600 dark:text-amber-500">Attention Panel</h3>
        <p className="text-[13px] text-amber-600/70 dark:text-amber-500/80">Needs attention</p>
      </div>
      
      <div className="flex-1 space-y-3">
        {items.length === 0 ? (
          <div className="text-[13px] text-amber-600/60 dark:text-amber-500/60 font-medium">
            All systems nominal. No attention required.
          </div>
        ) : (
          items.map(item => (
            <div key={item.id} className="flex items-center justify-between gap-2 border-b border-amber-500/10 pb-2 last:border-0">
              <span className="text-[13px] font-medium text-amber-700 dark:text-amber-400 leading-tight">
                {item.message}
              </span>
              <button 
                onClick={() => navigate(item.route)}
                className="px-3 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-400 rounded-md text-[11px] font-bold uppercase transition-colors whitespace-nowrap"
              >
                Review
              </button>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
